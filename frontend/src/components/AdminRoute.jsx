import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div style={{padding:24}}>Загрузка...</div>;
  if (!user || !user.is_admin) return <Navigate to="/" replace />;
  return children;
}
