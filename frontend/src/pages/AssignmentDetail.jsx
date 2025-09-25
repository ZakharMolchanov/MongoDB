import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-javascript";
import "ace-builds/src-noconflict/theme-github";
import "ace-builds/src-noconflict/ext-language_tools";
import ChatDrawer from "../components/ChatDrawer";
import { aiApi } from "../api.ai";
import { useAuth } from "../context/AuthContext";

export default function AssignmentDetail() {
  const { id } = useParams();
  const [assignment, setAssignment] = useState(null);
  const [code, setCode] = useState("db.collection.find({})");
  const [result, setResult] = useState(null);
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [runLoading, setRunLoading] = useState(false);
  const [error, setError] = useState(null);  // Добавляем состояние для ошибок

  // чат
  const [chatOpen, setChatOpen] = useState(false);
  const [aiReply, setAiReply] = useState("");
  const { token, user } = useAuth();

  useEffect(() => {
    // Получаем задание с сервера
    api
      .get(`/assignments/${id}`)
      .then((res) => setAssignment(res.data))
      .catch((err) => setError("Ошибка загрузки задания"))
      .finally(() => setLoading(false));
    // load user's attempts for this assignment (history)
    loadAttempts();
  }, [id]);

  const loadAttempts = () => {
    api
      .get(`/assignments/${id}/attempts`)
      .then((res) => setAttempts(res.data || []))
      .catch(() => setAttempts([]));
  };

  const handleRun = async () => {
    setRunLoading(true);
    try {
      const res = await api.post(`/assignments/${id}/attempts`, { code });
      setResult(res.data);
      // refresh attempts after a run
      loadAttempts();
    } catch (err) {
      const emsg = err.response?.data?.error || err.message || "Ошибка выполнения";
      const err_text = err.response?.data?.error_text || err.response?.data?.details || null;
      setError(emsg);
      setResult({ error: emsg, error_text: err_text });
    } finally {
      setRunLoading(false);
    }
  };

  // контекст для AI
  const ctx = assignment
    ? {
        assignment_title: assignment.title,
        assignment_description: assignment.description || "",
        schema: assignment.schema || null,
        user_query: code || "",
        error_text: result?.error || null,
      }
    : null;

  const askHint = async () => {
    if (!ctx) return;
    setAiLoading(true);
    try {
      const res = await aiApi.hint(ctx);
  setAiReply(res.data.reply);
      setChatOpen(true);
    } catch (err) {
      setError(err.response?.data?.error || "Ошибка при запросе подсказки");
    }
    setAiLoading(false);
  };

  const askExplain = async () => {
    if (!ctx) return;
    setAiLoading(true);
    try {
      const res = await aiApi.explain(ctx);
  setAiReply(res.data.reply);
      setChatOpen(true);
    } catch (err) {
      setError(err.response?.data?.error || "Ошибка при запросе объяснения");
    }
    setAiLoading(false);
  };

  const askFix = async () => {
    if (!ctx) return;
    setAiLoading(true);
    try {
      const res = await aiApi.fixError(ctx);
  setAiReply(res.data.reply);
      setChatOpen(true);
    } catch (err) {
      setError(err.response?.data?.error || "Ошибка при запросе исправления");
    }
    setAiLoading(false);
  };

  if (loading) return <div className="container">Загрузка...</div>;

  return (
    <div className="container">
      {error && <div style={{ color: "red" }}>{error}</div>} {/* Отображаем ошибки */}
      <h2>{assignment?.title}</h2>
      <p>{assignment?.description}</p>
      {assignment?.schema && assignment?.schema.required_method && (
        <div style={{ marginTop: 8, padding: 10, background: '#eef6ff', borderRadius: 6 }}>
          <b>Требование:</b> Для этого задания обязательно используйте <code>{assignment.schema.required_method}()</code> в вашем запросе.
        </div>
      )}

      <h3>Напиши MongoDB-запрос</h3>
      <AceEditor
        mode="javascript"
        theme="github"
        value={code}
        onChange={(v) => setCode(v)}
        name="mongo_editor"
        width="100%"
        height="200px"
        fontSize={14}
        showPrintMargin={false}
        showGutter={true}
        highlightActiveLine={true}
        setOptions={{
          enableBasicAutocompletion: true,
          enableLiveAutocompletion: true,
          enableSnippets: true,
        }}
      />

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button className="btn primary" onClick={handleRun} disabled={runLoading}>
          {runLoading ? 'Выполняется...' : 'Выполнить'}
        </button>
        <button className="btn ghost" onClick={askHint} disabled={!token || aiLoading}>
          {aiLoading ? 'Загрузка...' : 'Подсказка'}
        </button>
        <button className="btn ghost" onClick={askFix} disabled={!token || !result?.error || aiLoading}>
          {aiLoading ? 'Загрузка...' : 'Разобрать ошибку'}
        </button>
        <button className="btn" onClick={() => setChatOpen(true)} disabled={!token}>
          Открыть чат
        </button>
      </div>

      {!token && (
        <div style={{ marginTop: 12, padding: 10, background: "#fff7ed", borderRadius: 8 }}>
          Для использования подсказок и чата нужно войти в аккаунт. <a href="/login">Войти</a>
        </div>
      )}

      {result && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3>Результат</h3>
          {result.error ? (
            <>
              <pre style={{ color: "red" }}>{result.error}</pre>
              {result.error_text && <pre style={{ color: "#880000" }}>Подробности: {result.error_text}</pre>}
            </>
          ) : (
            <>
              <p>
                <b>Тесты:</b> {result.passed ? "✅ Пройдено" : "❌ Ошибки"}
              </p>
              {/* Per-test breakdown */}
              {Array.isArray(result.tests) && (
                <div style={{ marginBottom: 12 }}>
                  {result.tests.map((t) => (
                    <div key={t.test_id} style={{ padding: 8, border: '1px solid #eee', borderRadius: 6, marginBottom: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div><b>Test {t.test_id}:</b> {t.description}</div>
                        <div>{t.passed ? '✅' : '❌'}</div>
                      </div>
                      {!t.passed && (
                        <div style={{ marginTop: 8 }}>
                          {t.failure_reason && <div style={{ color: '#b91c1c' }}>Причина: {t.failure_reason}</div>}
                          {t.expected_sample && (
                            <div style={{ marginTop: 6 }}>
                              <div style={{ fontSize: 12, color: '#666' }}>Ожидается (пример):</div>
                              <pre style={{ maxHeight: 120, overflow: 'auto' }}>{JSON.stringify(t.expected_sample, null, 2)}</pre>
                            </div>
                          )}

                          
                          {t.actual_sample && (
                            <div style={{ marginTop: 6 }}>
                              <div style={{ fontSize: 12, color: '#666' }}>Фактический (пример):</div>
                              <pre style={{ maxHeight: 120, overflow: 'auto' }}>{JSON.stringify(t.actual_sample, null, 2)}</pre>
                            </div>
                          )}
                        </div>
                      )}

                          {/* attempts removed from per-test loop to render once at the bottom */}
                    </div>
                  ))}
                </div>
              )}

              <pre style={{ maxHeight: 300, overflow: "auto" }}>
                {JSON.stringify(result.result_sample || result, null, 2)}
              </pre>
              {result.error_text && <pre style={{ color: "#880000", marginTop: 8 }}>Подробности: {result.error_text}</pre>}
            </>
          )}
        </div>
      )}

      <div className="card" style={{ marginTop: 20 }}>
        <h3>📂 Схема базы</h3>
        {assignment?.schema ? (
          (() => {
            const schemaObj = assignment.schema;
            const entries = Object.entries(schemaObj || {});
            const isCollSchema = entries.length > 0 && entries.every(([, v]) => Array.isArray(v));
            if (isCollSchema) {
              return entries.map(([coll, docs]) => (
                <div key={coll} style={{ marginBottom: "16px" }}>
                  <h4>{coll}</h4>
                  <table
                    style={{
                      width: "100%",
                      borderCollapse: "collapse",
                      marginBottom: "8px",
                    }}
                  >
                    <thead>
                      <tr>
                        <th
                          style={{
                            borderBottom: "1px solid #ddd",
                            textAlign: "left",
                            padding: "4px 8px",
                          }}
                        >
                          Поле
                        </th>
                        <th
                          style={{
                            borderBottom: "1px solid #ddd",
                            textAlign: "left",
                            padding: "4px 8px",
                          }}
                        >
                          Примеры
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {Array.isArray(docs) && docs.length > 0 &&
                        Object.keys(docs[0] || {}).map((field) => (
                          <tr key={field}>
                            <td style={{ padding: "4px 8px" }}>{field}</td>
                            <td style={{ padding: "4px 8px", color: "#666" }}>
                              {docs
                                .map((d) => (d && d[field] !== undefined ? String(d[field]) : "—"))
                                .slice(0, 3)
                                .join(", ")}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              ));
            }
            // Fallback: render raw schema JSON if it's not a coll->docs mapping
            return <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(schemaObj, null, 2)}</pre>;
          })()
        ) : (
          <p>Схема не задана</p>
        )}
      </div>
      {/* User attempts history: render once at the bottom, fetched from backend */}
      <div className="card" style={{ marginTop: 20 }}>
        <h3>Мои попытки</h3>
        {attempts.length === 0 ? (
          <p>Пока нет попыток</p>
        ) : (
          <div>
            {attempts.map((a) => (
              <div key={a.id || a.query_id} style={{ padding: 8, borderBottom: '1px solid #eee' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <div><b>{new Date(a.created_at).toLocaleString()}</b> — {a.status}</div>
                  <div>{a.exec_ms ? `${a.exec_ms} ms` : ''} {a.result_count !== undefined ? ` — ${a.result_count} rows` : ''}</div>
                </div>
                {a.error_message && <div style={{ color: '#b91c1c' }}>Ошибка: {a.error_message}</div>}
                <pre style={{ maxHeight: 120, overflow: 'auto' }}>{a.code}</pre>
              </div>
            ))}
          </div>
        )}
      </div>

      <ChatDrawer open={chatOpen} onClose={() => setChatOpen(false)} aiReply={aiReply} />
    </div>
  );
}
