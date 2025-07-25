#!/usr/bin/env python3
"""
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""
import json, threading, queue, time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import paho.mqtt.client as mqtt
from config import MQTTConfig, SystemConfig

# ------------- MODELS -------------
class ToggleRequest(BaseModel):
    device: str   # "pump" | "heater" | "test_mode"
    state: bool

# ------------- GLOBAL STATE -------------
cfg = MQTTConfig()
system_cfg = SystemConfig()
state: Dict[str, Any] = {
    "temps": {},               # senaste från alla sensorer
    "status": {"pump": False, "heater": False, "test_mode": False},
    "mqtt_connected": False
}
cmd_q: "queue.Queue[Dict]" = queue.Queue()

# ------------- MQTT WORKER -------------
def mqtt_thread():
    def on_connect(client, userdata, flags, rc):
        state["mqtt_connected"] = (rc == 0)
        if state["mqtt_connected"]:
            client.subscribe([("sequentmicrosystems/#", 0), ("hass/#", 0)])

    def on_disconnect(client, userdata, rc):
        state["mqtt_connected"] = False

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            cmd_q.put({"type": "mqtt", "topic": msg.topic, "payload": payload})
        except Exception:
            pass

    client = mqtt.Client()
    client.username_pw_set(cfg.username, cfg.password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    while True:
        try:
            client.connect(cfg.broker, cfg.port, 5)
            client.loop_forever()
        except Exception:
            state["mqtt_connected"] = False
            time.sleep(5)

threading.Thread(target=mqtt_thread, daemon=True).start()

# ------------- PROCESS QUEUE -------------
def process_queue():
    while True:
        try:
            item = cmd_q.get_nowait()
            if item["type"] == "mqtt":
                topic, payload = item["topic"], item["payload"]
                if topic.startswith("sequentmicrosystems"):
                    state["temps"][topic] = payload.get("temperature", 0.0)
                elif topic == "hass/test_mode":
                    state["status"]["test_mode"] = bool(payload.get("state", 0))
                elif topic == "hass/elpatron":
                    state["status"]["heater"] = bool(payload.get("state", 0))
                elif topic == "hass/pump":
                    state["status"]["pump"] = bool(payload.get("state", 0))
        except queue.Empty:
            break

# ------------- FASTAPI -------------
app = FastAPI(title="Solar Tank API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "Solar Tank API alive"}

@app.get("/sensors")
def sensors():
    process_queue()
    return state["temps"]

@app.get("/status")
def status():
    process_queue()
    return {"mqtt_connected": state["mqtt_connected"], **state["status"]}

@app.post("/toggle")
def toggle(req: ToggleRequest):
    allowed = {"pump", "heater", "test_mode"}
    if req.device not in allowed:
        raise HTTPException(status_code=400, detail="unknown device")
    if not state["mqtt_connected"]:
        raise HTTPException(status_code=503, detail="MQTT offline")
    topic = f"hass/{req.device}"
    payload = json.dumps({"state": 1 if req.state else 0})
    threading.Thread(
        target=lambda: mqtt.Client().username_pw_set(cfg.username, cfg.password)
        .connect(cfg.broker, cfg.port, 2)
        .publish(topic, payload)
        .disconnect(),
        daemon=True
    ).start()
    state["status"][req.device] = req.state
    return {"ok": True}