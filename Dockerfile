FROM python:3.11-buster

ENV PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . /app


