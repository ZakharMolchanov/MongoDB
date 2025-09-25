import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const nav = useNavigate();
  const { register } = useAuth();
  const [form, setForm] = useState({
    email: "",
    first_name: "",
    last_name: "",
    password: "",
  });
  const [err, setErr] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false); // Состояние для загрузки

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    setInfo("");
    setLoading(true);  // Начинаем загрузку
    try {
      await register(form);
      nav("/topics");
    } catch (e) {
      // auth context throws Error with friendly message. If message indicates email exists, show info box.
      const msg = e?.message || e?.response?.data?.error || "Ошибка регистрации";
      const lower = String(msg).toLowerCase();
      if (lower.includes("существ" ) || lower.includes("already")) {
        setInfo(msg);
      } else {
        setErr(msg);
      }
    } finally {
      setLoading(false);  // Завершаем загрузку
    }
  };

  return (
    <div className="auth-card">
      <h2>Создать аккаунт</h2>
      <p>Присоединяйтесь к тренажеру MongoDB</p>
  {err && <div className="error-box">{err}</div>} {/* Выводим ошибки */}
  {info && <div className="info-box">{info}</div>} {/* Информационные сообщения */}
      <form onSubmit={onSubmit} className="auth-form">
        <div>
          <label>Email</label>
          <input
            name="email"
            type="email"
            value={form.email}
            placeholder="you@example.com"
            onChange={onChange}
            required
          />
        </div>
        <div>
          <label>Имя</label>
          <input
            name="first_name"
            value={form.first_name}
            placeholder="Иван"
            onChange={onChange}
            required
          />
        </div>
        <div>
          <label>Фамилия</label>
          <input
            name="last_name"
            value={form.last_name}
            placeholder="Иванов"
            onChange={onChange}
            required
          />
        </div>
        <div>
          <label>Пароль</label>
          <input
            name="password"
            type="password"
            value={form.password}
            placeholder="••••••••"
            onChange={onChange}
            required
            minLength={8}  // Требуем минимум 8 символов
          />
        </div>
        <button className="btn primary" type="submit" disabled={loading}>
          {loading ? "Загрузка..." : "Зарегистрироваться"} {/* Кнопка с индикатором */}
        </button>
      </form>
      <p>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </div>
  );
}
