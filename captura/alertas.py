"""Manda un correo cuando una lectura pasa un umbral. Corre en la laptop, junto a captura.py."""
import os, smtplib, time
from email.message import EmailMessage

# Umbrales fijos: por debajo de 20 % de humedad la planta ya sufre; sobre 35 °C y 6 mm/día se seca el suelo.
UMBRALES = [("humedad_suelo_pct", lambda v: v < 20, "humedad baja (< 20 %)"),
            ("temp_c",            lambda v: v > 35, "temperatura alta (> 35 °C)"),
            ("et0_mm_dia",        lambda v: v > 6,  "ET0 alta (> 6 mm/día)")]
USER, CLAVE = os.getenv("SMTP_USER"), os.getenv("SMTP_PASS")
DESTINOS = [c.strip() for c in os.getenv("ALERT_TO", "").split(",") if c.strip()]  # agregar a alguien = añadir a la lista
# Gmail por 465 con SSL: es la forma más corta (conecta ya cifrado, sin STARTTLS). SMTP_HOST/PORT solo sirven para probar.
HOST, PUERTO = os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", "465"))
COOLDOWN = 600  # segundos: sin esto llegaría un correo cada 5 s mientras dure la sequía
ultimo = {}     # estación -> momento del último correo

ACTIVAS = bool(USER and CLAVE and DESTINOS)
if not ACTIVAS:
    print("Alertas por correo APAGADAS (faltan SMTP_USER, SMTP_PASS o ALERT_TO)")

def revisar(d):
    motivos = [txt for campo, malo, txt in UMBRALES if malo(d[campo])]
    if not (ACTIVAS and motivos) or time.time() - ultimo.get(d["estacion"], 0) < COOLDOWN:
        return
    ultimo[d["estacion"]] = time.time()
    m = EmailMessage()
    m["Subject"], m["From"], m["To"] = f"ALERTA estación {d['estacion']}: {', '.join(motivos)}", USER, ", ".join(DESTINOS)
    m.set_content(f"Estación {d['estacion']} a las {time.strftime('%H:%M:%S')}\nMotivo: {', '.join(motivos)}\n"
                  f"Humedad {d['humedad_suelo_pct']} %, temp {d['temp_c']} °C, ET0 {d['et0_mm_dia']} mm/día")
    try:
        with (smtplib.SMTP_SSL if PUERTO == 465 else smtplib.SMTP)(HOST, PUERTO, timeout=10) as s:
            if PUERTO == 465:
                s.login(USER, CLAVE)
            s.send_message(m)
    except Exception as e:  # un fallo de correo nunca debe detener la captura
        print("aviso: no se pudo enviar el correo:", e)
