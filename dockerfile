# Production Dockerfile
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# system deps required for building some Python packages (adjust as needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential gcc libpq-dev ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# copy only requirements first for better caching
COPY requirements.txt /app/requirements.txt

# install python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy project
COPY . /app

# ensure env vars are available at runtime (use real secrets via env in production)
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Use uvicorn to run the FastAPI app (main:app assumes main.py exports app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
