# Используем базовый образ с Python
FROM python:3.13-alpine

# Задаём переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1

# Задаем рабочий каталог в контейнере
WORKDIR /app

# Копируем все файлы нашего приложения
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Открываем порт 8000 для доступа к приложению
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
