"""Domain-specific data integrity tests for the Seeed XIAO ESP32-S3 (plain) board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "xiao-esp32-s3.json"


@pytest.fixture(scope="module")
def xiao():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_edge_exposes_eleven_pins(xiao):
    """The XIAO castellated edge exposes exactly 11 GPIO (D0-D10)."""
    assert sorted(xiao["gpio"]["valid_pins"]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 43, 44]


def test_psram_enables_voice_assistant(xiao):
    """8MB OPI PSRAM plus dual-core Xtensa makes voice assistant viable."""
    assert xiao["memory"]["psram_mb"] == 8
    assert xiao["smart_home_capabilities"]["voice_assistant"] is True


def test_strapping_pin_on_edge_is_gpio3(xiao):
    """GPIO 3 is exposed as edge pin D2 and is an S3 strapping pin."""
    assert 3 in xiao["gpio"]["strapping_pins"]
    assert 3 in xiao["gpio"]["valid_pins"]


def test_edge_pins_are_adc1_and_touch(xiao):
    """GPIO 1-9 on the edge are all ADC1 channels and touch pins T1-T9."""
    assert sorted(xiao["gpio"]["adc1_pins"]) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert sorted(xiao["gpio"]["touch_pins"]) == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_no_battery_monitoring(xiao):
    """Plain XIAO S3 exposes no GPIO for VBAT sensing despite the charger."""
    assert xiao["power"]["vbat_monitor_pin"] is None
    assert xiao["smart_home_capabilities"]["battery_powered"] is True


def test_camera_is_sense_only(xiao):
    """The plain board has no camera connector; that is the Sense variant."""
    assert xiao["smart_home_capabilities"]["camera_support"] is False


def test_no_thread_or_zigbee(xiao):
    """ESP32-S3 has no 802.15.4 radio."""
    assert xiao["wireless"]["thread"] is False
    assert xiao["wireless"]["zigbee"] is False


def test_esphome_board_string(xiao):
    """PlatformIO/ESPHome board id is seeed_xiao_esp32s3."""
    assert xiao["esphome"]["board"] == "seeed_xiao_esp32s3"
    assert xiao["esphome"]["variant"] == "ESP32S3"


def test_user_led_on_gpio21(xiao):
    """LED_BUILTIN is the yellow user LED on GPIO 21."""
    assert xiao["onboard_components"]["led_gpio"] == 21
