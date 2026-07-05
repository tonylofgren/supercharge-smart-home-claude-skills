"""Domain-specific data integrity tests for the Seeed XIAO ESP32-C6 board profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "boards" / "special" / "xiao-esp32-c6.json"


@pytest.fixture(scope="module")
def xiao():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_edge_exposes_eleven_pins(xiao):
    """The XIAO castellated edge exposes exactly 11 GPIO (D0-D10)."""
    assert sorted(xiao["gpio"]["valid_pins"]) == [0, 1, 2, 16, 17, 18, 19, 20, 21, 22, 23]


def test_has_thread_and_zigbee(xiao):
    """ESP32-C6 has an 802.15.4 radio: Thread and Zigbee in XIAO format."""
    assert xiao["wireless"]["thread"] is True
    assert xiao["wireless"]["zigbee"] is True
    assert xiao["smart_home_capabilities"]["zigbee_coordinator"] is True
    assert xiao["smart_home_capabilities"]["thread_border_router"] is True


def test_no_strapping_pins_on_edge(xiao):
    """Chip strapping pins (4, 5, 8, 9, 15) are all off the D0-D10 edge."""
    edge = set(xiao["gpio"]["valid_pins"])
    assert edge.isdisjoint(set(xiao["gpio"]["strapping_pins"]))


def test_antenna_switch_documented(xiao):
    """GPIO 3 + GPIO 14 select onboard ceramic vs external U.FL antenna."""
    warnings = " ".join(xiao["limitations"]["strapping_conflict_warnings"])
    assert "GPIO 3" in warnings and "GPIO 14" in warnings


def test_user_led_on_gpio15(xiao):
    """LED_BUILTIN is GPIO 15 (also a chip strapping pin, off the edge)."""
    assert xiao["onboard_components"]["led_gpio"] == 15


def test_battery_powered_low_deep_sleep(xiao):
    """XIAO C6 charges LiPo onboard and sleeps at 15 uA."""
    assert xiao["smart_home_capabilities"]["battery_powered"] is True
    assert xiao["power"]["deep_sleep_current_ua"] == 15


def test_esphome_board_string(xiao):
    """PlatformIO/ESPHome board id is seeed_xiao_esp32c6, esp-idf only."""
    assert xiao["esphome"]["board"] == "seeed_xiao_esp32c6"
    assert xiao["esphome"]["framework"] == "esp-idf"


def test_wifi6(xiao):
    """ESP32-C6 supports WiFi 6 (802.11ax)."""
    assert xiao["wireless"]["wifi_standard"] == "WiFi 6 (ax)"
