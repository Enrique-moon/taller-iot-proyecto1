"""Prueba con un servidor SMTP falso local: no se envía ningún correo real."""
import os, socket, threading
recibidos = []

def smtp_falso(srv):  # responde lo mínimo del protocolo y guarda cada mensaje
    while True:
        c = srv.accept()[0]; f = c.makefile("rw", newline="\r\n"); f.write("220 ok\r\n"); f.flush()
        cuerpo = None
        for linea in f:
            if cuerpo is not None:
                if linea.strip() == ".":
                    recibidos.append("".join(cuerpo)); cuerpo = None; f.write("250 ok\r\n")
                else: cuerpo.append(linea)
            elif linea.upper().startswith("DATA"): cuerpo = []; f.write("354 sigue\r\n")
            elif linea.upper().startswith("QUIT"): f.write("221 adios\r\n"); f.flush(); break
            else: f.write("250 ok\r\n")
            f.flush()
        c.close()

srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen()
threading.Thread(target=smtp_falso, args=(srv,), daemon=True).start()
os.environ.update(SMTP_USER="a@x.com", SMTP_PASS="x", ALERT_TO="u1@x.com, u2@y.com", SMTP_HOST="127.0.0.1", SMTP_PORT=str(srv.getsockname()[1]))
import alertas

normal = dict(estacion=1, humedad_suelo_pct=35, temp_c=22, et0_mm_dia=4.5)
sequia = dict(estacion=3, humedad_suelo_pct=12, temp_c=38, et0_mm_dia=7)

def test_alertas():
    alertas.revisar(normal);  assert recibidos == []                       # lectura normal: nada
    alertas.revisar(sequia);  assert len(recibidos) == 1                   # sequía: un correo
    assert "u1@x.com" in recibidos[0] and "u2@y.com" in recibidos[0]       # a los dos destinatarios
    alertas.revisar(sequia);  assert len(recibidos) == 1                   # repetición: cooldown
    alertas.ultimo.clear(); alertas.PUERTO = 1                             # puerto cerrado: falla el envío
    alertas.revisar(sequia)                                                # no debe lanzar excepción
