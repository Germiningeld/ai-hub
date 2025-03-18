#!/bin/bash

# Скрипт для инициализации базы данных с нуля
# Запускать после docker-compose up -d

echo "Инициализация базы данных..."

# Проверяем, что контейнер postgres запущен
if ! docker ps | grep -q aihub-postgres; then
  echo "Ошибка: контейнер aihub-postgres не запущен!"
  echo "Сначала запустите контейнеры: docker-compose up -d"
  exit 1
fi

# Подключаемся к postgres и создаем базу данных заново
echo "Подключение к PostgreSQL..."

# Получаем переменные из .env файла
if [ -f .env ]; then
  source <(grep -v '^#' .env | sed -E 's/(.*)=(.*)$/export \1="\2"/g')
else
  echo "Файл .env не найден!"
  exit 1
fi

# Сбрасываем соединения и пересоздаем базу данных
echo "Сброс базы данных..."
docker exec -i aihub-postgres psql -U postgres << EOF
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '${POSTGRES_DB}' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ${POSTGRES_DB};
CREATE DATABASE ${POSTGRES_DB};
EOF

echo "База данных пересоздана!"

# Подключаемся к контейнеру backend и запускаем инициализацию миграций
echo "Инициализация миграций..."

# Проверяем, что контейнер backend запущен
if ! docker ps | grep -q aihub-backend; then
  echo "Ошибка: контейнер aihub-backend не запущен!"
  echo "Сначала запустите контейнеры: docker-compose up -d"
  exit 1
fi

# Создаем Python скрипт для инициализации и запуска миграций
docker exec -i aihub-backend bash -c "cat > /tmp/init_db.py" << 'EOF'
import os
import sys
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
import time

# Ждем, пока база данных будет доступна
time.sleep(5)

# Получаем DATABASE_URL из переменных окружения
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Ошибка: Переменная окружения DATABASE_URL не установлена")
    sys.exit(1)

# Полный URL для подключения к PostgreSQL через SQLAlchemy
if DATABASE_URL.startswith('//'):
    full_url = f"postgresql+psycopg2:{DATABASE_URL}"
else:
    full_url = f"postgresql+psycopg2://{DATABASE_URL}"

print(f"Подключение к базе данных: {full_url}")

# Создаем подключение и проверяем, доступна ли база данных
engine = create_engine(full_url)
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print("Соединение с базой данных установлено успешно!")
except Exception as e:
    print(f"Ошибка подключения к базе данных: {e}")
    sys.exit(1)

# Запускаем миграции
try:
    print("Применение миграций...")
    config = Config("alembic.ini")
    
    # Очищаем таблицу alembic_version, если она существует
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()
            print("Таблица alembic_version очищена!")
    except Exception as e:
        print(f"Ошибка при очистке таблицы alembic_version: {e}")
    
    # Создаем начальную метку
    print("Создание начальной метки миграции...")
    command.stamp(config, "head")
    print("Начальная метка создана!")
    
    # Применяем миграции
    print("Применение миграций...")
    command.upgrade(config, "head")
    print("Миграции успешно применены!")
except Exception as e:
    print(f"Ошибка при применении миграций: {e}")
    sys.exit(1)
EOF

# Запускаем скрипт инициализации базы данных
echo "Запуск скрипта инициализации..."
docker exec -i aihub-backend python /tmp/init_db.py

# Проверяем статус
if [ $? -eq 0 ]; then
  echo "База данных успешно инициализирована!"
else
  echo "Возникла ошибка при инициализации базы данных."
  echo "Для подробной информации подключитесь к контейнеру: docker exec -it aihub-backend bash"
  exit 1
fi

# Перезапускаем backend для применения изменений
echo "Перезапуск backend..."
docker restart aihub-backend

echo "Инициализация завершена успешно!"
echo "Приложение должно быть доступно по адресу: http://localhost:8000"