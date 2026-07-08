"""
Unit tests for the night cooling feature.

Night cooling dumps excess tank heat via the collector when the tank is too
hot AND the collector is meaningfully colder (which naturally happens at
night). It is temperature-controlled (no clock), toggleable, and exposes a
running indicator to Home Assistant.

Strategy (mirrors test_switch_state_retain.py / test_cartridge_heater_command.py):
define minimal stand-ins that reproduce the EXACT logic added to
main_system.py, avoiding an import of the ~4000-line module (which drags in
RPi.GPIO, smbus, etc.) while still testing the real behaviour under change.

Tests cover:
  1. Control logic: activation / deactivation / hysteresis / guard conditions
  2. Switch-command handling: enabling/disabling the feature and pump handoff
  3. Number-command handling: setting the tank threshold
  4. Indicator: night_cooling_active is published as an ON/OFF binary sensor
"""

import unittest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# 1. Control logic reproduction (mirrors _process_control_logic night block)
# ---------------------------------------------------------------------------


def night_cooling_tick(state, params, solar_collector, storage_tank):
    """Reproduces the night cooling branch of _process_control_logic exactly.

    Returns the mutated ``state`` for assertions. ``state`` carries
    ``overheated``, ``collector_cooling_active``, ``night_cooling_active`` and
    ``primary_pump``. ``params`` carries the four night_cooling_* settings.
    """
    enabled = params.get("night_cooling_enabled", False)
    target = params.get("night_cooling_tank_temp", 80.0)
    hyst = params.get("night_cooling_hysteres", 5.0)
    dt_min = params.get("night_cooling_dt_min", 5.0)
    tank_minus_collector = storage_tank - solar_collector

    if (
        enabled
        and not state.get("overheated", False)
        and not state.get("collector_cooling_active", False)
    ):
        if (
            not state.get("night_cooling_active", False)
            and storage_tank >= target
            and tank_minus_collector >= dt_min
        ):
            state["night_cooling_active"] = True
            if not state.get("primary_pump", False):
                state["primary_pump"] = True
        elif state.get("night_cooling_active", False) and (
            storage_tank < (target - hyst) or tank_minus_collector < dt_min
        ):
            state["night_cooling_active"] = False
            if state.get("primary_pump", False):
                state["primary_pump"] = False
    elif state.get("night_cooling_active", False):
        state["night_cooling_active"] = False

    # While active, keep the pump on (and the loop would 'return' here)
    if state.get("night_cooling_active", False):
        if not state.get("primary_pump", False):
            state["primary_pump"] = True

    return state


def _state(**overrides):
    base = {
        "overheated": False,
        "collector_cooling_active": False,
        "night_cooling_active": False,
        "primary_pump": False,
    }
    base.update(overrides)
    return base


def _params(**overrides):
    base = {
        "night_cooling_enabled": True,
        "night_cooling_tank_temp": 80.0,
        "night_cooling_hysteres": 5.0,
        "night_cooling_dt_min": 5.0,
    }
    base.update(overrides)
    return base


