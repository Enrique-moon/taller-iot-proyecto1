"""API del dashboard: tres rutas. La página vive en public/ (index.html y app.js)."""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import db

app = FastAPI()

@app.get("/health")  # el test de humo preguntan aquí si el servicio vive
def health():
    return {"ok": True}

@app.get("/api/ultimas")
def ultimas():
    return db.ultimas()  # FastAPI convierte fechas y números a JSON solo

@app.get("/api/serie")
def serie(estacion: int = 1):
    return db.serie(estacion)

# La versión (SemVer) vive en un solo archivo, dashboard/VERSION. Al publicar una versión nueva solo se edita ese archivo.
@app.get("/api/version")
def version():
    return {"version": (Path(__file__).parent / "VERSION").read_text().strip()}

# Solo en local: en Vercel public/ lo sirve la plataforma (el doc pide no montarla) y VERCEL=1 está definido.
# Va al final para no tapar /api. html=True sirve index.html en "/".
if not os.getenv("VERCEL"):
    app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "public"), html=True))
