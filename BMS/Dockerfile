# Используем базовый образ с Python
FROM python:3.13-alpine

# Задаём переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1

# Задаем рабочий каталог в контейнере
WORKDIR /app

# Копируем все файлы нашего приложения
COPY . .

# Установим зависимости и netcat
RUN apk add --no-cache netcat-openbsd && \
    chmod +x init_db.sh && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Открываем порт 8000 для доступа к приложению
EXPOSE 8000

# Указываем скрипт в качестве точки входа
CMD ["./init_db.sh"]
