-- Se aplica UNA vez:  psql "$DATABASE_URL" -f schema.sql
CREATE TABLE IF NOT EXISTS lecturas (
    id                serial PRIMARY KEY,                              -- número único de cada fila
    estacion          int  NOT NULL CHECK (estacion BETWEEN 1 AND 4),  -- cuál de las 4 estaciones
    ts                timestamptz NOT NULL DEFAULT now(),              -- cuándo llegó la lectura (lo pone la base)
    humedad_suelo_pct real NOT NULL CHECK (humedad_suelo_pct BETWEEN 0 AND 100),  -- % de humedad del suelo
    temp_c            real NOT NULL CHECK (temp_c BETWEEN -20 AND 60),            -- temperatura en °C
    et0_mm_dia        real NOT NULL CHECK (et0_mm_dia BETWEEN 0 AND 20),          -- evapotranspiración, mm/día
    evento            boolean NOT NULL DEFAULT false                   -- true mientras dura el evento simulado
);
-- Las consultas piden "las últimas de una estación": este índice las hace rápidas.
CREATE INDEX IF NOT EXISTS lecturas_estacion_ts ON lecturas (estacion, ts DESC);
