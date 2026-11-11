FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Primero las dependencias: esta capa queda en cache mientras requirements.txt no cambie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app

EXPOSE 8000

# Aplica las migraciones y después levanta la API
CMD ["sh", "-c", "alembic upgrade head && fastapi run app/main.py --port 8000"]