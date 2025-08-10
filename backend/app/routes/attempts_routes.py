from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.assignment_test import AssignmentTest
from app.models.query import Query
from app.models.assignment import Assignment
from app.utils.auth import token_required
from bson import ObjectId
from datetime import datetime
import json, re, subprocess

attempts_bp = Blueprint("attempts", __name__, url_prefix="/assignments")

MAX_DOCS = 200
MAX_TIME_MS = 3000            # лимит для операций внутри Mongo
MONGOSH_TIMEOUT = 5           # секунд на выполнение mongosh
MAX_OUTPUT_BYTES = 2_000_000  # защитный лимит на размер вывода

# Разрешаем только чтение: find / aggregate (+ sort/limit цепочки)
ALLOWED_SHELL = re.compile(
    r"""^\s*db\.(?P<coll>[A-Za-z0-9_]+)\.(?P<op>find|aggregate)\s*\([\s\S]*?\)\s*(\.\s*(sort|limit)\s*\([\s\S]*?\)\s*)*;?\s*$""",
    re.IGNORECASE,
)

def normalize_value(v):
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, list):
        return [normalize_value(x) for x in v]
    if isinstance(v, dict):
        return {k: normalize_value(v[k]) for k in sorted(v)}
    return v

def normalize_docs(docs):
    return [normalize_value(doc) for doc in docs[:MAX_DOCS]]

def _run_mongosh(code: str, mongo_uri: str) -> tuple[int, str, str]:
    """
    Запускает mongosh, если выражение вернёт курсор — делает toArray(),
    печатает JSON через print(JSON.stringify(...)).
    """
    user_code = code.strip()
    if user_code.endswith(";"):
        user_code = user_code[:-1]

    script = f"""
try {{
  const __expr_result = (function() {{ return ({user_code}); }})();
  let __out;
  if (__expr_result && typeof __expr_result.toArray === 'function') {{
    __out = __expr_result.toArray();
  }} else {{
    __out = __expr_result;
  }}
  const __json = JSON.stringify(__out);
  if (__json.length > {MAX_OUTPUT_BYTES}) {{
    throw new Error("Result too large");
  }}
  print(__json);
}} catch (e) {{
  print(JSON.stringify({{__mongo_error: String(e.message || e)}}));
  quit(2);
}}
"""
    cmd = ["mongosh", mongo_uri, "--quiet", "--eval", script]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=MONGOSH_TIMEOUT
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

@attempts_bp.route("/<int:assignment_id>/attempts", methods=["POST"])
@token_required
def attempt_assignment(user_id, assignment_id):
    """
    Отправка решения в виде mongo shell (через mongosh)
    ---
    tags:
      - Attempts
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: assignment_id
        required: true
        type: integer
        description: ID задания
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [code]
          properties:
            code:
              type: string
              example: "db.orders.find({status: 'A'}).sort({_id: 1}).limit(5);"
              description: Mongo shell выражение (find/aggregate, опционально sort/limit)
    responses:
      200:
        description: Результат проверки
        schema:
          type: object
          properties:
            passed:
              type: boolean
              description: Все ли тесты прошли
            tests:
              type: array
              items:
                type: object
                properties:
                  test_id:
                    type: integer
                  description:
                    type: string
                  passed:
                    type: boolean
            result_sample:
              type: array
              description: Первые N документов результата (нормализованные)
      400:
        description: Ошибка исполнения mongo-запроса (оригинальный текст от MongoDB) или ошибка валидации входных данных
        schema:
          type: object
          properties:
            error:
              type: string
              example: "db.orders.find ... 'A'}).sor213123t is not a function"
      403:
        description: Запрещённая операция (не read-only)
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Only read queries allowed: db.<coll>.find(...) / aggregate(...) with optional sort/limit"
      404:
        description: Задание не найдено
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Assignment not found"
      500:
        description: Внутренняя ошибка (настройка MONGO_URI / отсутствие mongosh / неверный stdout)
        schema:
          type: object
          properties:
            error:
              type: string
      504:
        description: Таймаут выполнения mongosh
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Mongo shell timed out"
    """
    body = request.get_json(silent=True) or {}
    code = body.get("code", "")
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Body must be JSON with 'code' string"}), 400

    if not ALLOWED_SHELL.match(code):
        return jsonify({
            "error": "Only read queries allowed: db.<coll>.find(...) / aggregate(...) with optional sort/limit"
        }), 403

    if not Assignment.query.get(assignment_id):
        return jsonify({"error": "Assignment not found"}), 404

    mongo_uri = current_app.config.get("MONGO_URI")
    if not mongo_uri or "/" not in mongo_uri.strip("/"):
        return jsonify({"error": "MONGO_URI must include database name, e.g. mongodb://mongo:27017/mongo_train"}), 500

    started = datetime.utcnow()
    try:
        rc, out, err = _run_mongosh(code, mongo_uri)
    except subprocess.TimeoutExpired:
        q = Query(
            user_id=user_id,
            assignment_id=assignment_id,
            query_text=code,
            status="error",
            error_message="mongosh timed out"
        )
        db.session.add(q); db.session.commit()
        return jsonify({"error": "Mongo shell timed out"}), 504
    except FileNotFoundError:
        return jsonify({"error": "mongosh not found. Install mongosh in your container/image."}), 500

    exec_ms = int((datetime.utcnow() - started).total_seconds() * 1000)

    if rc != 0:
        msg = err or out
        try:
            parsed = json.loads(out)
            if isinstance(parsed, dict) and "__mongo_error" in parsed:
                msg = parsed["__mongo_error"]
        except Exception:
            pass

        q = Query(
            user_id=user_id,
            assignment_id=assignment_id,
            query_text=code,
            status="error",
            error_message=msg
        )
        db.session.add(q); db.session.commit()
        return jsonify({"error": msg}), 400

    try:
        data = json.loads(out) if out else []
        if isinstance(data, dict):
            docs = [data]
        elif isinstance(data, list):
            docs = data
        else:
            docs = [data]
    except Exception as e:
        q = Query(
            user_id=user_id,
            assignment_id=assignment_id,
            query_text=code,
            status="error",
            error_message=f"Invalid mongosh JSON output: {e}"
        )
        db.session.add(q); db.session.commit()
        return jsonify({"error": "Invalid mongosh JSON output"}), 500

    normalized = normalize_docs(docs)

    tests = AssignmentTest.query.filter_by(assignment_id=assignment_id).all()
    all_passed, test_results = True, []
    for t in tests:
        expected = t.expected_result
        if isinstance(expected, str):
            try:
                expected = json.loads(expected)
            except Exception:
                expected = {"_raw": expected}
        passed = (expected == normalized)
        all_passed &= passed
        test_results.append({
            "test_id": t.test_id,
            "description": t.test_description,
            "passed": passed
        })

    q = Query(
        user_id=user_id,
        assignment_id=assignment_id,
        query_text=code,
        status="ok" if all_passed else "failed",
        result=normalized,
        exec_ms=exec_ms,
        result_count=len(normalized),
    )
    db.session.add(q); db.session.commit()

    return jsonify({
        "passed": all_passed,
        "tests": test_results,
        "result_sample": normalized[:5]
    })
