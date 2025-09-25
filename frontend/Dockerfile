FROM node:18

WORKDIR /app

# Копируем только package.json и package-lock.json для установки зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все остальные файлы
COPY . .

# Стандартно используем порт 5173 для Vite
EXPOSE 5173

# Указываем команду для старта приложения
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
