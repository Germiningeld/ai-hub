#!/bin/bash

# Проверка наличия директории
mkdir -p nginx/ssl

# Удаление старых сертификатов если они существуют
if [ -f nginx/ssl/server.key ] || [ -f nginx/ssl/server.crt ]; then
  echo "Удаление существующих сертификатов..."
  rm -f nginx/ssl/server.key nginx/ssl/server.crt
fi

# Создание новых самоподписанных сертификатов
echo "Создание новых SSL сертификатов..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/server.key \
  -out nginx/ssl/server.crt \
  -subj "/C=RU/ST=State/L=City/O=Organization/CN=aihub.workindev.ru"

# Проверка прав доступа
chmod 644 nginx/ssl/server.crt
chmod 600 nginx/ssl/server.key

echo "SSL сертификаты успешно созданы."