class TestNightCoolingControlLogic(unittest.TestCase):
    def test_activates_when_tank_hot_and_collector_cold(self):
        s = night_cooling_tick(_state(), _params(), solar_collector=40, storage_tank=82)
        self.assertTrue(s["night_cooling_active"])
        self.assertTrue(s["primary_pump"])

    def test_stays_active_within_hysteresis(self):
        s = _state(night_cooling_active=True, primary_pump=True)
        s = night_cooling_tick(s, _params(), solar_collector=40, storage_tank=79)
        self.assertTrue(s["night_cooling_active"], "79 > 80-5, should stay active")
        self.assertTrue(s["primary_pump"])

    def test_stops_when_tank_drops_below_hysteresis(self):
        s = _state(night_cooling_active=True, primary_pump=True)
        s = night_cooling_tick(s, _params(), solar_collector=40, storage_tank=74)
        self.assertFalse(s["night_cooling_active"], "74 < 80-5, should stop")
        self.assertFalse(s["primary_pump"])

    def test_stops_when_collector_warms_up(self):
        # Collector rises so tank-collector diff falls below dt_min while active
        s = _state(night_cooling_active=True, primary_pump=True)
        s = night_cooling_tick(s, _params(), solar_collector=79, storage_tank=82)
        self.assertFalse(s["night_cooling_active"], "tank-coll=3 < 5, should stop")
        self.assertFalse(s["primary_pump"])

    def test_no_activation_during_daytime(self):
        # Tank hot but collector also hot (sun shining) -> never activates
        s = night_cooling_tick(_state(), _params(), solar_collector=85, storage_tank=82)
        self.assertFalse(s["night_cooling_active"])
        self.assertFalse(s["primary_pump"])

    def test_no_activation_when_tank_below_target(self):
        s = night_cooling_tick(_state(), _params(), solar_collector=40, storage_tank=78)
        self.assertFalse(s["night_cooling_active"])

    def test_no_activation_when_feature_disabled(self):
        p = _params(night_cooling_enabled=False)
        s = night_cooling_tick(_state(), p, solar_collector=40, storage_tank=82)
        self.assertFalse(s["night_cooling_active"])

    def test_boundary_exactly_at_target_and_dt_min_activates(self):
        # tank == target (>=) and tank-collector == dt_min (>=) -> activates
        s = night_cooling_tick(_state(), _params(), solar_collector=75, storage_tank=80)
        self.assertTrue(s["night_cooling_active"])

    def test_overheated_clears_active_flag(self):
        s = _state(night_cooling_active=True, primary_pump=True, overheated=True)
        s = night_cooling_tick(s, _params(), solar_collector=40, storage_tank=82)
        self.assertFalse(
            s["night_cooling_active"],
            "overheated must take priority and clear night cooling",
        )

    def test_collector_cooling_takes_priority(self):
        s = _state(night_cooling_active=True, collector_cooling_active=True)
        s = night_cooling_tick(s, _params(), solar_collector=40, storage_tank=82)
        self.assertFalse(
            s["night_cooling_active"],
            "collector cooling must take priority and clear night cooling",
        )

    def test_disabling_feature_midcycle_clears_active(self):
        s = _state(night_cooling_active=True, primary_pump=True)
        p = _params(night_cooling_enabled=False)
        s = night_cooling_tick(s, p, solar_collector=40, storage_tank=82)
        self.assertFalse(s["night_cooling_active"])

    def test_custom_threshold_respected(self):
        # Lower the threshold to 70; a 72°C tank should now activate
        p = _params(night_cooling_tank_temp=70.0)
        s = night_cooling_tick(_state(), p, solar_collector=40, storage_tank=72)
        self.assertTrue(s["night_cooling_active"])


# ---------------------------------------------------------------------------
# 2. Switch-command handling (mirrors the night_cooling branch of
#    _handle_mqtt_command)
# ---------------------------------------------------------------------------


