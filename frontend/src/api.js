import axios from "axios";

// Создаём экземпляры axios с базовыми URL из переменных окружения
// Отправляем auth-запросы через фронт-прокси (/auth) в dev/prod по умолчанию.
const authApi = axios.create({
  baseURL: import.meta.env.VITE_AUTH_URL || "/auth", // можно переопределить в env
  withCredentials: true,
});

// coreApi обращается через префикс /api (через Vite proxy или nginx)
const coreApi = axios.create({
  baseURL: import.meta.env.VITE_CORE_API_URL || "/api",
  withCredentials: true,
});

// Интерсепторы: добавляем Authorization и логируем
authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

coreApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  console.log("[coreApi] sending", config.method, config.url, "token:", token);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

coreApi.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("[coreApi] response error", err?.response?.status, err?.response?.data);
    return Promise.reject(err);
  }
);

// auth
export const authApiMethods = {
  // authApi.baseURL уже содержит /auth (по умолчанию), поэтому эндпоинты относительные
  register: (payload) => authApi.post(`/register`, payload),
  login: (payload) => authApi.post(`/login`, payload),
  me: () => authApi.get(`/me`),
  isAdmin: (userId) => authApi.get(`/is-admin/${userId}`),
};

// topics
export const topicsApi = {
  getAll: (params) => coreApi.get(`/topics`, { params }),  // optional params: q, difficulty
  getOne: (id) => coreApi.get(`/topics/${id}`),
};

export const assignmentsApi = {
  getByTopic: (topicId) => coreApi.get(`/topics/${topicId}/assignments`),
  list: (params) => coreApi.get(`/assignments`, { params }), // optional params: q, topic_id
};

// Export coreApi as the default axios instance so `import api from "../api"` works
export default coreApi;
