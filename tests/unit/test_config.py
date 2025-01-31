import json
from pathlib import Path
from typing import Any, Dict

import pytest

# Schema definition using type hints for documentation
CONFIG_SCHEMA = {
    "cubesat_name": str,
    "callsign": str,
    "last_battery_temp": float,
    "sleep_duration": int,
    "detumble_enable_z": bool,
    "detumble_enable_x": bool,
    "detumble_enable_y": bool,
    "jokes": list,
    "debug": bool,
    "legacy": bool,
    "heating": bool,
    "orpheus": bool,
    "is_licensed": bool,
    "NORMAL_TEMP": int,
    "NORMAL_BATT_TEMP": int,
    "NORMAL_MICRO_TEMP": int,
    "NORMAL_CHARGE_CURRENT": float,
    "NORMAL_BATTERY_VOLTAGE": float,
    "CRITICAL_BATTERY_VOLTAGE": float,
    "vlowbatt": float,
    "battery_voltage": float,
    "current_draw": int,
    "REBOOT_TIME": int,
    "turbo_clock": bool,
    "radio_cfg": dict,
    "super_secret_code": str,
    "repeat_code": str,
    "jokereply": list,
}


def validate_config(config: Dict[str, Any]) -> None:
    """Validate config data against schema and business rules."""
    # Validate field presence and types
    for field, expected_type in CONFIG_SCHEMA.items():
        if field not in config:
            raise ValueError(f"Required field '{field}' is missing")

        value = config[field]
        if isinstance(expected_type, list):
            if not isinstance(value, list):
                raise TypeError(f"Field '{field}' must be a list")
            if not value:  # Check if list is empty
                raise ValueError(f"Field '{field}' cannot be empty")
            if not all(isinstance(item, str) for item in value):
                raise TypeError(f"All items in '{field}' must be strings")
        elif not isinstance(value, expected_type):
            raise TypeError(f"Field '{field}' must be of type {expected_type.__name__}")

    # Validate callsign
    if not config["callsign"]:
        raise ValueError("Callsign cannot be empty")

    # Validate voltage ranges
    voltage_fields = [
        "battery_voltage",
        "NORMAL_BATTERY_VOLTAGE",
        "CRITICAL_BATTERY_VOLTAGE",
        "vlowbatt",
    ]
    for field in voltage_fields:
        value = config[field]
        if not 0 <= value <= 12.0:
            raise ValueError(f"{field} must be between 0V and 12V")

    # Validate current draw
    if config["current_draw"] < 0:
        raise ValueError("Current draw cannot be negative")

    # Validate time values
    time_fields = ["sleep_duration", "REBOOT_TIME"]
    for field in time_fields:
        if config[field] <= 0:
            raise ValueError(f"{field} must be positive")

    # Add radio_cfg validation after voltage validation
    # Validate radio configuration
    radio_required_fields = {
        "sender_id": int,
        "receiver_id": int,
        "transmit_frequency": float,
        "LoRa_spreading_factor": int,
        "transmit_bandwidth": int,
        "LoRa_coding_rate": int,
        "transmit_power": int,
        "start_time": int,
    }

    if not isinstance(config["radio_cfg"], dict):
        raise TypeError("radio_cfg must be a dictionary")

    for field, expected_type in radio_required_fields.items():
        if field not in config["radio_cfg"]:
            raise ValueError(f"Required radio config field '{field}' is missing")
        if not isinstance(config["radio_cfg"][field], expected_type):
            raise TypeError(
                f"Radio config field '{field}' must be of type {expected_type.__name__}"
            )

    # Validate radio config ranges
    if not 0 <= config["radio_cfg"]["transmit_power"] <= 23:
        raise ValueError("transmit_power must be between 0 and 23")
    if not 400 <= config["radio_cfg"]["transmit_frequency"] <= 450:
        raise ValueError("transmit_frequency must be between 400 and 450 MHz")


