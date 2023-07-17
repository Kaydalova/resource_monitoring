# # Используйте базовый образ Python
# FROM python:3.8

# # Установите рабочую директорию внутри контейнера
# WORKDIR /app

# # Скопируйте зависимости проекта в контейнер
# COPY requirements.txt .

# # Установите зависимости
# RUN pip install -r requirements.txt

# # Скопируйте все файлы проекта в контейнер
# COPY . .

# # Задайте переменные окружения для конфигурации
# ENV CONFIG_FILE_PATH /app/config.yaml

# # Запустите ваше приложение при старте контейнера
# CMD ["python", "app.py"]

FROM python:3.8

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка PostgreSQL
RUN apt-get update && apt-get install -y postgresql

# Копирование исходного кода приложения
COPY . /app

# Команда запуска приложения
#CMD ["flask", "run", "--host=localhost"]

#CMD ["flask", "run", "--host=127.0.0.1"]

CMD ["flask", "run", "--host=0.0.0.0"]