FROM python:3.11.0a1-slim

RUN useradd -ms /bin/bash user

USER user

ENV PATH="/home/user/.local/bin:${PATH}"

WORKDIR /home/user/app

COPY . /home/user/app/
COPY requirements.txt /home/user/app/

RUN pip install -r requirements.txt







