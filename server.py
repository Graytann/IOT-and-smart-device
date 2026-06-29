"""
Smart Plant Watering - ML Server
Chạy trên máy tính, nhận data từ ESP32 qua WiFi
"""

from flask import Flask, request, jsonify
import pickle
from datetime import datetime
import traceback

app = Flask(__name__)

# Load model
with open('plant_model.pkl', 'rb') as f:
    model = pickle.load(f)

print("✅ Model loaded!")
print("🌿 Smart Pot Watering Server running...")

@app.route('/predict', methods=['POST'])
def predict():
    """
    ESP32 gửi:
    { "moisture": 2200, "temperature": 31.5, "humidity": 72.0 }
    """

    try:
        data = request.get_json()

        moisture = float(data['moisture'])
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])


        features = [[moisture, temperature, humidity]]

        prediction = model.predict(features)[0]
        confidence = model.predict_proba(features)[0][int(prediction)]

        result = {
            "water": bool(prediction),
            "confidence": round(float(confidence), 2),
            "message": "Tưới ngay!" if prediction else "Đất còn đủ ẩm",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "inputs": {
                "moisture": moisture,
                "temperature": temperature,
                "humidity": humidity,
            
            }
        }

        status = "💧 WATER" if prediction else "✅ OK"
        print(f"[{result['timestamp']}] moisture={moisture:.0f} "
              f"temp={temperature:.1f}°C humi={humidity:.0f}% → {status}")

        return jsonify(result)

    except Exception as e:
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)

        return jsonify({
            "error": str(e)
        }), 400


@app.route('/status', methods=['GET'])
def status():
    """Check server"""
    return jsonify({
        "status": "running",
        "model": "RandomForest",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)