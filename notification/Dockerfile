FROM python:3.11-slim

WORKDIR /app

COPY notification /app/notification

RUN pip install --no-cache-dir fastapi uvicorn requests

EXPOSE 8001

CMD ["uvicorn", "notification.main:app", "--host", "0.0.0.0", "--port", "8001"]