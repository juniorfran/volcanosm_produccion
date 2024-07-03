# Usar una imagen base oficial de Python basada en Debian Bullseye
FROM python:3.9-slim-bullseye

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los requisitos del archivo requirements.txt
COPY requirements.txt .

# Instalar las dependencias necesarias para mysqlclient y pkg-config
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc pkg-config libmariadb-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
RUN pip install --upgrade pip

# Instalar los requisitos de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación en el contenedor
COPY . .

# Exponer el puerto en el que la aplicación estará corriendo
EXPOSE 8000

# Comando para correr la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
