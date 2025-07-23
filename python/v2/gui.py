#!/usr/bin/env python3
"""
streamlit run gui.py
"""
import json, time, threading, queue, collections
from typing import Dict, Deque
import streamlit as st
import paho.mqtt.client as mqtt
from config import MQTTConfig

# ------------- CONFIG -------------
CFG = MQTTConfig()
RECONNECT_DELAY = 5  # sekunder

# ------------- STATE -------------
MAX_POINTS = 60
if "mqtt_connected" not in st.session_state:
    st.session_state.mqtt_connected = False
    st.session_state.ts: Deque[float] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.t1_hist: Deque[float] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.t2_hist: Deque[float] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.pump_hist: Deque[int] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.heater_hist: Deque[int] = collections.deque(maxlen=MAX_POINTS)
    st.session_state.temps: Dict[str, float] = {}
    st.session_state.status = {"pump": False, "heater": False, "test_mode": False}
    st.session_state.cmd_q: "queue.Queue[str]" = queue.Queue()

# ------------- MQTT HANDLER (own thread) -------------
class MqttWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.client = mqtt.Client()
        self.client.username_pw_set(CFG.username, CFG.password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            st.session_state.mqtt_connected = True
            client.subscribe([("sequentmicrosystems/#", 0), ("hass/#", 0)])
        else:
            st.session_state.mqtt_connected = False

    def _on_disconnect(self, client, userdata, rc):
        st.session_state.mqtt_connected = False

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode())
        except Exception:
            return
        # Thread-safe: put into Streamlit session_state via queue
        st.session_state.cmd_q.put((topic, payload))

    def run(self):
        while True:
            try:
                self.client.connect(CFG.broker, CFG.port, keepalive=5)
                self.client.loop_forever(retry_first_connection=False)
            except Exception:
                pass
            st.session_state.mqtt_connected = False
            time.sleep(RECONNECT_DELAY)

worker = MqttWorker()
worker.start()

# ------------- STREAMLIT MAIN LOOP -------------
st.set_page_config(page_title="Solar Tank Dashboard", layout="wide")
st.title("🌞 Live Solar Tank Dashboard")

# ---- process MQTT messages in main thread ----
while not st.session_state.cmd_q.empty():
    topic, payload = st.session_state.cmd_q.get_nowait()
    if topic.startswith("sequentmicrosystems"):
        temp = payload.get("temperature", 0.0)
        st.session_state.temps[topic] = temp
        if "T1" in topic:
            st.session_state.t1_hist.append(temp)
        if "T2" in topic:
            st.session_state.t2_hist.append(temp)
    elif topic == "hass/test_mode":
        st.session_state.status["test_mode"] = bool(payload.get("state", 0))
    elif topic == "hass/elpatron":
        st.session_state.status["heater"] = bool(payload.get("state", 0))
    elif topic == "hass/pump":
        st.session_state.status["pump"] = bool(payload.get("state", 0))
        st.session_state.pump_hist.append(int(st.session_state.status["pump"]))
    elif topic == "hass/heater":
        st.session_state.status["heater"] = bool(payload.get("state", 0))
        st.session_state.heater_hist.append(int(st.session_state.status["heater"]))

# ---- Row 0: MQTT status ----
if st.session_state.mqtt_connected:
    st.success("MQTT online")
else:
    st.error("MQTT offline – showing cached data")

# ---- Row 1: Gauges & Controls ----
c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
t1 = st.session_state.temps.get("sequentmicrosystems_3_6", 0.0)
t2 = st.session_state.temps.get("sequentmicrosystems_3_7", 0.0)
c1.metric("Collector (T1)", f"{t1:.1f} °C")
c2.metric("Tank (T2)", f"{t2:.1f} °C")

def send_cmd(topic: str, value: bool):
    if st.session_state.mqtt_connected:
        worker.client.publish(topic, json.dumps({"state": 1 if value else 0}))

c3.button("Toggle Pump", on_click=lambda: send_cmd("hass/pump", not st.session_state.status["pump"]))
c4.button("Toggle Heater", on_click=lambda: send_cmd("hass/elpatron", not st.session_state.status["heater"]))
c5.button("Toggle Test Mode", on_click=lambda: send_cmd("hass/test_mode", not st.session_state.status["test_mode"]))

# ---- Row 2: Live Charts ----
st.subheader("📈 Temperature History")
chart_data = {
    "Time": list(range(len(st.session_state.t1_hist))),
    "Collector (T1)": list(st.session_state.t1_hist),
    "Tank (T2)": list(st.session_state.t2_hist),
}
st.line_chart(chart_data, use_container_width=True)

# ---- Row 3: State Timeline ----
st.subheader("🕑 Pump & Heater Timeline")
state_df = {
    "Time": list(range(len(st.session_state.pump_hist))),
    "Pump": list(st.session_state.pump_hist),
    "Heater": list(st.session_state.heater_hist),
}
st.area_chart(state_df, use_container_width=True)

# ---- Row 4: Sensor Heat-map ----
st.subheader("🌡️ All Sensors (latest)")
if st.session_state.temps:
    import pandas as pd
    df = pd.Series(st.session_state.temps).rename_axis("Topic").reset_index(name="Temp")
    df["Stack"] = df["Topic"].str.extract(r"sequentmicrosystems_(\d+)_\d+").astype(int)
    df["Input"] = df["Topic"].str.extract(r"sequentmicrosystems_\d+_(\d+)").astype(int)
    pivot = df.pivot(index="Stack", columns="Input", values="Temp")
    st.dataframe(pivot.style.background_gradient(cmap="coolwarm", vmin=20, vmax=80))

time.sleep(1)
st.experimental_rerun()