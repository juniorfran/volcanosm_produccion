# Usar una imagen base oficial de Python basada en Debian Bullseye
FROM python:3.9-slim-bullseye

# Establecer el directorio de trabajo
WORKDIR /app

# Actualizar apt-get e instalar apt-utils
RUN apt-get update && \
    apt-get install -y apt-utils && \
    apt-get install -y --no-install-recommends gcc pkg-config libmariadb-dev python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar los requisitos del archivo requirements.txt
COPY requirements.txt .

# Instalar los requisitos de Python
RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación en el contenedor
COPY . .

# Ejecutar el comando collectstatic durante la construcción
RUN python3 manage.py collectstatic --noinput
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate


# Exponer el puerto en el que la aplicación estará corriendo
EXPOSE 8000

# Comando para correr la aplicación
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
