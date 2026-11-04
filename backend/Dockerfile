FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend"

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies from backend folder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source trees
COPY backend/ /app/backend/
COPY ml/ /app/ml/

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]