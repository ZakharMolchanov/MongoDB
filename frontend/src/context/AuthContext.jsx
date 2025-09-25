import React, { createContext, useContext, useEffect, useState } from "react";
import { authApiMethods } from "../api";  // Импортируем authApiMethods, а не authApi

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export default function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(token));

  useEffect(() => {
    if (!token) return;

    // подгружаем профиль при наличии токена
    setLoading(true); // устанавливаем состояние загрузки
    authApiMethods.me()
      .then(async (res) => {
        const u = res.data;
        try {
          const adm = await authApiMethods.isAdmin(u.id);
          u.is_admin = adm.data?.is_admin || false;
        } catch (e) {
          u.is_admin = false;
        }
        setUser(u);
      })
      .catch((err) => {
        // Не удаляем токен при временных ошибках (например 500). Удаляем при 401/403
        const status = err?.response?.status;
        if (status === 401 || status === 403) {
          localStorage.removeItem("token");
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => setLoading(false));  // Устанавливаем состояние завершения загрузки
  }, [token]);

  const login = async (email, password) => {
    try {
      const { data } = await authApiMethods.login({ email, password });
      const t = data.token || data.access_token || data.jwt;

      if (!t) {
        throw new Error("Токен не получен");
      }

      localStorage.setItem("token", t);
      setToken(t);
  console.log("[Auth] token saved", t);

      // Загружаем данные о пользователе
      const me = await authApiMethods.me();
      setUser(me.data);
    } catch (error) {
  // Prefer server message when available and provide a friendly message for unauthorized
  const status = error?.response?.status;
  const data = error?.response?.data || {};
  const serverMsg = data.error || data.message || data.detail || (Array.isArray(data.errors) && data.errors[0]?.msg);
  const msg = serverMsg || (status === 401 || status === 403 ? "Неверный email или пароль" : error?.message || "Ошибка авторизации");
  throw new Error(msg);
    }
  };

  const register = async (payload) => {
    try {
      await authApiMethods.register(payload);
      // если сервер вернул автоматически токен, лучше логиниться
      if (payload.email && payload.password) {
        await login(payload.email, payload.password);
      }
    } catch (error) {
      // Prefer server-provided message (data.error or data.message). Handle conflict (409) specially.
      const status = error?.response?.status;
  const data = error?.response?.data || {};
  // common places where backends put human messages
  const serverMsg = data.error || data.message || data.detail || (Array.isArray(data.errors) && data.errors[0]?.msg);
      const msg =
        serverMsg ||
        (status === 409 ? "Пользователь с таким email уже существует" : error?.message || "Ошибка регистрации");
      throw new Error(msg);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  const value = { token, user, loading, login, register, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
