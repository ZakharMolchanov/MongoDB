import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function NavBar() {
  const { user, logout } = useAuth();

  return (
    <nav className="nav">
      <div className="container nav-inner">
        <Link to="/" className="brand">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path
              d="M4 12c0-4.418 3.582-8 8-8 1.93 0 3.705.684 5.078 1.825L12 12l-5.66 5.66A7.962 7.962 0 0 1 4 12Z"
              fill="#10a37f"
            />
            <path
              d="M12 12l5.66-5.66A7.962 7.962 0 0 1 20 12c0 4.418-3.582 8-8 8-1.93 0-3.705-.684-5.078-1.825L12 12Z"
              fill="#0a8a6a"
            />
          </svg>
          Mongo Trainer
          <span className="badge">MVP</span>
        </Link>

        <div className="actions">
          {user ? (
            <>
              {user.is_admin && (
                <span style={{marginRight:8}}>
                  <Link to="/admin/logs" className="btn ghost" style={{marginRight:6}}>Logs</Link>
                  <Link to="/admin/users" className="btn ghost" style={{marginRight:6}}>Users</Link>
                  <Link to="/admin/topics" className="btn ghost" style={{marginRight:6}}>Topics</Link>
                  <Link to="/admin/assignments" className="btn ghost">Assignments</Link>
                </span>
              )}
              <span className="user-name">
                👤 {user.first_name} {user.last_name}
              </span>
              <button onClick={logout} className="btn logout-btn">
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn ghost">
                Войти
              </Link>
              <Link to="/register" className="btn primary">
                Регистрация
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
