import React, { useState, useEffect } from "react";
import { aiApi } from "../api.ai";  // Используем aiApi для отправки запросов к ai-service
import { useAuth } from "../context/AuthContext";

export default function ChatDrawer({ open, onClose, aiReply = null }) {
  const [history, setHistory] = useState([
    { role: "assistant", content: "Привет! Я помогу с MongoDB. Спросите что угодно." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null); // Добавляем состояние для ошибок
  const { token } = useAuth();

  const send = async () => {
    if (!input.trim()) return;
    if (!token) {
      setError("Требуется вход, чтобы отправлять сообщения в чат");
      return;
    }

    // Build messages array to send to AI
    const msgs = [
      ...history.map((m) => ({ role: m.role, content: m.content })),
      { role: "user", content: input },
    ];

    // Append the user message and a temporary assistant "typing" placeholder
    setHistory((h) => [...h, { role: "user", content: input }, { role: "assistant", content: "ИИ печатает...", temp: true }]);
    setInput("");
    setLoading(true);
    setError(null); // Очищаем ошибки перед отправкой запроса

    try {
      const res = await aiApi.chat(msgs);

      // Replace the temporary assistant message with the real reply
      setHistory((h) => {
        const newH = [...h];
        const tempIndex = newH.findIndex((m) => m.temp);
        if (tempIndex >= 0) {
          newH[tempIndex] = { role: "assistant", content: res?.data?.reply ?? "(пустой ответ)" };
        } else {
          newH.push({ role: "assistant", content: res?.data?.reply ?? "(пустой ответ)" });
        }
        return newH;
      });
    } catch (e) {
      // Try to extract a useful error message from the response
      const msg = e?.response?.data?.error || e?.response?.data?.message || e?.message || "Ошибка запроса к ИИ. Попробуйте позже.";
      setError(msg);

      setHistory((h) => {
        const newH = [...h];
        const tempIndex = newH.findIndex((m) => m.temp);
        const content = typeof msg === "string" ? `Ошибка: ${msg}` : "Ошибка запроса к ИИ";
        if (tempIndex >= 0) {
          newH[tempIndex] = { role: "assistant", content };
        } else {
          newH.push({ role: "assistant", content });
        }
        return newH;
      });
    } finally {
      setLoading(false);
    }
  };

  // Если родитель передаёт aiReply (например ответ от /task), добавим его в историю
  useEffect(() => {
    if (!open) return; // добавляем только когда окно открыто
    if (!aiReply) return;
    setHistory((h) => [...h, { role: "assistant", content: aiReply }]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [aiReply, open]);

  const clear = () => setHistory([{ role: "assistant", content: "Диалог очищен." }]);


  if (!open) return null;
  return (
    <div style={{
      position: "fixed", right: 0, top: 0, bottom: 0, width: 420,
      background: "#fff", borderLeft: "1px solid #eaeaea", boxShadow: "-6px 0 20px rgba(0,0,0,.06)", zIndex: 9999
    }}>
      <div style={{ display:"flex", justifyContent:"space-between", padding: 12, borderBottom: "1px solid #eee" }}>
        <b>Mongo AI помощник</b>
        <div>
          <button className="btn ghost" onClick={clear} style={{ marginRight: 8 }}>Очистить</button>
          <button className="btn" onClick={onClose}>Закрыть</button>
        </div>
      </div>

      {/* Ошибка, если она возникла */}
      {error && <div className="error-box" style={{ color: "red", padding: "10px" }}>{error}</div>}

      <div style={{ padding: 12, overflow: "auto", height: "calc(100% - 120px)" }}>
        {history.map((m, i) => (
          <div key={i} style={{ margin: "8px 0" }}>
            <div style={{ fontSize: 12, color: "#888" }}>{m.role === "user" ? "Вы" : "ИИ"}</div>
            <div style={{
              whiteSpace: "pre-wrap",
              background: m.role === "user" ? "#f5f5f5" : "#f0f9f6",
              padding: 10, borderRadius: 8
            }}>{m.content}</div>
          </div>
        ))}
      </div>

      <div style={{ padding: 12, borderTop: "1px solid #eee" }}>
        {!token && (
          <div style={{ marginBottom: 8, color: "#b91c1c" }}>Требуется вход, чтобы использовать чат. <a href="/login">Войдите</a></div>
        )}

        <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
          <textarea
            rows={2}
            value={input}
            onChange={e => setInput(e.target.value)}
            style={{ flex: 1, resize: "none" }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
          />
          <button
            className="btn primary"
            onClick={send}
            disabled={loading || !token}
            aria-busy={loading}
            style={{ height: 40, display: "flex", alignItems: "center", gap: 8 }}
          >
            {loading ? (
              <>
                <span style={{ fontSize: 14 }}>⏳</span>
                <span>Отправка...</span>
              </>
            ) : (
              "Отправить"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
