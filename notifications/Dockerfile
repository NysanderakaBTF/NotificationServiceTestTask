FROM python:3.11-bullseye

WORKDIR /var/www
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN apt update \
    && pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . .

