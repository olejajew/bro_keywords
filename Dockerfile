# Указываем базовый образ Python
FROM python:3.9

# Устанавливаем переменную окружения для неиз interact-ного вывода
ENV PYTHONUNBUFFERED 1

# Устанавливаем pipenv
RUN pip install --no-cache-dir pipenv

# Создаем и используем рабочую директорию
WORKDIR /app

# Копируем Pipfile и Pipfile.lock в контейнер
COPY Pipfile Pipfile.lock /app/

# Устанавливаем зависимости через pipenv
RUN pipenv install --deploy --system

# Копируем все файлы проекта в контейнер
COPY . /app/

# Указываем команду для запуска приложения
CMD ["python", "run.py"]
