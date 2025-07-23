#!/usr/bin/env python3
"""
streamlit run gui.py
"""
import json, time, collections
from typing import Dict, Deque
import streamlit as st
import paho.mqtt.client as mqtt
from config import MQTTConfig

# ------------- MQTT -------------
@st.cache_resource
def get_mqtt_client():
    cfg = MQTTConfig()
    client = mqtt.Client(transport="tcp")
    client.username_pw_set(cfg.username, cfg.password)
    client.connect(cfg.broker, cfg.port, 5)
    client.loop_start()
    return client

client = get_mqtt_client()

# ------------- DATA BUFFERS -------------
MAX_POINTS = 60
if "ts" not in st.session_state:
    st.session_state.ts: Deque[float] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.t1_hist: Deque[float] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.t2_hist: Deque[float] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.pump_hist: Deque[int] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.heater_hist: Deque[int] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.temps: Dict[str, float] = {}
    st.session_state.status = {"pump": False, "heater": False, "test_mode": False}

# ------------- MQTT CALLBACK -------------
def on_msg(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())
    if topic.startswith("sequentmicrosystems"):
        st.session_state.temps[topic] = payload.get("temperature", 0.0)
        # Store history for T1 & T2
        if "T1" in topic:
            st.session_state.t1_hist.append(payload.get("temperature", 0.0))
        if "T2" in topic:
            st.session_state.t2_hist.append(payload.get("temperature", 0.0))
    elif topic == "hass/test_mode":
        st.session_state.status["test_mode"] = bool(payload.get("state", 0))
    elif topic == "hass/elpatron":
        st.session_state.status["heater"] = bool(payload.get("state", 0))
    elif topic == "hass/pump":
        st.session_state.status["pump"] = bool(payload.get("state", 0))

client.on_message = on_msg
client.subscribe([("sequentmicrosystems/#", 0), ("hass/#", 0)])

# ------------- STREAMLIT LAYOUT -------------
st.set_page_config(page_title="Solar Tank Dashboard", layout="wide")
st.title("🌞 Live Solar Tank Dashboard")

# --- Row 1: Gauges & Controls ---
c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])

with c1:
    t1 = st.session_state.temps.get("sequentmicrosystems_3_6", 0.0)
    st.metric("Collector (T1)", f"{t1:.1f} °C")
with c2:
    t2 = st.session_state.temps.get("sequentmicrosystems_3_7", 0.0)
    st.metric("Tank (T2)", f"{t2:.1f} °C")

def toggle(topic: str, key: str):
    new = not st.session_state.status[key]
    client.publish(topic, json.dumps({"state": 1 if new else 0}))
    st.session_state.status[key] = new

c3.button("Pump", on_click=toggle, args=("hass/pump", "pump"))
c4.button("Heater", on_click=toggle, args=("hass/elpatron", "heater"))
c5.button("Test Mode", on_click=toggle, args=("hass/test_mode", "test_mode"))

# --- Row 2: Live Charts ---
st.subheader("📈 Temperature History")
chart_data = {
    "Time": list(range(len(st.session_state.t1_hist))),
    "Collector (T1)": list(st.session_state.t1_hist),
    "Tank (T2)": list(st.session_state.t2_hist),
}
st.line_chart(chart_data, use_container_width=True)

# --- Row 3: State Timeline ---
st.subheader("🕑 Pump & Heater Timeline")
state_df = {
    "Time": list(range(len(st.session_state.pump_hist))),
    "Pump": list(st.session_state.pump_hist),
    "Heater": list(st.session_state.heater_hist),
}
st.area_chart(state_df, use_container_width=True)

# --- Row 4: Sensor Heat-map ---
st.subheader("🌡️ All Sensors (latest)")
if st.session_state.temps:
    import pandas as pd
    df = pd.Series(st.session_state.temps).rename_axis("Topic").reset_index(name="Temp")
    df["Stack"] = df["Topic"].str.extract(r"sequentmicrosystems_(\d+)_\d+").astype(int)
    df["Input"] = df["Topic"].str.extract(r"sequentmicrosystems_\d+_(\d+)").astype(int)
    pivot = df.pivot(index="Stack", columns="Input", values="Temp")
    st.dataframe(pivot.style.background_gradient(cmap="coolwarm", vmin=20, vmax=80))

# --- Footer: refresh ---
time.sleep(1)
st.experimental_rerun()