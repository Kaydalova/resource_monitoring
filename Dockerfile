FROM python:3.8

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Копирование исходного кода приложения
COPY . /app

# CMD ["flask", "run", "--host=0.0.0.0"]
CMD export FLASK_APP=test_task_app && export FLASK_DEBUG=1 && flask run --host=0.0.0.0