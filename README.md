# Proyecto 1: del ESP32 a un dashboard en internet

```
ESP32 -> broker MQTT (laptop) -> captura.py (laptop) -> PostgreSQL en Neon <- dashboard en Vercel
                                                          código en GitHub -> Actions (pruebas) y Vercel (despliegue)
```

| Pieza | Qué hace |
|---|---|
| `esp32/esp32.ino` | Simula 4 estaciones y publica su JSON cada 5 s en `estaciones/N/datos`. |
| `mosquitto.conf` | Configuración del broker MQTT. |
| `schema.sql` | Crea la tabla `lecturas`. Se aplica una vez. |
| `captura/` | `captura.py` guarda cada mensaje MQTT en la base; `alertas.py` manda correos. Corren en la laptop. |
| `dashboard/` | FastAPI (`main.py`, `db.py`) + página en `public/`. Solo LEE la base. Es lo que se despliega. |
| `docker-compose.yml` | PostgreSQL de práctica en local (puerto 55433). |
| `.github/workflows/test.yml` | GitHub Actions: levanta Postgres y corre pytest en cada push y pull request. |

## Probarlo todo en local (sin cuentas)

1. `docker compose up -d` y `export DATABASE_URL=postgresql://iot:iot@127.0.0.1:55433/iot PGSSLMODE=disable`
2. `psql "$DATABASE_URL" -f schema.sql`
3. `python -m venv .venv && . .venv/bin/activate && pip install -r captura/requirements.txt -r dashboard/requirements.txt pytest httpx`
4. `mosquitto -c mosquitto.conf`, carga el ESP32 y en otra terminal `MQTT_HOST=127.0.0.1 python captura/captura.py`
5. `cd dashboard && uvicorn main:app --port 8030` y abre http://localhost:8030
6. Pruebas: `cd dashboard && pytest -q` y `cd captura && pytest -q`.

(`PGSSLMODE=disable` solo es para el Postgres local, que no tiene SSL. En Neon no lo definas: `db.py` usa `sslmode=require`.)

## Paso a paso en la nube

**1. Base en Neon.** neon.tech > Sign up > Create project (región cercana). En el panel pulsa **Connect**, activa
**Connection pooling** y copia la cadena: el host debe llevar `-pooler` (`...-pooler.<región>.aws.neon.tech`) y terminar en `?sslmode=require`.
Usamos la cadena pooled porque cada petición del dashboard abre una conexión corta (no hay pool propio) y Neon las reparte.

**2. Crear la tabla.** `psql "CADENA_DE_NEON" -f schema.sql`

**3. Captura en la laptop, escribiendo a Neon.**
`env DATABASE_URL="CADENA_DE_NEON" MQTT_HOST=127.0.0.1 python captura/captura.py`. El ESP32 y el broker siguen en tu red.

**4. Repositorio en GitHub.** Crea uno vacío en github.com > New repository (sin README). `proyecto1/` es SU propio repositorio:
```
cd proyecto1
git init -b main
git add . && git commit -m "Proyecto 1"
git remote add origin https://github.com/TU_USUARIO/proyecto1.git
git push -u origin main
```
`.gitignore` ya excluye `.env`: no subas claves. Tras el push, la pestaña **Actions** muestra las pruebas (verde = pasaron, rojo = fallaron; entra al run para ver el detalle).

**5. Desplegar en Vercel.** vercel.com > Sign up con GitHub > **Add New > Project > Import Git Repository** > elige `proyecto1`.
- **Root Directory = `dashboard`** (Edit junto al campo).
- **Environment Variables:** `DATABASE_URL` = la cadena pooled de Neon.
- **Deploy.** Al terminar, Vercel muestra la URL (`https://proyecto1-xxxx.vercel.app`).

**6. Redespliegue.** Cada `git push` a `main` crea un despliegue nuevo y lo publica solo. Otras ramas y pull requests generan despliegues de prueba con URL propia.

