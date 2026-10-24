// Pide los datos a la API cada 5 s y los dibuja. Sin librerías: se lee completo.
const tarjetas = document.getElementById("tarjetas");
const selector = document.getElementById("estacion");
const ctx = document.getElementById("grafico").getContext("2d");

async function pedir(url) { return (await fetch(url)).json(); }

let filas = [], llegaron = Date.now();  // últimos datos y el momento en que llegaron al navegador

async function pedirUltimas() {
  filas = await pedir("/api/ultimas");
  llegaron = Date.now();
  pintar();
}

// Cada segundo: la edad que dijo el servidor + lo que pasó desde entonces. EN VIVO si alguna lectura tiene < 15 s.
function pintar() {
  const extra = (Date.now() - llegaron) / 1000;
  const edades = filas.map(f => f.edad_s + extra);
  tarjetas.innerHTML = filas.map((f, i) => `<div class="tarjeta"><b>Estación ${f.estacion}</b><br>
    Humedad ${f.humedad_suelo_pct} %<br>Temp ${f.temp_c} °C<br>ET0 ${f.et0_mm_dia} mm/día<br>
    <small>actualizado hace ${Math.round(edades[i])} s</small></div>`).join("");
  const vivo = edades.length > 0 && Math.min(...edades) < 15;
  document.getElementById("vivo").textContent = vivo ? "EN VIVO" : "SIN DATOS";
  document.getElementById("vivo").className = vivo ? "si" : "no";
}

async function dibujarGrafico() {
  const serie = await pedir("/api/serie?estacion=" + selector.value);
  ctx.clearRect(0, 0, 1000, 300);
  // El eje Y va de 0 a 100 %: 300 px de alto, 2.8 px por punto porcentual.
  ctx.strokeStyle = "#ccc"; ctx.fillStyle = "#555";
  for (const v of [0, 25, 50, 75, 100]) {
    const y = 290 - v * 2.8;
    ctx.beginPath(); ctx.moveTo(30, y); ctx.lineTo(1000, y); ctx.stroke();
    ctx.fillText(v, 2, y);
  }
  ctx.strokeStyle = "#1565c0"; ctx.beginPath();
  serie.forEach((p, i) => {
    const x = 30 + i * 970 / Math.max(serie.length - 1, 1);
    const y = 290 - p.humedad_suelo_pct * 2.8;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  });
  ctx.stroke();
}

function refrescar() { if (document.hidden) return; pedirUltimas(); dibujarGrafico(); }  // pestaña oculta: no consultar
selector.onchange = dibujarGrafico;
refrescar();
setInterval(refrescar, 5000);  // el ESP32 publica cada 5 s: consultar más seguido no trae datos nuevos
setInterval(pintar, 1000);
pedir("/api/version").then(d => document.getElementById("ver").textContent = "v" + d.version);  // pie: versión
