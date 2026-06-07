#!/usr/bin/env bash
#
# Sincroniza la base remota (fuente de verdad) -> mirror local (MariaDB en
# docker) usando el cliente mariadb del propio contenedor db_local.
# Pensado para cron en el VPS, p.ej. cada 30 min:
#
#   */30 * * * * . /home/administrator/volcanosm_produccion/.env.sync && \
#       /home/administrator/volcanosm_produccion/scripts/sync_db.sh >> /var/log/volcanosm_sync.log 2>&1
#
# Las contraseñas se leen de variables de entorno (ver .env.sync); NO escribir aquí.
set -euo pipefail

REMOTE_HOST="${REMOTE_DB_HOST:-www.metrocuadrado.com.sv}"
REMOTE_DB="${REMOTE_DB_NAME:-cuadmesv_tour}"
REMOTE_USER="${REMOTE_DB_USER:-cuadmesv_tour}"
REMOTE_PWD="${REMOTE_DB_PASSWORD:?Define REMOTE_DB_PASSWORD}"

CONTAINER="${LOCAL_DB_CONTAINER:-volcanosm_db_local}"
LOCAL_DB="${LOCAL_DB_NAME:-cuadmesv_tour}"
LOCAL_ROOT_PWD="${LOCAL_DB_ROOT_PASSWORD:?Define LOCAL_DB_ROOT_PASSWORD}"

DUMP="$(mktemp /tmp/volcanosm_sync_XXXXXX.sql)"
trap 'rm -f "$DUMP"' EXIT

# Dump de la remota usando el cliente del contenedor (MariaDB 11.4).
docker exec -e MYSQL_PWD="$REMOTE_PWD" "$CONTAINER" \
  mariadb-dump --single-transaction --quick --no-tablespaces \
  -h "$REMOTE_HOST" -u "$REMOTE_USER" "$REMOTE_DB" > "$DUMP"

SIZE=$(wc -c < "$DUMP")
if [ "$SIZE" -lt 1024 ]; then
  echo "[sync $(date -u +%FT%TZ)] ERROR: dump vacio ($SIZE bytes), se conserva la copia previa"
  exit 1
fi

# Import al mirror local (el dump trae DROP TABLE IF EXISTS, reemplaza limpio).
docker exec -i -e MYSQL_PWD="$LOCAL_ROOT_PWD" "$CONTAINER" \
  mariadb -u root "$LOCAL_DB" < "$DUMP"

echo "[sync $(date -u +%FT%TZ)] OK ($SIZE bytes)"
