# Usar una imagen base oficial de Python basada en Debian Bullseye
FROM python:3.9-slim-bullseye

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los requisitos del archivo requirements.txt y luego instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar las dependencias necesarias para mysqlclient
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc pkg-config libmariadb-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar el código fuente de la aplicación en el contenedor
COPY . .

# Exponer el puerto en el que la aplicación estará corriendo
EXPOSE 8000

# Comando para correr la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
