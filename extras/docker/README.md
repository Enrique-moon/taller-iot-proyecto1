# Docker (opcional)

**Vercel NO usa este Dockerfile.** Vercel construye `dashboard/` por su cuenta. Esto sirve para aprender y para llevar el dashboard a cualquier máquina con Docker.

## Tres palabras
- **Imagen**: el paquete cerrado con Python, las librerías y tu código. Como una receta ya cocinada y congelada.
- **Contenedor**: una imagen en marcha. De una imagen salen todos los contenedores que quieras.
- **Capa**: cada línea del Dockerfile que cambia archivos crea una capa. Docker guarda las capas y reutiliza las que no cambiaron, por eso el orden importa.

## El Dockerfile, línea por línea
- `FROM python:3.12-slim`: parte de una imagen con Python 3.12 y poco más (liviana).
- `WORKDIR /app`: la carpeta de trabajo dentro de la imagen.
- `COPY requirements.txt .` y `RUN pip install ...`: instala las librerías antes de copiar el código. Si solo cambias código, esta capa se reutiliza y el build es rápido.
- `COPY . .`: copia el contenido de `dashboard/` (el contexto), menos lo que diga `Dockerfile.dockerignore`.
- `RUN useradd ...` y `USER app`: el programa corre sin ser root; si alguien lo vulnera, tiene menos poder.
- `ENV PORT=8000`: puerto por defecto; se puede cambiar con `-e PORT=...`.
- `CMD [...]`: lo que se ejecuta al arrancar. Usa `sh -c` para que `$PORT` se expanda.

## Construir y correr (desde `proyecto1/`)
```
docker build -t taller-dashboard:0.1.0 -f extras/docker/Dockerfile dashboard
docker run --rm -p 18095:8000 -e DATABASE_URL="..." taller-dashboard:0.1.0
curl localhost:18095/health
```
Con Postgres local sin SSL agrega `-e PGSSLMODE=disable`. Con una `.env`: `--env-file .env`.

## Versión de la imagen
El tag de la imagen es la versión SemVer de `dashboard/VERSION`:
`docker tag taller-dashboard:0.1.0 taller-dashboard:latest`
Al subir a 0.2.0 se construye `taller-dashboard:0.2.0`. Así sabes qué código corre cada contenedor.
