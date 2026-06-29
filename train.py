"""
Smart Plant Pot – Train Script
Load tarp_clean.csv → Adjust label → Train → Save model
Chạy: python train.py  (sau khi đã chạy eda.py)
Output: plant_model.pkl
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os

# ── LOAD DATA SẠCH TỪ EDA ────────────────────────────────────────────────────
print("📂 Loading cleaned dataset...")
if not os.path.exists('tarp_clean.csv'):
    print("❌ Không tìm thấy tarp_clean.csv!")
    print("   Hãy chạy python eda.py trước.")
    exit()

df = pd.read_csv('tarp_clean.csv')
print(f"   Shape: {df.shape}")
print(f"   Columns: {df.columns.tolist()}")

# ── ADJUST LABEL CHO RAU MÁ ───────────────────────────────────────────────────
print("\n🌿 Điều chỉnh label theo đặc tính Rau Má...")
# Dataset gốc: cây tổng quát
# Rau má cần ẩm hơn (75-100% FC)
# → Tưới thêm khi moisture 35-50 + nhiệt > 28°C
mask = (df['Soil Moisture'] >= 35) & (df['Soil Moisture'] <= 50)
df.loc[mask & (df['Temperature'] > 28), 'label'] = 1

on_count  = df['label'].sum()
off_count = len(df) - on_count
print(f"   ON  (tưới):  {on_count:,} ({on_count/len(df):.1%})")
print(f"   OFF (không): {off_count:,} ({off_count/len(df):.1%})")

# ── TRAIN/TEST SPLIT ──────────────────────────────────────────────────────────
features = ['Soil Moisture', 'Temperature', 'Soil Humidity']
X = df[features]
y = df['label']

print("\n✂️  Train/Test Split (80/20, stratified)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")

# ── TRAIN ─────────────────────────────────────────────────────────────────────
print("\n🤖 Training Random Forest...")
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)
print("   Done!")

# ── EVALUATE ──────────────────────────────────────────────────────────────────
print("\n=== Kết quả Model ===")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred,
      target_names=['OFF (không tưới)', 'ON (tưới)']))

print("Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"   TN={cm[0,0]:,}  FP={cm[0,1]:,}")
print(f"   FN={cm[1,0]:,}  TP={cm[1,1]:,}")

print("\nFeature Importance:")
for feat, imp in sorted(zip(features, model.feature_importances_),
                         key=lambda x: -x[1]):
    bar = '█' * int(imp * 40)
    print(f"   {feat:<20} {bar} {imp:.3f}")

# ── SAVE ──────────────────────────────────────────────────────────────────────
with open('plant_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("\n✅ Saved: plant_model.pkl")
print("🚀 Tiếp theo: python server.py")