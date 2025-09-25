import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      // Проксируем только API под префиксом /api -> core-service
      "/api": {
        target: "http://core-service:5002",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      // auth-service проксируется как /auth
      "/auth": {
        target: "http://auth-service:5001",
        changeOrigin: true,
        secure: false,
        // Не удаляем префикс /auth — backend ожидает путь /auth/register, /auth/login
      },
      // ai-integration-service
      "/ai": {
        target: "http://ai-integration-service:8088",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/ai/, ""),
      },
    },
  },
  build: {
    outDir: "dist",
  },
  preview: {
    port: 5173,
    host: true,
  },
});

