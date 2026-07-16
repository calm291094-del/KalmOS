FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Crear directorios necesarios
RUN mkdir -p kalm_data D system/program views static

# Exponer puertos
EXPOSE 8080 5353 8888

# Comando de inicio
CMD ["python", "kalm.py"]