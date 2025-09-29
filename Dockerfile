# Imagen base
FROM python:3.9-slim-bullseye

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc pkg-config libmariadb-dev python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copiar el código fuente
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando por defecto: gunicorn
CMD ["gunicorn", "volcanosm.wsgi:application", "--bind", "0.0.0.0:8000"]