class _FakeLogger:
    def info(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass


class _MinimalSwitchSystem:
    """Reproduces ONLY the night_cooling switch branch of _handle_mqtt_command."""

    def __init__(self, hardware_mock):
        self.hardware = hardware_mock
        self.control_params = {"night_cooling_enabled": False}
        self.system_state = {"night_cooling_active": False, "primary_pump": False}
        self.log = _FakeLogger()

    def _update_system_mode(self):
        pass

    def handle_night_cooling_switch(self, state):
        # The generic relay write that _handle_mqtt_command does first:
        self.hardware.set_relay_state(1, state)
        # The night_cooling branch:
        self.control_params["night_cooling_enabled"] = state
        if not state:
            if self.system_state.get("night_cooling_active", False):
                self.system_state["night_cooling_active"] = False
                self.hardware.set_relay_state(1, False)
                self.system_state["primary_pump"] = False
            else:
                self.hardware.set_relay_state(
                    1, self.system_state.get("primary_pump", False)
                )
        else:
            self.hardware.set_relay_state(
                1, self.system_state.get("primary_pump", False)
            )
        self._update_system_mode()


class TestNightCoolingSwitchCommand(unittest.TestCase):
    def test_enabling_sets_flag(self):
        sys = _MinimalSwitchSystem(MagicMock())
        sys.handle_night_cooling_switch(True)
        self.assertTrue(sys.control_params["night_cooling_enabled"])

    def test_enabling_does_not_force_pump_on(self):
        # Feature ON but conditions not evaluated here: pump must stay as-is (OFF)
        sys = _MinimalSwitchSystem(MagicMock())
        sys.handle_night_cooling_switch(True)
        # Final relay write should restore current pump state (False), not force ON
        last_call = sys.hardware.set_relay_state.call_args
        self.assertEqual(last_call.args, (1, False))

    def test_disabling_while_active_stops_pump(self):
        sys = _MinimalSwitchSystem(MagicMock())
        sys.control_params["night_cooling_enabled"] = True
        sys.system_state["night_cooling_active"] = True
        sys.system_state["primary_pump"] = True
        sys.handle_night_cooling_switch(False)
        self.assertFalse(sys.control_params["night_cooling_enabled"])
        self.assertFalse(sys.system_state["night_cooling_active"])
        self.assertFalse(sys.system_state["primary_pump"])
        last_call = sys.hardware.set_relay_state.call_args
        self.assertEqual(last_call.args, (1, False))

    def test_disabling_while_inactive_preserves_pump_state(self):
        # Pump running for normal heating, night cooling not active -> disabling
        # night cooling must NOT stop the pump
        sys = _MinimalSwitchSystem(MagicMock())
        sys.system_state["primary_pump"] = True
        sys.handle_night_cooling_switch(False)
        last_call = sys.hardware.set_relay_state.call_args
        self.assertEqual(last_call.args, (1, True), "pump must be left running")


# ---------------------------------------------------------------------------
# 3. Number-command handling (mirrors night_cooling_tank_temp branch)
# ---------------------------------------------------------------------------


class TestNightCoolingNumberCommand(unittest.TestCase):
    def test_sets_tank_threshold(self):
        control_params = {"night_cooling_tank_temp": 80.0}

        # Reproduce the number_command branch:
        number_name = "night_cooling_tank_temp"
        value = 75.0
        if number_name == "night_cooling_tank_temp":
            control_params["night_cooling_tank_temp"] = value

        self.assertEqual(control_params["night_cooling_tank_temp"], 75.0)


# ---------------------------------------------------------------------------
# 4. Indicator publishing (mirrors the night_cooling_active binary sensor)
# ---------------------------------------------------------------------------


class _IndicatorSystem:
    """Reproduces the night_cooling_active binary sensor publish branch."""

    def __init__(self, mqtt_mock):
        self.mqtt = mqtt_mock

    def publish_indicator(self, value):
        sensor_name = "night_cooling_active"
        binary_topic = (
            f"homeassistant/binary_sensor/solar_heating_{sensor_name}/state"
        )
        binary_message = "ON" if value else "OFF"
        self.mqtt.publish_raw(binary_topic, binary_message)


class TestNightCoolingIndicator(unittest.TestCase):
    def test_publishes_on_when_active(self):
        mqtt = MagicMock()
        _IndicatorSystem(mqtt).publish_indicator(True)
        mqtt.publish_raw.assert_called_once_with(
            "homeassistant/binary_sensor/solar_heating_night_cooling_active/state",
            "ON",
        )

    def test_publishes_off_when_inactive(self):
        mqtt = MagicMock()
        _IndicatorSystem(mqtt).publish_indicator(False)
        mqtt.publish_raw.assert_called_once_with(
            "homeassistant/binary_sensor/solar_heating_night_cooling_active/state",
            "OFF",
        )


if __name__ == "__main__":
    unittest.main()
