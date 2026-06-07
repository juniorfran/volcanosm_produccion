"""Router de failover de base de datos.

Estrategia: la DB remota (`default`) es la fuente de verdad. Cuando está
inalcanzable, las LECTURAS se sirven desde la réplica local (`replica`), un
MySQL local sincronizado periódicamente. Las ESCRITURAS siempre van a
`default` (y fallarán de forma controlada durante una caída de la remota, en
vez de colgar el sitio).

El estado de salud de la remota se cachea unos segundos por worker para no
intentar una conexión TCP en cada request.

Se activa solo si DATABASE_ROUTERS lo incluye (ver settings.py, gated por la
variable de entorno DB_FAILOVER_ENABLED).
"""

import socket
import time

from django.conf import settings


class FailoverRouter:
    # Estado compartido por proceso (cada worker de gunicorn tiene el suyo).
    _alive = True
    _checked_at = 0.0
    _ttl_seconds = 10.0
    _probe_timeout = 3.0

    def _remote_alive(self):
        now = time.monotonic()
        if now - FailoverRouter._checked_at < FailoverRouter._ttl_seconds:
            return FailoverRouter._alive

        db = settings.DATABASES.get("default", {})
        host = db.get("HOST")
        port = db.get("PORT") or 3306
        try:
            with socket.create_connection((host, int(port)), timeout=self._probe_timeout):
                FailoverRouter._alive = True
        except (OSError, ValueError):
            FailoverRouter._alive = False
        FailoverRouter._checked_at = now
        return FailoverRouter._alive

    def db_for_read(self, model, **hints):
        # Si la réplica no está configurada, nunca desviamos (fail-safe).
        if "replica" not in settings.DATABASES:
            return "default"
        return "default" if self._remote_alive() else "replica"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Las migraciones solo se aplican sobre la DB principal.
        return db == "default"
