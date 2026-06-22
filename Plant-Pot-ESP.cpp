#include <Arduino.h>

//Pin & threshold settings
constexpr int  SENSOR_PIN   = 34;   // ADC‑capable pin (input only)
constexpr int  PUMP_PIN     = 25;   // Any GPIO that’s free / PWM‑capable
constexpr int  ADC_MAX      = 4095; // 12‑bit ADC range on ESP32
constexpr int  DRY_LIMIT    = 2200; // Calibrate! lower = wetter
constexpr bool RELAY_ACTIVE_LOW = true; //true if low on water > turns pump ON

//Timing parameters(ms)
constexpr uint32_t PUMP_ON_TIME   = 3000;   // how long to water
constexpr uint32_t SAMPLE_PERIOD  = 60000;  // check once a minute

//turn pump on/off
inline void pump(bool on)
{
  digitalWrite(PUMP_PIN, (on ^ RELAY_ACTIVE_LOW) ? HIGH : LOW);
}

void setup()
{
  Serial.begin(115200);
  pinMode(PUMP_PIN, OUTPUT);
  pump(false);
  analogReadResolution(12);              // safest: make sure we’re at 0‑4095
  // Optional: improve accuracy a bit
  Serial.println(F("Smart Plant Pot – ESP32 ready"));
}

void loop()
{
  //read sensor
  uint32_t accum = 0;
  for (int i = 0; i < 5; ++i)
  {
    accum += analogRead(SENSOR_PIN);
    delay(10);
  }
  int moisture = accum / 5;

  //print status
  Serial.printf("Moisture level = %d / %d  →  %s\n",
                moisture, ADC_MAX,
                (moisture > DRY_LIMIT ? "DRY" : "OK"));

  //soil dry or not
  if (moisture > DRY_LIMIT)
  {
    Serial.println(F("Soil is dry → watering…"));
    pump(true);
    delay(PUMP_ON_TIME);
    pump(false);
    Serial.println(F("Watering done"));
  }

  //wait until next reading
  delay(SAMPLE_PERIOD);
}
