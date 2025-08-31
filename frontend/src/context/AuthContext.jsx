import React, { createContext, useContext, useEffect, useState } from "react";
import { authApi } from "../api";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export default function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(token));

  useEffect(() => {
    if (!token) return;
    // подгружаем профиль при наличии токена
    authApi.me()
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = async (email, password) => {
    const { data } = await authApi.login({ email, password });
    // бэк должен вернуть { token: "..." }
    const t = data.token || data.access_token || data.jwt;
    if (!t) throw new Error("Токен не получен");
    localStorage.setItem("token", t);
    setToken(t);
    const me = await authApi.me();
    setUser(me.data);
  };

  const register = async (payload) => {
    await authApi.register(payload);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  const value = { token, user, loading, login, register, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
