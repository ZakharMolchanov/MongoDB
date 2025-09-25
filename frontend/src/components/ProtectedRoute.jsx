import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { token, user, loading } = useAuth();
  const location = useLocation();

  // Если данные загружаются, показываем индикатор загрузки
  if (loading) {
    return (
      <div style={{ padding: 24, textAlign: "center" }}>
        <p>Загрузка...</p>
        {/* Можно добавить спиннер для анимации */}
      </div>
    );
  }

  // Если пользователь не авторизован, перенаправляем на страницу логина
  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  // Если токен есть, отображаем дочерние компоненты
  return children;
}
