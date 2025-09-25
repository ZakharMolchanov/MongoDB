import os
from typing import List, Optional, Literal, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# ---- DeepSeek config ----
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
DEEPSEEK_BASE = os.getenv("DEEPSEEK_BASE", "https://api.deepseek.com/v1").rstrip("/")

if not DEEPSEEK_API_KEY:
    # Не падаем на импорте, но вернём 500 на /chat без ключа
    pass

CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(title="AI Assistant Service (DeepSeek)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ Schemas ------------ #

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str

class ChatPayload(BaseModel):
    messages: List[ChatMessage]
    temperature: float = 0.2
    top_p: float = 0.9
    stream: bool = False  # сейчас используем только non-stream

class TaskContext(BaseModel):
    assignment_title: str
    assignment_description: str
    schema: Dict[str, Any] | None = None
    user_query: Optional[str] = None
    error_text: Optional[str] = None

class TaskPrompt(BaseModel):
    kind: Literal["hint", "explain", "fix_error"]
    context: TaskContext

# ------------ Prompt templates ------------ #

SYSTEM_TASK = (
    "Ты — помощник по MongoDB. Отвечай кратко и по делу, с примерами в стиле mongo shell. "
    "Если просит подсказку — веди от простого к сложному, сначала вопросы про понимание. "
    "Если есть схема, используй корректные имена коллекций и полей. "
    "Если просят исправить ошибку — сначала короткий анализ, затем точная правка, потом финальный корректный запрос. "
    "Никогда не выдумывай данные и не меняй смысл задания."
)

HINT_TMPL = """Задание: {title}
Описание: {desc}

Схема (JSON, коллекции и примерные поля):
{schema}

Если пользователь уже написал запрос — вот он:
{user_query}

Дай подсказку по решению. Не раскрывай сразу полный ответ; предложи путь и ключевые шаги (+ возможные операторы)."""

EXPLAIN_TMPL = """Задание: {title}
Описание: {desc}

Схема:
{schema}

Попросили объяснить подход и предложить корректный запрос (сообщи и альтернативы, где уместно)."""

FIX_TMPL = """Задание: {title}
Описание: {desc}

Схема:
{schema}

Запрос пользователя:
{user_query}

Ошибка/лог:
{error}

1) В чём причина?
2) Как исправить (точная правка)?
3) Дай финальный корректный запрос.
"""

# ------------ DeepSeek client ------------ #

async def call_deepseek_chat(
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    top_p: float = 0.9,
    stream: bool = False,
) -> str:
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="DEEPSEEK_API_KEY is not set")

    url = f"{DEEPSEEK_BASE}/chat/completions"
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False if stream is False else True,  # на будущее
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, json=payload, headers=headers)
        if r.status_code != 200:
            # Пробросим ответ DeepSeek для дебага
            raise HTTPException(status_code=502, detail=f"DeepSeek error: {r.text}")

        data = r.json()
        # Формат OpenAI-совместимый:
        # data["choices"][0]["message"] -> {"role": "assistant", "content": "...", "reasoning_content": "...?"}
        try:
            msg = data["choices"][0]["message"]
        except Exception:
            raise HTTPException(status_code=502, detail=f"DeepSeek unexpected response: {data}")

        content = (msg.get("content") or "").strip()
        reasoning = (msg.get("reasoning_content") or "").strip()

        # Если это deepseek-reasoner — можно вернуть и рассуждения, и финальный ответ
        if reasoning and content:
            return f"{content}\n\n---\n(reasons)\n{reasoning}"
        return content or reasoning or ""

# ------------ Endpoints ------------ #

@app.get("/health")
async def health():
    return {
        "ok": True,
        "model": DEEPSEEK_MODEL,
        "uses": "DeepSeek Chat Completions",
        "base": DEEPSEEK_BASE,
        "has_api_key": bool(DEEPSEEK_API_KEY),
    }

@app.post("/chat")
async def chat(payload: ChatPayload):
    messages = [{"role": m.role, "content": m.content} for m in payload.messages]
    # добавим системный контекст, если его нет
    if not any(m["role"] == "system" for m in messages):
        messages = [{"role": "system", "content": SYSTEM_TASK}] + messages

    text = await call_deepseek_chat(
        messages,
        temperature=payload.temperature,
        top_p=payload.top_p,
        stream=payload.stream,
    )
    return {"reply": text}

@app.post("/task")
async def task_prompt(body: TaskPrompt):
    ctx = body.context
    schema_str = "—" if not ctx.schema else str(ctx.schema)

    if body.kind == "hint":
        user = HINT_TMPL.format(
            title=ctx.assignment_title, desc=ctx.assignment_description,
            schema=schema_str, user_query=(ctx.user_query or "—")
        )
    elif body.kind == "explain":
        user = EXPLAIN_TMPL.format(
            title=ctx.assignment_title, desc=ctx.assignment_description,
            schema=schema_str
        )
    elif body.kind == "fix_error":
        user = FIX_TMPL.format(
            title=ctx.assignment_title, desc=ctx.assignment_description,
            schema=schema_str, user_query=(ctx.user_query or "—"),
            error=(ctx.error_text or "—")
        )
    else:
        raise HTTPException(400, "unknown kind")

    messages = [
        {"role": "system", "content": SYSTEM_TASK},
        {"role": "user", "content": user},
    ]
    text = await call_deepseek_chat(messages)
    return {"reply": text}
