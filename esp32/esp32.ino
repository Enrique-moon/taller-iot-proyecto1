#include <WiFi.h>
#include <PubSubClient.h>
// Simula 4 estaciones y publica su JSON por MQTT cada 5 s. La hora la pone la base de datos.

// ===== CONFIGURA AQUÍ =====
#define WIFI_SSID "TU_WIFI"
#define WIFI_PASS "TU_CLAVE"
#define MQTT_HOST "192.168.1.10"   // IP de la laptop con Mosquitto
// ==========================

WiFiClient red;
PubSubClient mqtt(red);
unsigned long ultimoEnvio = 0, ultimoIntento = 0;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  mqtt.setServer(MQTT_HOST, 1883);
}

// Reintenta cada 5 s con millis(): nunca se queda esperando en un while
void conectar() {
  if (millis() - ultimoIntento < 5000) return;
  ultimoIntento = millis();
  if (WiFi.status() != WL_CONNECTED) { Serial.println("Sin WiFi, esperando..."); return; }
  String id = "esp32-" + String((uint32_t)ESP.getEfuseMac(), HEX);
  if (mqtt.connect(id.c_str())) Serial.println("MQTT conectado");
  else Serial.printf("MQTT fallo, rc=%d (-2=no llega al broker, 5=no autorizado)\n", mqtt.state());
}

void publicar(int est) {
  float seg = millis() / 1000.0;
  bool evento = (est == 3 && seg >= 60 && seg < 240);  // calor y sequia 180 s
  float temp = (evento ? 38 : 22) + random(-30, 30) / 10.0;
  float hum  = (evento ? 12 : 35) + random(-40, 40) / 10.0;
  float et0  = constrain(0.25 * temp - 1.0 + random(-3, 3) / 10.0, 0, 20);  // sube con la temperatura

  char topic[32], json[200];
  snprintf(topic, sizeof topic, "estaciones/%d/datos", est);
  snprintf(json, sizeof json,
           "{\"estacion\":%d,\"humedad_suelo_pct\":%.1f,\"temp_c\":%.1f,\"et0_mm_dia\":%.2f,\"evento\":%s}",
           est, hum, temp, et0, evento ? "true" : "false");
  mqtt.publish(topic, json);
  Serial.println(json);
}

void loop() {
  if (!mqtt.connected()) conectar(); else mqtt.loop();
  if (mqtt.connected() && millis() - ultimoEnvio >= 5000) {
    ultimoEnvio = millis();
    for (int est = 1; est <= 4; est++) publicar(est);
  }
}
