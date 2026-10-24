# Registro de cambios

Todos los cambios importantes del proyecto se anotan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [0.1.0] - 2026-10-24

### Añadido
- Simulador ESP32 con 4 estaciones que publican por MQTT cada 5 s.
- Captura MQTT hacia PostgreSQL (Neon) y alertas por correo.
- Dashboard FastAPI con tarjetas en vivo y gráfico de humedad.
- Endpoint `GET /api/version` y número de versión en el pie de la página.
- Pruebas con pytest y flujo de GitHub Actions.
