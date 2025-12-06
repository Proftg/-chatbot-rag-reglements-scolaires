# Dockerfile pour School Assistant APM
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="taharguenfoud@gmail.com"
LABEL description="Assistant RAG pour règlements scolaires APM"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Brussels

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    poppler-utils \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -m -u 1000 -s /bin/bash appuser

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer Playwright et les navigateurs
RUN pip install --no-cache-dir playwright && \
    playwright install chromium && \
    playwright install-deps

# Copier le code de l'application
COPY --chown=appuser:appuser . .

# Créer les dossiers nécessaires
RUN mkdir -p logs data school_assistant/data school_assistant/auth/state && \
    chown -R appuser:appuser logs data school_assistant/data school_assistant/auth/state

# Passer à l'utilisateur non-root
USER appuser

# Exposer le port Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Commande par défaut : interface Streamlit
CMD ["streamlit", "run", "school_assistant/interface/app.py", "--server.address", "0.0.0.0"]
