# Берем официальный образ Python (как чистый лист Windows, только для Python)
FROM python:3.12-slim

# Создаем рабочую папку внутри контейнера
WORKDIR /app

# Копируем список библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта в контейнер
COPY . .

# По умолчанию мы не указываем команду запуска здесь,
# мы сделаем это в docker-compose, чтобы запустить и бота, и сайт.