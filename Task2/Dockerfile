# syntax=docker/dockerfile:1
FROM python:3.14-slim

WORKDIR /app

COPY app.py /app/app.py

RUN pip install --no-cache-dir prometheus-client

EXPOSE 8080

CMD ["python", "app.py"]

