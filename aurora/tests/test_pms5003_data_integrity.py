"""Data integrity tests for PMS5003 particulate matter sensor profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "air-quality" / "pms5003.json"


@pytest.fixture(scope="module")
def pms5003():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_uart(pms5003):
    """PMS5003 streams PM data over UART at 9600 8N1, not I2C or SPI."""
    assert pms5003["protocol"] == "uart"
    assert pms5003["pin_requirements"]["type"] == "uart_tx_rx"
    assert pms5003["limitations"]["uart_baud"] == 9600


def test_vcc_must_be_5v_logic_is_3v3(pms5003):
    """The fan needs a 5V supply while the data pins are 3.3V TTL."""
    assert pms5003["limitations"]["vcc_must_be_5v"] is True
    assert pms5003["power"]["voltage_min"] == 4.5
    assert pms5003["limitations"]["logic_level_v"] == 3.3
    assert pms5003["power"]["level_shifter_required_on_5v_board"] is False


def test_calibration_not_required(pms5003):
    """PMS5003 ships factory calibrated; no user procedure exists."""
    assert pms5003["calibration"]["required"] is False


def test_esphome_platform_is_pmsx003(pms5003):
    """ESPHome drives the whole PMSx003 family through the pmsx003 platform."""
    assert pms5003["esphome"]["platform"] == "pmsx003"


def test_easily_confused_with_variants(pms5003):
    """PMS5003T/S add extra measurements and need a different ESPHome type."""
    confused = {v["component_id"] for v in pms5003["variants"]["easily_confused_with"]}
    assert "pms5003t" in confused
    assert "pms7003" in confused


def test_laser_is_a_consumable(pms5003):
    """Laser diode lasts ~8000h continuous; long update intervals extend life."""
    assert pms5003["limitations"]["laser_lifetime_h"] == 8000
    assert pms5003["limitations"]["fan_is_mechanical_consumable"] is True


def test_active_current_is_high(pms5003):
    """The fan draws ~100mA active; relevant for battery power budgets."""
    assert pms5003["power"]["current_ma_active"] == 100
