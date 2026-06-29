  /*
    Smart Plant Pot – ESP32 + WiFi + ML Prediction
    Gửi moisture lên Python server, nhận lệnh tưới từ ML model
  */

  #include <WiFi.h>
  #include <HTTPClient.h>
  #include <ArduinoJson.h>

  // ── WiFi ─────────────────────────────────────────────────────────────────────
  const char* WIFI_SSID     = "DESKTOP-DIICEH7 3913";
  const char* WIFI_PASSWORD = "40*791Ea";

  // ── Server ───────────────────────────────────────────────────────────────  x────
  const char* SERVER_URL = "http://192.168.137.1:5000/predict";

  // ── Pin & threshold ──────────────────────────────────────────────────────────
  constexpr int  SENSOR_PIN        = 34;
  constexpr int  PUMP_PIN          = 25;
  constexpr int  ADC_MAX           = 4095;
  constexpr bool RELAY_ACTIVE_LOW  = true;

  // ── Timing ───────────────────────────────────────────────────────────────────
  constexpr uint32_t PUMP_ON_TIME  = 3000;
  constexpr uint32_t SAMPLE_PERIOD = 60000;

  // ── Fallback threshold ────────────────────────────────────────────────────────
  constexpr int DRY_LIMIT = 2000;

  // ─────────────────────────────────────────────────────────────────────────────

  inline void pump(bool on) {
    if (RELAY_ACTIVE_LOW) {
      digitalWrite(PUMP_PIN, on ? LOW : HIGH);
    } else {
      digitalWrite(PUMP_PIN, on ? HIGH : LOW);
    }
    Serial.printf("Relay = %s\n", on ? "ON" : "OFF");
  }

  int readMoisture() {
    uint32_t accum = 0;
    for (int i = 0; i < 5; i++) {
      accum += analogRead(SENSOR_PIN);
      delay(10);
    }
    return accum / 5;
  }

  bool askML(int moisture, float temperature, float humidity) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("⚠ WiFi mất kết nối — dùng fallback threshold");
      return moisture > DRY_LIMIT;
    }

    HTTPClient http;
    Serial.print("🌐 Connecting to: ");
    Serial.println(SERVER_URL);

    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    String body = "{\"moisture\":" + String(moisture) +
                  ",\"temperature\":" + String(temperature, 1) +
                  ",\"humidity\":" + String(humidity, 1) + "}";

    Serial.print("📤 JSON: ");
    Serial.println(body);

    int httpCode = http.POST(body);
    Serial.printf("HTTP Code = %d\n", httpCode);

    if (httpCode <= 0) {
      Serial.print("❌ HTTP Error: ");
      Serial.println(http.errorToString(httpCode));
      http.end();
      return moisture > DRY_LIMIT;
    }

    String response = http.getString();
    Serial.println("📥 Response:");
    Serial.println(response);
    http.end();

    StaticJsonDocument<256> doc;
    DeserializationError err = deserializeJson(doc, response);
    if (err) {
      Serial.print("❌ JSON parse error: ");
      Serial.println(err.c_str());
      return moisture > DRY_LIMIT;
    }

    bool water     = doc["water"];
    float conf     = doc["confidence"];
    String message = doc["message"].as<String>();

    Serial.printf("🤖 ML: %s (confidence=%.0f%%)\n", message.c_str(), conf * 100);
    return water;
  }

  // ─────────────────────────────────────────────────────────────────────────────

  void setup() {
    Serial.begin(115200);
    pinMode(PUMP_PIN, OUTPUT);

    // Relay Active LOW -> HIGH là OFF
    digitalWrite(PUMP_PIN, HIGH);
    delay(200);

    pump(false);
    analogReadResolution(12);

    Serial.println("\n🌿 Smart Plant Pot – ESP32 khởi động...");

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("📡 Đang kết nối WiFi");
    int tries = 0;
    while (WiFi.status() != WL_CONNECTED && tries < 20) {
      delay(500);
      Serial.print(".");
      tries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("\n✅ WiFi OK — IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
      Serial.println("\n⚠ Không kết nối được WiFi — chạy offline mode");
    }
  }

  void loop() {
    int moisture = readMoisture();
    Serial.printf("\n📊 Moisture = %d / %d  (%s)\n",
                  moisture, ADC_MAX,
                  moisture > DRY_LIMIT ? "KHÔ" : "ỔN");

    bool shouldWater = askML(moisture, 30.0, 75.0);

    if (shouldWater) {
      Serial.println("💧 Bắt đầu tưới...");
      pump(true);
      delay(PUMP_ON_TIME);
      pump(false);
      Serial.println("✅ Tưới xong!");
    } else {
      Serial.println("😊 Đất đủ ẩm, không cần tưới");
    }

    delay(SAMPLE_PERIOD);
  }