**7. Logs.** En Vercel: proyecto > **Logs** (o Deployments > el despliegue > Logs). Aquí salen los errores de `/api/...`.

## Cómo está armado para Vercel (según la documentación oficial)

- Vercel busca la instancia `app` en `app.py`, `index.py`, `server.py` o `main.py` (también en `src/` o `app/`): `dashboard/main.py` ya cumple, no se renombró.
- Python: 3.12 por defecto (también 3.13 y 3.14). Dependencias en `requirements.txt`.
- Estáticos: `public/` en la raíz del proyecto de Vercel (aquí `dashboard/public/`), servidos por la CDN. El doc pide NO montarla con `app.mount()`.
  Por eso `main.py` solo monta `StaticFiles` si no existe la variable `VERCEL`: es únicamente para que `uvicorn` sirva la página en local.
- No hay `vercel.json`. El doc que leí no dice explícitamente que `public/index.html` se sirva en `/`: **verificar** en el primer despliegue.
  Si `/` diera 404, lo mínimo sería añadir una ruta `/` en `main.py` que devuelva ese archivo. Este despliegue no se probó.

## Notas honestas

- El despliegue de Vercel NO espera a las pruebas de GitHub Actions: publica en cuanto hay push. Existe "Deployment Checks" (Settings del proyecto) para retener producción hasta que pasen, pero es opcional y no lo configuramos. Un test en rojo no frena el despliegue.
- Plan gratis "Hobby": solo uso personal y no comercial. Cifras que vi en la documentación (**verificar** en vercel.com/docs/limits y /pricing, cambian): hasta 300 s por función en Hobby (no los 10 s que se recordaban), 1 millón de invocaciones al mes, 4 h de CPU activa.
  El dashboard hace 2 peticiones cada 2 s por pestaña abierta: una pestaña 24 h al día gasta ~2,6 millones al mes. Ciérralas al terminar.
- No pude comprobar si Vercel pide tarjeta al registrarse; Neon tampoco lo verifiqué. Sin promesas de gratuidad: revisa los planes vigentes.
- Neon suspende la base tras un rato sin uso: la primera petición puede tardar un par de segundos (**verificar**).
- NO PROBADO: Vercel, Neon, GitHub Actions y la integración entre ellos. Sí se probó en local: pytest, uvicorn y la página con datos reales.

## Alertas por correo

`captura/alertas.py` manda un correo si humedad < 20 %, temp > 35 °C o ET0 > 6 mm/día, máximo uno cada 10 min por estación.
Corre en la laptop junto a `captura.py`; Vercel NO envía correos. Sin las tres variables, las alertas quedan apagadas y lo avisa al arrancar.

1. Cuenta Google > Seguridad > Verificación en 2 pasos > Contraseñas de aplicaciones > crea una y cópiala.
2. Variables antes de arrancar (fish): `set -x SMTP_USER tucorreo@gmail.com`, `set -x SMTP_PASS la_clave`, `set -x ALERT_TO a@x.com,b@y.com`.
3. Para cambiar destinatarios, edita `ALERT_TO` (separada por comas) y reinicia `captura.py`.
4. Prueba sin correos reales: `cd captura && pytest test_alertas.py` (SMTP falso local).

## Cómo cambiar de WiFi/IP

Arriba de `esp32.ino`, en CONFIGURA AQUÍ: `WIFI_SSID`, `WIFI_PASS` y `MQTT_HOST` (la IP de la laptop, `ip a`). Vuelve a cargar el ESP32.

## Tiempo real, con honestidad

El ESP32 publica cada ~5 s y el navegador consulta cada 2 s: una lectura se ve 5-7 s después. No es push (sin WebSocket ni SSE).
El dashboard pasa de EN VIVO a SIN DATOS si no llega nada nuevo en 15 s (con la laptop apagada, verás SIN DATOS pero los últimos valores).
