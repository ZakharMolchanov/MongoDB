import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import NavBar from "./components/NavBar.jsx";
import Footer from "./components/Footer.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Topics from "./pages/Topics.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";

export default function App() {
  return (
    <div>
      {/* Шапка */}
      <NavBar />

      {/* Основное содержимое */}
      <main className="container" style={{ marginTop: "32px" }}>
        <Routes>
          {/* Главная страница ведёт на список тем */}
          <Route path="/" element={<Navigate to="/topics" replace />} />

          {/* Авторизация / регистрация */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Список тем (защищённый доступ) */}
          <Route
            path="/topics"
            element={
              <ProtectedRoute>
                <Topics />
              </ProtectedRoute>
            }
          />

          {/* 404 */}
          <Route path="*" element={<div>Страница не найдена</div>} />
        </Routes>
      </main>

      {/* Футер */}
      <Footer />
    </div>
  );
}
