from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.assignment_test import AssignmentTest
from app.models.query import Query
from app.models.assignment import Assignment
from app.utils.auth import token_required  # Оставляем проверку токена
from bson import ObjectId
from datetime import datetime
import json, re, subprocess
from sqlalchemy.exc import SQLAlchemyError, NoReferencedTableError, ProgrammingError


def _safe_rollback():
    """Rollback session if possible, swallow errors to avoid SAWarning when
    session state is not active.
    """
    try:
        # Only rollback if there is an active transaction; otherwise removing the session
        # is safer (rollback on non-active transaction emits SAWarning).
        try:
            in_tx = False
            if hasattr(db.session, 'in_transaction'):
                # SQLAlchemy 1.4+: in_transaction() returns a Transaction or None
                in_tx = bool(db.session.in_transaction())
            elif hasattr(db.session, 'get_transaction'):
                in_tx = bool(db.session.get_transaction())
        except Exception:
            in_tx = False

        if in_tx:
            db.session.rollback()
        else:
            try:
                db.session.remove()
            except Exception:
                pass
    except Exception:
        # best-effort cleanup
        try:
            db.session.remove()
        except Exception:
            pass

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
    """
    body = request.get_json(silent=True) or {}
    code = body.get("code", "")
    if not isinstance(code, str) or not code.strip():
        return jsonify({"error": "Body must be JSON with 'code' string"}), 400

    if not ALLOWED_SHELL.match(code):
        return jsonify({
            "error": "Only read queries allowed: db.<coll>.find(...) / aggregate(...) with optional sort/limit"
        }), 403

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    # Optional enforcement: assignment may require using a specific method (e.g. "find")
    # The config may be stored in assignment.schema_json as {"required_method": "find"}
    required_method = None
    try:
        conf = None
        if assignment.schema_json:
            if isinstance(assignment.schema_json, dict):
                conf = assignment.schema_json
            else:
                # sometimes stored as JSON string
                try:
                    conf = json.loads(assignment.schema_json)
                except Exception:
                    conf = None
        if conf and isinstance(conf, dict):
            required_method = conf.get("required_method")
    except Exception:
        required_method = None

    # Create an initial Query row ASAP so we have a persistent record of the submission
    q = None
    try:
        q = Query(
            user_id=user_id,
            assignment_id=assignment_id,
            query_text=code,
            status="running",
        )
        db.session.add(q)
        db.session.commit()
    except SQLAlchemyError:
        # if saving fails, continue without persistent q; we'll try to save later
        _safe_rollback()

    if required_method:
        # robust check: look for a dot + method name + opening parenthesis, allow spaces and case-insensitive
        try:
            meth_re = re.compile(rf"\.\s*{re.escape(required_method)}\s*\(", re.IGNORECASE)
        except re.error:
            meth_re = None

        if not meth_re or not meth_re.search(code):
            # save failed attempt with reason (update existing q if present)
            msg = f"Submission must use {required_method}() as required by the assignment"
            try:
                if q:
                    q.status = "failed"
                    q.error_message = msg
                    db.session.add(q)
                    db.session.commit()
                else:
                    q2 = Query(
                        user_id=user_id,
                        assignment_id=assignment_id,
                        query_text=code,
                        status="failed",
                        error_message=msg,
                    )
                    db.session.add(q2)
                    db.session.commit()
            except SQLAlchemyError:
                _safe_rollback()
            return jsonify({"error": msg, "error_text": msg, "required_method": required_method}), 400

    mongo_uri = current_app.config.get("MONGO_URI")
    if not mongo_uri or "/" not in mongo_uri.strip("/"):
        return jsonify({"error": "MONGO_URI must include database name, e.g. mongodb://mongo:27017/mongo_train"}), 500

    started = datetime.utcnow()
    try:
        rc, out, err = _run_mongosh(code, mongo_uri)
    except subprocess.TimeoutExpired:
        try:
            msg = "mongosh timed out"
            if q:
                q.status = "error"
                q.error_message = msg
                db.session.add(q)
                db.session.commit()
            else:
                q2 = Query(
                    user_id=user_id,
                    assignment_id=assignment_id,
                    query_text=code,
                    status="error",
                    error_message=msg,
                )
                db.session.add(q2)
                db.session.commit()
        except SQLAlchemyError:
            _safe_rollback()
        return jsonify({"error": "Mongo shell timed out"}), 504
    except FileNotFoundError:
        return jsonify({"error": "mongosh not found. Install mongosh in your container/image."}), 500

    exec_ms = int((datetime.utcnow() - started).total_seconds() * 1000)

    if rc != 0:
        # Prefer structured error from our JS wrapper (stdout JSON), fallback to stderr
        msg = "Unknown mongosh error"
        try:
            parsed = json.loads(out or "{}")
            if isinstance(parsed, dict) and "__mongo_error" in parsed:
                msg = parsed["__mongo_error"]
            else:
                # if stdout contains something else, use it
                if out:
                    msg = out
        except Exception:
            # stdout wasn't JSON; prefer stderr if present
            if err:
                msg = err
            elif out:
                msg = out

        # Save / update Query with error info
        try:
            if q:
                q.status = "error"
                q.error_message = msg
                try:
                    q.error_json = {"stdout": out, "stderr": err}
                except Exception:
                    pass
                db.session.add(q)
                db.session.commit()
            else:
                q2 = Query(
                    user_id=user_id,
                    assignment_id=assignment_id,
                    query_text=code,
                    status="error",
                    error_message=msg,
                )
                try:
                    q2.error_json = {"stdout": out, "stderr": err}
                except Exception:
                    pass
                db.session.add(q2)
                db.session.commit()
        except SQLAlchemyError:
            _safe_rollback()

        return jsonify({"error": msg, "error_text": msg, "required_method": required_method}), 400

    try:
        data = json.loads(out) if out else []
        if isinstance(data, dict):
            docs = [data]
        elif isinstance(data, list):
            docs = data
        else:
            docs = [data]
    except Exception as e:
        msg = f"Invalid mongosh JSON output: {e}"
        try:
            if q:
                q.status = "error"
                q.error_message = msg
                db.session.add(q)
                db.session.commit()
            else:
                q2 = Query(
                    user_id=user_id,
                    assignment_id=assignment_id,
                    query_text=code,
                    status="error",
                    error_message=msg,
                )
                db.session.add(q2)
                db.session.commit()
        except SQLAlchemyError:
            _safe_rollback()
        return jsonify({"error": msg}), 500

    normalized = normalize_docs(docs)

    # diagnostics: if result is empty but tests expect rows, run quick diagnostics
    diag = None
    try:
        match = ALLOWED_SHELL.match(code)
        coll_name = match.group('coll') if match else None
        # we'll only run diagnostics if there was a collection name and normalized empty
        if coll_name and len(normalized) == 0:
            diag_script = f"printjson(db.getCollectionNames()); printjson(db.{coll_name}.find().limit(5).toArray());"
            rc2, out2, err2 = _run_mongosh(diag_script, mongo_uri)
            diag = {"rc": rc2, "out": out2, "err": err2}
    except Exception:
        diag = {"rc": -1, "out": None, "err": "diag-failed"}

    tests = AssignmentTest.query.filter_by(assignment_id=assignment_id).all()
    all_passed, test_results = True, []
    failure_reasons = []
    for t in tests:
        expected = t.expected_result
        if isinstance(expected, str):
            try:
                expected = json.loads(expected)
            except Exception:
                expected = {"_raw": expected}

        passed = (expected == normalized)
        all_passed &= passed

        # build detailed result for UI
        tr = {
            "test_id": t.test_id,
            "description": t.test_description,
            "passed": passed
        }
        if not passed:
            # include small samples to help debugging
            expected_sample = expected if (isinstance(expected, list) or isinstance(expected, dict)) else [expected]
            actual_sample = normalized[:5]
            if isinstance(expected, list):
                reason = f"expected {len(expected)} docs, got {len(normalized)}"
            else:
                reason = "expected value mismatch"
            tr.update({
                "expected_sample": expected_sample if isinstance(expected_sample, list) else [expected_sample],
                "actual_sample": actual_sample,
                "failure_reason": reason
            })
            failure_reasons.append(f"Test {t.test_id}: {reason}")

        test_results.append(tr)

    # Update the previously-created Query record if present, otherwise create a new one
    try:
        if q:
            q.status = "ok" if all_passed else "failed"
            q.result = normalized
            q.exec_ms = exec_ms
            q.result_count = len(normalized)
            if diag:
                try:
                    q.error_json = diag
                except Exception:
                    pass
            db.session.add(q)
            db.session.commit()
        else:
            q = Query(
                user_id=user_id,
                assignment_id=assignment_id,
                query_text=code,
                status="ok" if all_passed else "failed",
                result=normalized,
                exec_ms=exec_ms,
                result_count=len(normalized),
            )
            if diag:
                try:
                    q.error_json = diag
                except Exception:
                    pass
            db.session.add(q)
            db.session.commit()
    except (NoReferencedTableError, ProgrammingError) as e:
        # FK / table missing: DB schema not initialized or broken. Log and return success result to user
        print(f"[attempts_routes] DB schema issue saving query result: {e}")
        # try to persist a minimal Query without FK fields if possible
        try:
            q.user_id = None
            db.session.add(q)
            db.session.commit()
        except Exception:
            _safe_rollback()
        # include failure reasons in error_text if tests failed
        error_text = None
        if not all_passed:
            error_text = "; ".join(failure_reasons) if failure_reasons else None
        return jsonify({
            "passed": all_passed,
            "tests": test_results,
            "result_sample": normalized[:5],
            "warning": "Database schema not initialized; query result not fully saved",
            "error_text": error_text,
            "required_method": required_method
        }), 200
    except SQLAlchemyError as e:
        _safe_rollback()
        return jsonify({"error": "Database error saving query result", "details": str(e)}), 500

    # build top-level error_text when tests failed to help user
    error_text = None
    if not all_passed:
        error_text = "; ".join(failure_reasons) if failure_reasons else None

    return jsonify({
        "passed": all_passed,
        "tests": test_results,
        "result_sample": normalized[:5],
        "required_method": required_method,
        "error_text": error_text
    })
