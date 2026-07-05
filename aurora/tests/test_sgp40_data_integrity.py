"""Data integrity tests for SGP40 VOC index sensor profile."""
import json
from pathlib import Path
import pytest

PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "components" / "air-quality" / "sgp40.json"


@pytest.fixture(scope="module")
def sgp40():
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_protocol_is_i2c_at_0x59(sgp40):
    """SGP40 has a fixed I2C address of 0x59 with no strap pin."""
    assert sgp40["protocol"] == "i2c"
    assert sgp40["i2c"]["default_addresses"] == ["0x59"]
    assert sgp40["i2c"]["address_strap_pin"] is None


def test_not_5v_tolerant(sgp40):
    """SGP40 tops out at 3.6V; a 5V board needs a level shifter."""
    assert sgp40["power"]["voltage_max"] == 3.6
    assert sgp40["power"]["tolerates_5v"] is False
    assert sgp40["power"]["level_shifter_required_on_5v_board"] is True


def test_calibration_not_required(sgp40):
    """The VOC index self-adapts via Sensirion's Gas Index Algorithm."""
    assert sgp40["calibration"]["required"] is False


def test_voc_index_computed_host_side(sgp40):
    """The chip outputs raw SRAW; the 1-500 VOC index is computed in ESPHome."""
    assert sgp40["limitations"]["index_computed_host_side"] is True
    assert sgp40["limitations"]["voc_index_range"] == "1-500"


def test_esphome_platform_is_sgp4x(sgp40):
    """SGP40 and SGP41 share the unified sgp4x platform since ESPHome 2022.6.0."""
    assert sgp40["esphome"]["platform"] == "sgp4x"
    assert sgp40["esphome"]["min_version"] == "2022.6.0"


def test_easily_confused_with_sgp41_and_sgp30(sgp40):
    """SGP41 adds NOx (same platform); SGP30 uses the separate sgp30 platform."""
    confused = {v["component_id"] for v in sgp40["variants"]["easily_confused_with"]}
    assert "sgp41" in confused
    assert "sgp30" in confused
