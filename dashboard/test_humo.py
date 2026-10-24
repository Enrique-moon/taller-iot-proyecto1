"""Test de humo: ¿arranca el dashboard y responde? Lo corre el CI antes de desplegar."""
from fastapi.testclient import TestClient
from main import app

cliente = TestClient(app)

def test_health():
    assert cliente.get("/health").json() == {"ok": True}

def test_ultimas_es_lista():
    r = cliente.get("/api/ultimas")
    assert r.status_code == 200 and isinstance(r.json(), list)

def test_version_es_semver():
    v = cliente.get("/api/version").json()["version"]
    assert len(v.split(".")) == 3 and all(n.isdigit() for n in v.split("."))
