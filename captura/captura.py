"""Escucha al ESP32 por MQTT y guarda cada lectura en PostgreSQL.
Corre en la laptop (donde está el broker). El dashboard en la nube solo lee la base."""
import json, os
import paho.mqtt.client as mqtt
import psycopg
import alertas

# Una sola conexión abierta: son pocos mensajes (4 cada 5 s).
db = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)

def al_conectar(cliente, datos, flags, rc, props=None):
    # Se suscribe aquí (no antes) para que se repita si el broker se reinicia.
    cliente.subscribe("estaciones/+/datos")

def al_llegar(cliente, datos, msg):
    try:
        d = json.loads(msg.payload)
        # Validación mínima; los CHECK de schema.sql son la segunda barrera.
        db.execute(
            "INSERT INTO lecturas (estacion, humedad_suelo_pct, temp_c, et0_mm_dia, evento) VALUES (%s,%s,%s,%s,%s)",
            (d["estacion"], d["humedad_suelo_pct"], d["temp_c"], d["et0_mm_dia"], bool(d.get("evento"))))
        print("guardada estacion", d["estacion"])
        alertas.revisar(d)  # después de guardar: si el correo falla, el dato ya está a salvo
    except Exception as e:  # un mensaje malo se descarta y se sigue
        print("descartada:", e)
        db.rollback()

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_connect = al_conectar
cliente.on_message = al_llegar
cliente.connect(os.getenv("MQTT_HOST", "localhost"), 1883)
cliente.loop_forever()  # bloquea y reconecta solo
