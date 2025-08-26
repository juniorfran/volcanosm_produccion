# Dockerfile (prod)
FROM python:3.9-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Paquetes de sistema (compilar mysqlclient/mariadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config libmariadb-dev python3-dev \
 && rm -rf /var/lib/apt/lists/*

# Requisitos primero (mejor caché)
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn

# Copiar código
COPY . /app/

# Usuario no root (opcional)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# IMPORTANTE: no hacer migrate/collectstatic en build
# Hágalo al arrancar el contenedor (ver compose).
# Reemplace alpiedelvolcan_.wsgi si su paquete Django tiene otro nombre.
CMD bash -lc "\
  python manage.py migrate --noinput && \
  python manage.py collectstatic --noinput && \
  gunicorn alpiedelvolcan_.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 \
"
