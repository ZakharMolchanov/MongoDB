import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div style={{ padding: 24 }}>Загрузка…</div>;
  if (!token) return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  return children;
}
