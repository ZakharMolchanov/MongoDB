import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { topicsApi } from "../api.js";

export default function Topics() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(""); // Добавляем состояние для ошибки

  useEffect(() => {
    topicsApi
      .getAll()
      .then((res) => setTopics(res.data))
      .catch((err) => {
        console.error("Ошибка загрузки тем:", err);
        setError("Не удалось загрузить темы. Попробуйте снова позже.");
      })
      .finally(() => setLoading(false));
  }, []);

  const [q, setQ] = useState('');
  const search = () => {
    setLoading(true);
    const params = q ? { q } : {};
    topicsApi.getAll(params).then((res) => setTopics(res.data)).catch(() => setError('Не удалось загрузить темы')).finally(() => setLoading(false));
  };

  if (loading) return <div className="container">Загрузка...</div>;

  return (
    <div className="container">
      <h2>Темы</h2>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            <input placeholder='Поиск по темам' value={q} onChange={e=>setQ(e.target.value)} />
            <button className='btn' onClick={search}>Поиск</button>
          </div>
          {error && <div className="error-box">{error}</div>} {/* Показываем ошибку */}
      
      {topics.length === 0 ? (
        <p>Тем пока нет</p>
      ) : (
        <div className="grid-3">
          {topics.map((t) => (
            <Link
              key={t.topic_id}
              to={`/topics/${t.topic_id}`}
              className="card"
              style={{ textDecoration: "none" }}
            >
              <h3>{t.title}</h3>
              <p>{t.description}</p>
              <p>
                <b>Сложность:</b> {t.difficulty}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
