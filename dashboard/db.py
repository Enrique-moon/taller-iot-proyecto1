"""Acceso a PostgreSQL: solo lectura. Aquí viven las dos consultas del dashboard."""
import os
import psycopg

def consulta(sql, args=()):
    # Conexión corta por petición, sin pool: cada invocación serverless es efímera. Usa la cadena POOLED
    # de Neon (host con -pooler), que reparte las conexiones. SSL siempre; para el Postgres local sin SSL: PGSSLMODE=disable.
    with psycopg.connect(os.environ["DATABASE_URL"], sslmode=os.getenv("PGSSLMODE", "require")) as c:
        cur = c.execute(sql, args)
        cols = [x.name for x in cur.description]
        return [dict(zip(cols, fila)) for fila in cur.fetchall()]

def ultimas():  # la lectura más reciente de cada estación
    # edad_s la calcula la base (now() - ts): así no depende de que el reloj del navegador coincida con el del servidor.
    return consulta("SELECT DISTINCT ON (estacion) *, extract(epoch FROM now() - ts)::float AS edad_s "
                    "FROM lecturas ORDER BY estacion, ts DESC")

def serie(estacion):  # las últimas 60 de una estación, de la más vieja a la más nueva
    return consulta("SELECT ts, humedad_suelo_pct FROM (SELECT * FROM lecturas WHERE estacion=%s "
                    "ORDER BY ts DESC LIMIT 60) t ORDER BY ts", (estacion,))
