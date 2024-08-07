# Usar una imagen base oficial de Python basada en Debian Bullseye
FROM python:3.9-slim-bullseye

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los requisitos del archivo requirements.txt
COPY requirements.txt .

# Instalar las dependencias necesarias para mysqlclient y pkg-config
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc pkg-config libmariadb-dev git curl gnupg && \
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | apt-key add - && \
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list && \
    apt-get update && \
    apt-get install -y caddy && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar pip y los requisitos de Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación en el contenedor
COPY . .

# Exponer el puerto en el que la aplicación estará corriendo
EXPOSE 8000

# Comando para correr la aplicación
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]
