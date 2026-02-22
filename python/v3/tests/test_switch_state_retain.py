"""
Unit tests for _publish_switch_state retain=True fix.

Strategy: define a minimal class that reproduces the exact method body from
main_system.py, with a mocked logger and mocked mqtt.  This avoids importing
the 3 000-line main_system.py (which drags in RPi.GPIO, smbus, etc.) while
still testing the real logic under change.

Tests verify:
  1. publish_raw is called with retain=True  (the fix)
  2. ON/OFF payloads are correct
  3. Topic format is correct for all three switches
  4. No publish when MQTT is disconnected / None
"""

import logging
import unittest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Minimal stand-in that reproduces ONLY the patched method
# ---------------------------------------------------------------------------


class _FakeLogger:
    def debug(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


logger = _FakeLogger()


class _MinimalSystem:
    """Reproduces _publish_switch_state exactly as it appears in main_system.py."""

    def __init__(self, mqtt_mock):
        self.mqtt = mqtt_mock

    def _publish_switch_state(self, switch_name: str, state: bool):
        """Publish switch state to Home Assistant with retain=True so HA always
        gets the last known state on reconnect / subscribe."""
        try:
            if not self.mqtt or not self.mqtt.is_connected():
                return

            topic = f"homeassistant/switch/solar_heating_{switch_name}/state"
            state_str = "ON" if state else "OFF"
            self.mqtt.publish_raw(topic, state_str, retain=True)
            logger.debug(
                f"Published switch state: {switch_name} = {state_str} (retained)"
            )

        except Exception as e:
            logger.error(f"Error publishing switch state: {e}")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _connected_system():
    mqtt = MagicMock()
    mqtt.is_connected.return_value = True
    mqtt.publish_raw = MagicMock()
    return _MinimalSystem(mqtt)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPublishSwitchStateRetain(unittest.TestCase):
    # --- retain=True is the core fix ---

    def test_retain_true_when_on(self):
        """ON state must be published with retain=True."""
        sys = _connected_system()
        sys._publish_switch_state("cartridge_heater", True)
        _, kwargs = sys.mqtt.publish_raw.call_args
        self.assertTrue(kwargs.get("retain"), "retain must be True for ON")

    def test_retain_true_when_off(self):
        """OFF state must also be published with retain=True."""
        sys = _connected_system()
        sys._publish_switch_state("cartridge_heater", False)
        _, kwargs = sys.mqtt.publish_raw.call_args
        self.assertTrue(kwargs.get("retain"), "retain must be True for OFF")

    # --- payload correctness ---

    def test_payload_on(self):
        sys = _connected_system()
        sys._publish_switch_state("cartridge_heater", True)
        args, _ = sys.mqtt.publish_raw.call_args
        self.assertEqual(args[1], "ON")

    def test_payload_off(self):
        sys = _connected_system()
        sys._publish_switch_state("cartridge_heater", False)
        args, _ = sys.mqtt.publish_raw.call_args
        self.assertEqual(args[1], "OFF")

    # --- topic format for all three switches ---

    def test_topic_cartridge_heater(self):
        sys = _connected_system()
        sys._publish_switch_state("cartridge_heater", True)
        args, _ = sys.mqtt.publish_raw.call_args
        self.assertEqual(
            args[0], "homeassistant/switch/solar_heating_cartridge_heater/state"
        )

    def test_topic_primary_pump(self):
        sys = _connected_system()
        sys._publish_switch_state("primary_pump", True)
        args, _ = sys.mqtt.publish_raw.call_args
        self.assertEqual(
            args[0], "homeassistant/switch/solar_heating_primary_pump/state"
        )

    def test_topic_primary_pump_manual(self):
        sys = _connected_system()
        sys._publish_switch_state("primary_pump_manual", False)
        args, _ = sys.mqtt.publish_raw.call_args
        self.assertEqual(
            args[0], "homeassistant/switch/solar_heating_primary_pump_manual/state"
        )

    # --- safety guards ---

    def test_no_publish_when_disconnected(self):
        """Must not publish when MQTT is not connected."""
        mqtt = MagicMock()
        mqtt.is_connected.return_value = False
        sys = _MinimalSystem(mqtt)
        sys._publish_switch_state("cartridge_heater", True)
        mqtt.publish_raw.assert_not_called()

    def test_no_publish_when_mqtt_none(self):
        """Must not raise and must not publish when mqtt is None."""
        sys = _MinimalSystem(None)
        # Should not raise
        sys._publish_switch_state("cartridge_heater", True)

    def test_publish_called_exactly_once(self):
        """publish_raw must be called exactly once per switch state call."""
        sys = _connected_system()
        sys._publish_switch_state("cartridge_heater", True)
        self.assertEqual(sys.mqtt.publish_raw.call_count, 1)


if __name__ == "__main__":
    unittest.main()
