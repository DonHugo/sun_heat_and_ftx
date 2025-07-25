# mqtt_discovery.py
import json
from typing import Any
from paho.mqtt.client import Client

DISCOVERY_PREFIX = "homeassistant"

def _send(client: Client, topic: str, payload: Any):
    client.publish(topic, json.dumps(payload), retain=True)

def publish_discovery(client: Client):
    """Skicka alla HA Discovery-meddelanden en gång vid uppstart."""
    # Temperatur-sensorer
    _send(client, f"{DISCOVERY_PREFIX}/sensor/solar_t1/config", {
        "name": "Collector T1",
        "state_topic": "sequentmicrosystems/3_6",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "unique_id": "solar_t1",
        "device": {
            "identifiers": ["solar_tank_controller"],
            "name": "Solar Tank Controller"
        }
    })
    _send(client, f"{DISCOVERY_PREFIX}/sensor/solar_t2/config", {
        "name": "Tank T2",
        "state_topic": "sequentmicrosystems/3_7",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "unique_id": "solar_t2",
        "device": {
            "identifiers": ["solar_tank_controller"]
        }
    })

    # Switch / pump
    _send(client, f"{DISCOVERY_PREFIX}/switch/solar_pump/config", {
        "name": "Solar Pump",
        "command_topic": "hass/pump",
        "state_topic": "hass/pump",
        "value_template": "{{ value_json.state }}",
        "payload_on": '{"state":true}',
        "payload_off": '{"state":false}',
        "unique_id": "solar_pump",
        "device": {"identifiers": ["solar_tank_controller"]}
    })

    # Switch / heater
    _send(client, f"{DISCOVERY_PREFIX}/switch/solar_heater/config", {
        "name": "Solar Heater",
        "command_topic": "hass/elpatron",
        "state_topic": "hass/elpatron",
        "value_template": "{{ value_json.state }}",
        "payload_on": '{"state":true}',
        "payload_off": '{"state":false}',
        "unique_id": "solar_heater",
        "device": {"identifiers": ["solar_tank_controller"]}
    })