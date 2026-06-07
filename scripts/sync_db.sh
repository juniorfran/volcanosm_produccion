#!/usr/bin/env bash
#
# Sincroniza la base de datos remota (fuente de verdad) hacia el MySQL local
# de respaldo. Pensado para correr por cron en el VPS, p.ej. cada 15 minutos:
#
#   */15 * * * * REMOTE_DB_PASSWORD=... LOCAL_DB_ROOT_PASSWORD=... \
#       /home/administrator/volcanosm_produccion/scripts/sync_db.sh >> /var/log/volcanosm_sync.log 2>&1
#
# Requiere que la remota sea ALCANZABLE (IP del VPS en el whitelist del hosting)
# y el cliente mysql/mysqldump instalado en el host (o usar el del contenedor).
#
# Las contraseñas se leen de variables de entorno; NO las escribas aquí.

set -euo pipefail

# ---- Origen (remoto, fuente de verdad) --------------------------------------
REMOTE_HOST="${REMOTE_DB_HOST:-www.metrocuadrado.com.sv}"
REMOTE_PORT="${REMOTE_DB_PORT:-3306}"
REMOTE_DB="${REMOTE_DB_NAME:-cuadmesv_tour}"
REMOTE_USER="${REMOTE_DB_USER:-cuadmesv_tour}"
REMOTE_PASS="${REMOTE_DB_PASSWORD:?Define REMOTE_DB_PASSWORD}"

# ---- Destino (MySQL local en docker) ----------------------------------------
LOCAL_CONTAINER="${LOCAL_DB_CONTAINER:-volcanosm_db_local}"
LOCAL_DB="${LOCAL_DB_NAME:-cuadmesv_tour}"
LOCAL_ROOT_PASS="${LOCAL_DB_ROOT_PASSWORD:?Define LOCAL_DB_ROOT_PASSWORD}"

DUMP="$(mktemp /tmp/volcanosm_sync_XXXXXX.sql)"
trap 'rm -f "$DUMP"' EXIT

echo "[sync $(date -u +%FT%TZ)] Verificando alcance de la remota..."
if ! timeout 8 bash -c "cat < /dev/null > /dev/tcp/${REMOTE_HOST}/${REMOTE_PORT}" 2>/dev/null; then
  echo "[sync] ERROR: remota ${REMOTE_HOST}:${REMOTE_PORT} inalcanzable. Abortando (se conserva la copia local previa)."
  exit 1
fi

echo "[sync] Dump de ${REMOTE_DB}@${REMOTE_HOST}..."
mysqldump \
  --single-transaction --quick --no-tablespaces --skip-lock-tables \
  --set-gtid-purged=OFF --column-statistics=0 \
  -h "$REMOTE_HOST" -P "$REMOTE_PORT" -u "$REMOTE_USER" -p"$REMOTE_PASS" \
  "$REMOTE_DB" > "$DUMP" 2>/dev/null \
  || mysqldump --single-transaction --quick --no-tablespaces --skip-lock-tables \
       -h "$REMOTE_HOST" -P "$REMOTE_PORT" -u "$REMOTE_USER" -p"$REMOTE_PASS" \
       "$REMOTE_DB" > "$DUMP"

SIZE=$(wc -c < "$DUMP")
if [ "$SIZE" -lt 1024 ]; then
  echo "[sync] ERROR: el dump parece vacío (${SIZE} bytes). Abortando para no corromper la copia local."
  exit 1
fi

echo "[sync] Importando ${SIZE} bytes a ${LOCAL_CONTAINER}/${LOCAL_DB}..."
docker exec -i "$LOCAL_CONTAINER" \
  sh -c "exec mysql -uroot -p\"$LOCAL_ROOT_PASS\" \"$LOCAL_DB\"" < "$DUMP"

echo "[sync $(date -u +%FT%TZ)] OK"
