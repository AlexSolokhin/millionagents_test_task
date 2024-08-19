FROM python:3.11.1-slim AS base

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y gettext

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install cleo urllib3 charset-normalizer
RUN pip install -r requirements.txt

COPY . .
