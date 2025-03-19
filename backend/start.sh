#!/bin/sh

# Устанавливаем соединение с базой данных на основе переменных окружения
export DATABASE_URL="${POSTGRES_USER:-aihub_admin}:${POSTGRES_PASSWORD:-lLSsdflDFjFjLWSlkLKSDFlsdlksjdLKJSFjk}@postgres:5432/${POSTGRES_DB:-aihub}"

# Выводим информацию для отладки
echo "Starting backend with DATABASE_URL=${DATABASE_URL}"

# Проверяем структуру директорий
ls -la
echo "Содержимое app директории:"
ls -la app/

# Запуск приложения
cd /app
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 4000