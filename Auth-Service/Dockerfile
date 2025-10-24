FROM python:3.12-slim

WORKDIR /app

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

