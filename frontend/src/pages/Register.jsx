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

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      await register(form);
      nav("/login");
    } catch (e) {
      setErr(e?.response?.data?.error || "Ошибка регистрации");
    }
  };

  return (
    <div className="auth-card">
      <h2>Создать аккаунт</h2>
      <p>Присоединяйтесь к тренажеру MongoDB</p>
      {err && <div className="error-box">{err}</div>}
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
          />
        </div>
        <button className="btn primary" type="submit">
          Зарегистрироваться
        </button>
      </form>
      <p>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </div>
  );
}
