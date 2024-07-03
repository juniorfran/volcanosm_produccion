# Usa una imagen base oficial de Python
FROM python:3.7.3

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias necesarias para mysqlclient
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc pkg-config libmariadb-dev

# Copia los archivos de requerimientos y los instala
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copia el contenido de tu aplicación en el directorio de trabajo
COPY . .

# Expone el puerto en el que la aplicación correrá
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
