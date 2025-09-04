# --- Stage 1: Build ---
FROM python:3.11-slim AS build

WORKDIR /app

# Install dependencies for build
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        tar \
        gzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and model parts
COPY . .

# Rebuild the tar.gz and extract model
RUN cat /app/model/archive_part.tar.gz* > /app/model/archive_full.tar.gz \
    && tar -xzf /app/model/archive_full.tar.gz -C /app/model \
    && rm /app/model/archive_full.tar.gz /app/model/archive_part.tar.gz*

# --- Stage 2: Final image ---
FROM python:3.11-slim

WORKDIR /app

# Runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy python env and app
COPY --from=build /usr/local /usr/local
COPY --from=build /app /app

EXPOSE 5000

# Start API with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
