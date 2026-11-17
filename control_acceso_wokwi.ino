#include <Arduino.h>

// Python envia '1' si encuentra un rostro y '0' si no lo encuentra.
// Tambien puedes escribir estos comandos en el monitor serial de Wokwi.
constexpr uint8_t LED_VERDE = 8;
constexpr uint8_t LED_ROJO = 9;

void setup() {
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_ROJO, LOW);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() == 0) {
    return;
  }

  const int comando = Serial.read();
  if (comando != '1' && comando != '0') {
    return;  // Ignora los saltos de linea y otros caracteres.
  }

  const bool hayRostro = comando == '1';
  digitalWrite(LED_VERDE, hayRostro ? HIGH : LOW);
  digitalWrite(LED_ROJO, hayRostro ? LOW : HIGH);
  Serial.println(hayRostro ? "acceso correcto" : "acceso denegado");
}
