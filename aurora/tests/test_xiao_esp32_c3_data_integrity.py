"""Domain-specific data integrity tests for the Seeed XIAO ESP32-C3 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "xiao-esp32-c3.json"


@pytest.fixture(scope="module")
def xiao():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_edge_exposes_eleven_pins(xiao):
    """The XIAO castellated edge exposes exactly 11 GPIO (D0-D10)."""
    assert sorted(xiao["gpio"]["valid_pins"]) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21]


def test_battery_powered_with_charging(xiao):
    """XIAO C3 has an onboard LiPo charge circuit and battery solder pads."""
    assert xiao["smart_home_capabilities"]["battery_powered"] is True
    assert xiao["power"]["battery_connector"] is not None


def test_no_user_led(xiao):
    """XIAO ESP32-C3 has no user-controllable LED; the orange LED is charger-driven."""
    assert xiao["onboard_components"]["led_gpio"] is None


def test_external_antenna_only(xiao):
    """There is no onboard antenna; the included U.FL antenna is mandatory."""
    assert xiao["form_factor"]["ipex_connector"] is True
    warnings = " ".join(xiao["limitations"]["strapping_conflict_warnings"])
    assert "antenna" in warnings.lower()


def test_strapping_pins_on_edge(xiao):
    """GPIO 2, 8, 9 are strapping pins and all three sit on the D0-D10 edge."""
    assert sorted(xiao["gpio"]["strapping_pins"]) == [2, 8, 9]


def test_no_thread_or_zigbee(xiao):
    """ESP32-C3 has no 802.15.4 radio."""
    assert xiao["wireless"]["thread"] is False
    assert xiao["wireless"]["zigbee"] is False
    assert xiao["smart_home_capabilities"]["zigbee_coordinator"] is False


def test_esphome_board_string(xiao):
    """PlatformIO/ESPHome board id is seeed_xiao_esp32c3."""
    assert xiao["esphome"]["board"] == "seeed_xiao_esp32c3"
    assert xiao["esphome"]["variant"] == "ESP32C3"


def test_deep_sleep_current(xiao):
    """Seeed documents 44 uA deep sleep for the XIAO ESP32-C3."""
    assert xiao["power"]["deep_sleep_current_ua"] == 44
