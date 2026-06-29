import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Pot", layout="wide")
st.title("🌿 Smart Pot Dashboard")

SERVER = "http://localhost:5000"

if st.button("🔄 Refresh"):
    st.rerun()

# Server status
try:
    res = requests.get(f"{SERVER}/status", timeout=3)
    data = res.json()
    st.success(f"✅ Server running — {data['time']}")
except:
    st.error("❌ Server offline! Hãy chạy server.py trước.")
    st.stop()

# Load logs
try:
    logs = requests.get(f"{SERVER}/logs", timeout=3).json()
except:
    logs = []

if not logs:
    st.warning("Chưa có dữ liệu! Đợi ESP32 gửi data...")
    st.stop()

df = pd.DataFrame(logs)
df['time'] = pd.to_datetime(df['time'])

# Metrics
col1, col2, col3, col4 = st.columns(4)
latest = df.iloc[-1]
col1.metric("💧 Moisture",   f"{latest['moisture']:.0f}")
col2.metric("🌡️ Nhiệt độ",  f"{latest['temperature']:.1f}°C")
col3.metric("💦 Độ ẩm KK",  f"{latest['humidity']:.0f}%")
col4.metric("🪣 Lần tưới",  f"{df['watered'].sum()} lần")

st.divider()

# Biểu đồ moisture
st.subheader("📈 Độ ẩm đất theo thời gian")
fig1 = px.line(df, x='time', y='moisture', color_discrete_sequence=['#2ecc71'])
fig1.add_hline(y=2000, line_dash="dash", line_color="red", annotation_text="Ngưỡng khô")
st.plotly_chart(fig1, use_container_width=True)

# Nhiệt độ & độ ẩm
st.subheader("🌡️ Nhiệt độ & Độ ẩm không khí")
col1, col2 = st.columns(2)
fig2 = px.line(df, x='time', y='temperature', color_discrete_sequence=['#e74c3c'])
col1.plotly_chart(fig2, use_container_width=True)
fig3 = px.line(df, x='time', y='humidity', color_discrete_sequence=['#3498db'])
col2.plotly_chart(fig3, use_container_width=True)

# Lịch sử tưới
st.subheader("💧 Lịch sử tưới")
watered_df = df[df['watered'] == True][['time', 'moisture', 'confidence']]
if watered_df.empty:
    st.info("Chưa có lần tưới nào!")
else:
    watered_df.columns = ['Thời gian', 'Moisture lúc tưới', 'Độ tin cậy']
    st.dataframe(watered_df, use_container_width=True)

# Raw data
with st.expander("📋 Xem toàn bộ dữ liệu"):
    st.dataframe(df, use_container_width=True)