import React, { useEffect, useState } from "react";
import { topicsApi } from "../api.js";

export default function Topics() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    topicsApi
      .getAll()
      .then((res) => setTopics(res.data))
      .catch((err) => console.error("Ошибка загрузки тем:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container">Загрузка...</div>;

  return (
    <div className="container">
      <h2>Темы</h2>
      {topics.length === 0 ? (
        <p>Тем пока нет</p>
      ) : (
        <div className="grid-3">
          {topics.map((t) => (
            <div key={t.topic_id} className="card">
              <h3>{t.title}</h3>
              <p>{t.description}</p>
              <p>
                <b>Сложность:</b> {t.difficulty}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
