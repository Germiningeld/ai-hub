#!/bin/bash

# Создание необходимых директорий
mkdir -p nginx/conf.d
mkdir -p nginx/ssl
mkdir -p nginx/logs

# Проверка и копирование конфигурации Nginx
if [ -f "default.conf" ]; then
  cp default.conf nginx/conf.d/default.conf
  echo "Конфигурационный файл nginx скопирован."
else
  echo "ВНИМАНИЕ: default.conf не найден. Убедитесь, что вы создали его."
fi

# Проверка наличия SSL сертификатов
if [ ! -f "nginx/ssl/server.key" ] || [ ! -f "nginx/ssl/server.crt" ]; then
  echo "Создание самоподписанных SSL сертификатов для разработки..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/server.key \
    -out nginx/ssl/server.crt \
    -subj "/C=RU/ST=State/L=City/O=Organization/CN=aihub.workindev.ru"
  echo "SSL сертификаты созданы."
fi

# Установка прав доступа
chmod -R 755 nginx
echo "Права доступа установлены."

echo "Настройка Nginx завершена."