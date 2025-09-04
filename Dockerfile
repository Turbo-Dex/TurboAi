# Dockerfile.gpu
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    WORKDIR=/workspace

# Install system dependencies (OpenCV needs libgl1 + libglib2.0-0)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev build-essential git wget ca-certificates unzip \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3 /usr/bin/python

# Copy requirements (contains torch, ultralytics, jupyter, etc.)
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Create workspace
WORKDIR /workspace
VOLUME ["/workspace"]

# Expose Jupyter
EXPOSE 8888

# Create non-root user
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g ${GROUP_ID} developer || true \
 && useradd -m -u ${USER_ID} -g ${GROUP_ID} developer || true \
 && chown -R developer:developer /workspace
USER developer

# Start Jupyter
CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=$JUPYTER_TOKEN --NotebookApp.notebook_dir=/workspace"]
