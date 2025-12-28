FROM node:20

WORKDIR /app

# Копируем только package.json + package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm ci --legacy-peer-deps

# Копируем всё кроме node_modules
COPY . .

# Запуск dev-сервера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
