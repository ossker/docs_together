FROM python:3.12-slim

WORKDIR /app

COPY docs_together/ /app/

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

