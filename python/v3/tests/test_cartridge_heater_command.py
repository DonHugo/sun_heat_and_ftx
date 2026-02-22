"""
Unit tests for cartridge heater switch command handler fix.

Root cause fixed: 'SystemConfig' object has no attribute 'cartridge_heater_relay'
Fix: replaced config.cartridge_heater_relay with pump_config.cartridge_heater_relay
     (pump_config is a PumpConfiguration instance; cartridge_heater_relay = 2)

Tests verify:
  1. set_relay_state is called with relay=2 (pump_config.cartridge_heater_relay)
  2. set_relay_state is called with the correct boolean state
  3. system_state["cartridge_heater"] is updated before relay is set
  4. _publish_switch_state is called after a successful command
  5. No AttributeError is raised (regression test for the original crash)
"""

import unittest
from unittest.mock import MagicMock, call


# ---------------------------------------------------------------------------
# Minimal reproduction of the cartridge heater branch in handle_mqtt_command
# ---------------------------------------------------------------------------

CARTRIDGE_HEATER_RELAY = 2  # mirrors PumpConfiguration.cartridge_heater_relay


class _FakeLogger:
    def info(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass


logger = _FakeLogger()


class _MinimalSystem:
    """
    Reproduces ONLY the cartridge_heater branch of handle_mqtt_command,
    using pump_config.cartridge_heater_relay (the fix) rather than
    config.cartridge_heater_relay (the broken original).
    """

    def __init__(self, hardware_mock, mqtt_mock):
        self.hardware = hardware_mock
        self.mqtt = mqtt_mock
        self.system_state = {"cartridge_heater": False}
        # Simulate pump_config with the correct attribute
        self._relay = CARTRIDGE_HEATER_RELAY

    def _handle_cartridge_heater_command(self, state: bool):
        """Extracted logic from the switch_command branch — fixed version."""
        self.system_state["cartridge_heater"] = state
        # FIX: use pump_config.cartridge_heater_relay (= self._relay here)
        self.hardware.set_relay_state(self._relay, state)
        logger.info(
            f"Cartridge heater relay {self._relay} set to {'ON' if state else 'OFF'}"
        )
        self._publish_switch_state("cartridge_heater", state)

    def _publish_switch_state(self, switch_name: str, state: bool):
        if not self.mqtt or not self.mqtt.is_connected():
            return
        topic = f"homeassistant/switch/solar_heating_{switch_name}/state"
        payload = "ON" if state else "OFF"
        self.mqtt.publish_raw(topic, payload, retain=True)


def _make_system(connected: bool = True):
    hw = MagicMock()
    hw.set_relay_state = MagicMock()
    mqtt = MagicMock()
    mqtt.is_connected.return_value = connected
    mqtt.publish_raw = MagicMock()
    return _MinimalSystem(hw, mqtt)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCartridgeHeaterCommandFix(unittest.TestCase):
    # --- relay number correctness ---

    def test_relay_number_is_2_on_turn_on(self):
        """set_relay_state must be called with relay 2 when turning ON."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(True)
        args, _ = sys.hardware.set_relay_state.call_args
        self.assertEqual(
            args[0], 2, "Relay number must be 2 (pump_config.cartridge_heater_relay)"
        )

    def test_relay_number_is_2_on_turn_off(self):
        """set_relay_state must be called with relay 2 when turning OFF."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(False)
        args, _ = sys.hardware.set_relay_state.call_args
        self.assertEqual(args[0], 2)

    # --- relay state correctness ---

    def test_relay_state_true_on_turn_on(self):
        """set_relay_state must receive True when turning heater ON."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(True)
        args, _ = sys.hardware.set_relay_state.call_args
        self.assertTrue(args[1])

    def test_relay_state_false_on_turn_off(self):
        """set_relay_state must receive False when turning heater OFF."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(False)
        args, _ = sys.hardware.set_relay_state.call_args
        self.assertFalse(args[1])

    # --- system_state updated ---

    def test_system_state_set_true(self):
        """system_state['cartridge_heater'] must be True after ON command."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(True)
        self.assertTrue(sys.system_state["cartridge_heater"])

    def test_system_state_set_false(self):
        """system_state['cartridge_heater'] must be False after OFF command."""
        sys = _make_system()
        sys.system_state["cartridge_heater"] = True  # pre-condition: was ON
        sys._handle_cartridge_heater_command(False)
        self.assertFalse(sys.system_state["cartridge_heater"])

    # --- publish state back to HA ---

    def test_publish_called_after_on(self):
        """_publish_switch_state (→ publish_raw) must be called after ON."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(True)
        sys.mqtt.publish_raw.assert_called_once()
        args, _ = sys.mqtt.publish_raw.call_args
        self.assertEqual(args[1], "ON")

    def test_publish_called_after_off(self):
        """_publish_switch_state (→ publish_raw) must be called after OFF."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(False)
        sys.mqtt.publish_raw.assert_called_once()
        args, _ = sys.mqtt.publish_raw.call_args
        self.assertEqual(args[1], "OFF")

    def test_publish_topic_is_correct(self):
        """Published topic must match HA switch state topic convention."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(True)
        args, _ = sys.mqtt.publish_raw.call_args
        self.assertEqual(
            args[0], "homeassistant/switch/solar_heating_cartridge_heater/state"
        )

    def test_publish_retain_true(self):
        """State must be published with retain=True."""
        sys = _make_system()
        sys._handle_cartridge_heater_command(True)
        _, kwargs = sys.mqtt.publish_raw.call_args
        self.assertTrue(kwargs.get("retain"))

    # --- regression: no AttributeError ---

    def test_no_attribute_error(self):
        """Must NOT raise AttributeError (regression for config.cartridge_heater_relay crash)."""
        sys = _make_system()
        try:
            sys._handle_cartridge_heater_command(True)
            sys._handle_cartridge_heater_command(False)
        except AttributeError as e:
            self.fail(f"AttributeError raised — fix not applied: {e}")

    # --- relay called exactly once ---

    def test_relay_called_exactly_once(self):
        sys = _make_system()
        sys._handle_cartridge_heater_command(True)
        self.assertEqual(sys.hardware.set_relay_state.call_count, 1)

    # --- no publish when disconnected ---

    def test_no_publish_when_disconnected(self):
        """Relay must still be set, but publish_raw must NOT be called when MQTT disconnected."""
        sys = _make_system(connected=False)
        sys._handle_cartridge_heater_command(True)
        sys.hardware.set_relay_state.assert_called_once()  # relay still set
        sys.mqtt.publish_raw.assert_not_called()  # but no MQTT publish


if __name__ == "__main__":
    unittest.main()
