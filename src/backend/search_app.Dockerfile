FROM python:3.8.12-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV FLASK_APP=/app/search_app.py

COPY search_app.py .
ARG config_file
COPY $config_file /config/search_app_config.json

EXPOSE 8880

ENTRYPOINT gunicorn --preload --bind 0.0.0.0:8880 --workers 4 --threads 4 --timeout=600 search_app:app
