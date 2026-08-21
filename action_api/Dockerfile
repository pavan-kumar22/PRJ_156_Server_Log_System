FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn

COPY action_api /app/action_api

RUN mkdir -p /var/log/aicte

EXPOSE 8002

CMD ["uvicorn", "action_api.main:app", "--host", "0.0.0.0", "--port", "8002"]