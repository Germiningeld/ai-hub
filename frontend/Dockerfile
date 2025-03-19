# Этап сборки
FROM node:18 as build-stage

WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci

# Копирование исходного кода
COPY . .

# Аргументы сборки
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Отладочная информация
RUN echo "API URL: $VITE_API_BASE_URL"
RUN ls -la

# Сборка приложения для production
RUN npm run build

# Вывести содержимое директории dist для отладки
RUN ls -la dist/

# Этап production
FROM nginx:stable-alpine as production-stage

# Создание конфигурации nginx если её еще нет
RUN [ ! -f /etc/nginx/conf.d/default.conf ] && echo 'Creating default Nginx config' || echo 'Using existing Nginx config'

# Копирование собранных файлов из предыдущего этапа
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Конфигурация Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Проверим, что все файлы на месте
RUN ls -la /usr/share/nginx/html
RUN cat /etc/nginx/conf.d/default.conf

EXPOSE 80

# Запуск Nginx
CMD ["nginx", "-g", "daemon off;"]