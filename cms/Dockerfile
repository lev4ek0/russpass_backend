# получаем image для нашего питона
FROM python:3.12

# задаём переменные окружения, чтобы
# предотвратить ряд событий, а именно:
# создания .pyc файлов и использования
# питоном буффера для stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# обновляем  репозитории
RUN apt-get update -y && apt-get upgrade -y

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN apt-get install -y sqlite3 libsqlite3-dev

# ставим локализацию
RUN apt-get install -y gettext

# устанавливаем рабочую директорию
WORKDIR /cms

# ставим python зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# копируем проект
COPY . .
