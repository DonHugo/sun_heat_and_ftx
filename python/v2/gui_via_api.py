#!/usr/bin/env python3
"""
streamlit run gui_via_api.py
"""
import json, time, requests
import streamlit as st

API = "http://localhost:8000"

def api(path: str, method="GET", **kwargs):
    try:
        r = requests.request(method, API + path, timeout=1, **kwargs)
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None

# ------------- STREAMLIT -------------
st.set_page_config(page_title="Solar Tank GUI (API)", layout="wide")
st.title("🌞 Solar Tank Dashboard (API)")

status = api("/status")
if not status:
    st.stop()

# MQTT banner
if status.get("mqtt_connected"):
    st.success("MQTT online")
else:
    st.error("MQTT offline – showing cached data")

# Gauges & controls
c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
temps = api("/sensors") or {}
t1 = temps.get("sequentmicrosystems_3_6", 0.0)
t2 = temps.get("sequentmicrosystems_3_7", 0.0)
c1.metric("Collector (T1)", f"{t1:.1f} °C")
c2.metric("Tank (T2)", f"{t2:.1f} °C")

def toggle(device: str):
    new = not status[device]
    api("/toggle", method="POST", json={"device": device, "state": new})

c3.button("Toggle Pump", on_click=toggle, args=("pump",))
c4.button("Toggle Heater", on_click=toggle, args=("heater",))
c5.button("Toggle Test Mode", on_click=toggle, args=("test_mode",))

# Charts / heat-map (samma som tidigare, men hämtar från API)
st.subheader("📈 Temperature History")
import pandas as pd
# ... (använd samma kod som i föregående GUI men med data från `temps`)

time.sleep(2)
st.experimental_rerun()