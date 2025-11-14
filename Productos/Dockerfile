# Usar Python 3.11 como base
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/

# NOTA: gcp-credentials.json NO se copia aquí porque:
# 1. En CI/CD no está disponible (está en .gitignore)
# 2. En producción (GKE) se usa Workload Identity automáticamente
# 3. El código en servicio_gcp_storage.py maneja la ausencia del archivo
# Si necesitas el archivo para desarrollo local, cópialo manualmente o usa secrets

# Exponer puerto
EXPOSE 5000

# Variables de entorno
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
# GOOGLE_APPLICATION_CREDENTIALS es opcional
# En producción (GKE) se usa Workload Identity automáticamente si no está definido
# El código verifica si el archivo existe antes de usarlo

# Comando para ejecutar la aplicación
CMD ["python", "src/main.py"]
