#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  CREATE DATABASE bms_db;
  CREATE DATABASE bms_test;
EOSQL

echo "⏳ Ожидание базы данных..."
# Ждём, пока PostgreSQL примет подключения
while ! nc -z db 5432; do
  sleep 0.5
done

echo "✅ База данных доступна. Применяем миграции Alembic..."
alembic upgrade head

echo "🚀 Запуск приложения FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
