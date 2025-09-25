import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { topicsApi } from "../api";

export default function Assignments() {
  const { id } = useParams();
  const [topic, setTopic] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // Добавляем состояние для ошибок

  useEffect(() => {
    topicsApi
      .getOne(id)
      .then((res) => {
        setTopic(res.data);
        setAssignments(res.data.assignments || []);
      })
      .catch((err) => {
        console.error("Ошибка:", err);
        setError("Не удалось загрузить данные о заданиях.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="container">Загрузка...</div>;

  return (
    <div className="container">
      <h2>{topic?.title || "Задания"}</h2>
      <p style={{ color: "var(--muted)" }}>{topic?.description}</p>

      {/* Обработка ошибок */}
      {error && <div className="error-message">{error}</div>}

      {assignments.length === 0 ? (
        <p>Заданий пока нет</p>
      ) : (
        <div className="grid-3">
          {assignments.map((a) => (
            <Link
              key={a.assignment_id}
              to={`/assignments/${a.assignment_id}`}
              className="card assignment-card"
              style={{ textDecoration: "none" }}
            >
              <h3>{a.title}</h3>
              <p>{a.description}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