def load_config(config_path: str) -> dict:
    """Load and parse the config file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON in config file: {e}")
    except FileNotFoundError:
        pytest.fail(f"Config file not found at {config_path}")


@pytest.fixture
def config_data():
    """Fixture to load the config data."""
    workspace_root = Path(__file__).parent.parent.parent
    config_path = workspace_root / "config.json"
    return load_config(str(config_path))


def test_config_file_exists():
    """Test that config.json exists."""
    workspace_root = Path(__file__).parent.parent.parent
    config_path = workspace_root / "config.json"
    assert config_path.exists(), "config.json file not found"


def test_config_is_valid_json(config_data):
    """Test that config.json is valid JSON."""
    assert isinstance(config_data, dict), "Config file is not a valid JSON object"


def test_config_validation(config_data):
    """Test that config.json matches the expected schema and business rules."""
    try:
        validate_config(config_data)
    except (ValueError, TypeError) as e:
        pytest.fail(str(e))


def test_field_types(config_data):
    """Test that all fields have correct types."""
    # Test string fields
    string_fields = ["cubesat_name", "callsign", "super_secret_code", "repeat_code"]
    for field in string_fields:
        assert isinstance(config_data[field], str), f"{field} must be a string"

    # Test numeric fields
    float_fields = [
        "last_battery_temp",
        "NORMAL_CHARGE_CURRENT",
        "NORMAL_BATTERY_VOLTAGE",
        "CRITICAL_BATTERY_VOLTAGE",
        "vlowbatt",
        "battery_voltage",
    ]
    for field in float_fields:
        assert isinstance(config_data[field], (int, float)), f"{field} must be a number"

    int_fields = [
        "sleep_duration",
        "NORMAL_TEMP",
        "NORMAL_BATT_TEMP",
        "NORMAL_MICRO_TEMP",
        "current_draw",
        "REBOOT_TIME",
    ]
    for field in int_fields:
        assert isinstance(config_data[field], int), f"{field} must be an integer"

    # Test boolean fields
    bool_fields = [
        "detumble_enable_z",
        "detumble_enable_x",
        "detumble_enable_y",
        "debug",
        "legacy",
        "heating",
        "orpheus",
        "is_licensed",
        "turbo_clock",
    ]
    for field in bool_fields:
        assert isinstance(config_data[field], bool), f"{field} must be a boolean"

    # Test list fields
    list_fields = ["jokes", "jokereply"]
    for field in list_fields:
        assert isinstance(config_data[field], list), f"{field} must be a list"
        assert all(
            isinstance(item, str) for item in config_data[field]
        ), f"All items in {field} must be strings"

    # Add radio config testing after list fields
    assert isinstance(config_data["radio_cfg"], dict), "radio_cfg must be a dictionary"
    radio_fields = {
        "sender_id": int,
        "receiver_id": int,
        "transmit_frequency": float,
        "LoRa_spreading_factor": int,
        "transmit_bandwidth": int,
        "LoRa_coding_rate": int,
        "transmit_power": int,
        "start_time": int,
    }
    for field, expected_type in radio_fields.items():
        assert isinstance(
            config_data["radio_cfg"][field], expected_type
        ), f"radio_cfg.{field} must be a {expected_type.__name__}"


def test_voltage_ranges(config_data):
    """Test that voltage values are within expected ranges."""
    voltage_fields = [
        "battery_voltage",
        "NORMAL_BATTERY_VOLTAGE",
        "CRITICAL_BATTERY_VOLTAGE",
        "vlowbatt",
    ]
    for field in voltage_fields:
        value = config_data[field]
        assert 0 <= value <= 12.0, f"{field} must be between 0V and 12V"


def test_time_values(config_data):
    """Test that time values are positive."""
    assert config_data["sleep_duration"] > 0, "sleep_duration must be positive"
    assert config_data["REBOOT_TIME"] > 0, "REBOOT_TIME must be positive"


def test_current_draw_positive(config_data):
    """Test that current draw is not negative."""
    assert config_data["current_draw"] >= 0, "current_draw cannot be negative"


def test_lists_not_empty(config_data):
    """Test that list fields are not empty."""
    assert len(config_data["jokes"]) > 0, "jokes list cannot be empty"
    assert len(config_data["jokereply"]) > 0, "jokereply list cannot be empty"
    assert all(
        isinstance(joke, str) for joke in config_data["jokes"]
    ), "All jokes must be strings"
    assert all(
        isinstance(reply, str) for reply in config_data["jokereply"]
    ), "All joke replies must be strings"
