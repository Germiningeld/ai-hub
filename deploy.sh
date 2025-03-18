#!/bin/bash

# Генерируем случайные ключи для продакшена
generate_secret_key() {
  openssl rand -hex 32
}

# Проверяем наличие файла .env
if [ ! -f .env ]; then
  echo "Создаем .env файл..."

  # Генерируем секретные ключи
  SECRET_KEY=$(generate_secret_key)
  JWT_SECRET_KEY=$(generate_secret_key)

  # Запрашиваем пароль для базы данных
  read -p "Введите пароль для PostgreSQL: " DB_PASSWORD

  # Запрашиваем домен
  read -p "Введите домен для CORS (например, https://example.com): " DOMAIN

  # Запрашиваем данные для администратора
  read -p "Введите email администратора: " ADMIN_EMAIL
  read -p "Введите логин администратора: " ADMIN_USERNAME
  read -s -p "Введите пароль администратора: " ADMIN_PASSWORD
  echo ""

  # Создаем файл .env на основе образца
  cp env-sample .env

  # Заменяем значения в файле .env
  sed -i "s|сложный_пароль_для_продакшена|$DB_PASSWORD|g" .env
  sed -i "s|сгенерированный_сложный_ключ_для_продакшена|$SECRET_KEY|g" .env
  sed -i "s|сгенерированный_сложный_ключ_для_jwt|$JWT_SECRET_KEY|g" .env
  sed -i "s|https://ваш-домен.com|$DOMAIN|g" .env
  sed -i "s|admin@example.com|$ADMIN_EMAIL|g" .env
  sed -i "s|admin|$ADMIN_USERNAME|g" .env
  sed -i "s|сложный_пароль_администратора|$ADMIN_PASSWORD|g" .env

  echo "Файл .env создан успешно!"
else
  echo "Файл .env уже существует. Пропускаем создание."
fi

# Копируем Dockerfile в соответствующие директории
cp dockerfile-backend backend/Dockerfile
cp dockerfile-frontend frontend/Dockerfile
cp nginx-conf frontend/nginx.conf
cp env-frontend-prod frontend/.env.production

# Запускаем Docker Compose
echo "Запускаем контейнеры Docker..."
docker-compose up -d --build

echo "Проект успешно запущен!"
echo "Backend API доступен по адресу: http://localhost:8000"
echo "Frontend доступен по адресу: http://localhost"