# Stage 1: Build
FROM python:3.11-slim AS build

WORKDIR /app

# Install only build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install the rest of the requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Final image
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from build stage
COPY --from=build /usr/local /usr/local
COPY --from=build /app /app

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]
