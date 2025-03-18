#!/bin/bash

# Скрипт для запуска бэкенда после инициализации БД
# Запускать после ./init_db.sh

echo "Запуск FastAPI сервиса..."

# Проверяем, что контейнер backend запущен
if ! docker ps | grep -q aihub-backend; then
  echo "Ошибка: контейнер aihub-backend не запущен!"
  echo "Сначала запустите контейнеры: docker-compose up -d"
  exit 1
fi

# Останавливаем контейнер backend
docker stop aihub-backend

# Обновляем команду запуска
docker update --command "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" aihub-backend

# Запускаем контейнер backend с новой командой
docker start aihub-backend

echo "Backend успешно запущен!"
echo "API доступно по адресу: http://localhost:8000"
echo "Swagger UI доступен по адресу: http://localhost:8000/docs"