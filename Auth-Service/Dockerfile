FROM python:3.12-slim

WORKDIR /app

# Build arguments para versionamiento
ARG VERSION=1.0.0-dev
ARG BUILD_DATE=unknown
ARG COMMIT_HASH=unknown

# Variables de entorno para la aplicación
ENV VERSION=${VERSION}
ENV BUILD_DATE=${BUILD_DATE}
ENV COMMIT_HASH=${COMMIT_HASH}
ENV ENVIRONMENT=production

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente y configuración
COPY src/ ./src/
COPY config/ ./config/

# Exponer puerto
EXPOSE 5004

# Comando para ejecutar la aplicación
CMD ["python", "src/main.py"]

