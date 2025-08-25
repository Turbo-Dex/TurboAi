# Dockerfile (CPU)
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    WORKDIR=/workspace

# dépendances système utiles
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates wget unzip \
    && rm -rf /var/lib/apt/lists/*

# copie fichiers package (facultatif) et install pip packages
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# crée dossier de travail
WORKDIR /workspace
VOLUME ["/workspace"]

# Jupyter config (expose 8888)
EXPOSE 8888

# utilisateur non-root (optionnel pour éviter soucis de permission)
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g ${GROUP_ID} developer || true \
 && useradd -m -u ${USER_ID} -g ${GROUP_ID} developer || true \
 && chown -R developer:developer /workspace
USER developer

# commande de démarrage par défaut
CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=$JUPYTER_TOKEN --NotebookApp.notebook_dir=/workspace"]
