FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/ShadyPayServer

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000