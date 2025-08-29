# --- Stage 1: Build ---
FROM python:3.11-slim AS build

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and model
COPY . .

# --- Stage 2: Final image ---
FROM python:3.11-slim

WORKDIR /app

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages and app code from build
COPY --from=build /usr/local /usr/local
COPY --from=build /app /app

# Expose port
EXPOSE 5000

# Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]