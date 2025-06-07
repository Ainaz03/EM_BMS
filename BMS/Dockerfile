FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Копируем весь проект в /app, включая init_db.sh
COPY . .

# Устанавливаем netcat и делаем скрипт исполняемым
RUN apk add --no-cache netcat-openbsd \
    && chmod +x /app/init_db.sh \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# По умолчанию запускаем наш скрипт
CMD ["sh", "/app/init_db.sh"]
