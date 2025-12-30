# Entity Platforms

Complete reference for Home Assistant entity types and implementation.

## Entity Basics

All entities inherit from `Entity` or a platform-specific base class.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `unique_id` | `str` | Unique identifier (REQUIRED for customization) |

### Recommended Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Entity name |
| `device_info` | `DeviceInfo` | Device grouping |
| `available` | `bool` | Entity availability |
| `entity_category` | `EntityCategory` | Config/diagnostic category |

### Base Entity Example

```python
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.helpers.entity import EntityCategory

class MyEntity(Entity):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, device_id: str) -> None:
        """Initialize entity."""
        self.coordinator = coordinator
        self._device_id = device_id

        # Unique ID is REQUIRED
        self._attr_unique_id = f"{entry.entry_id}_{device_id}"

        # Device info groups entities
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name="My Device",
            manufacturer="Acme Corp",
            model="Model X",
            sw_version="1.0.0",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
```

---

## Using CoordinatorEntity

Most entities should extend `CoordinatorEntity` for automatic updates.

```python
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class MySensor(CoordinatorEntity, SensorEntity):
    """Sensor with coordinator."""

    def __init__(self, coordinator: MyCoordinator, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temperature"
        self._attr_name = "Temperature"

    @property
    def native_value(self) -> float | None:
        """Return current value."""
        return self.coordinator.data.get("temperature")
```

---

## Entity Categories

```python
from homeassistant.helpers.entity import EntityCategory

# Categories
EntityCategory.CONFIG      # Configuration entities (settings)
EntityCategory.DIAGNOSTIC  # Diagnostic entities (status, debug info)
# None = Primary entity (default)
```

---

## Entity Platforms Reference

### Sensor

Represents numeric/text values.

```python
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPower,
    UnitOfEnergy,
    PERCENTAGE,
)


class MyTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True
    _attr_name = "Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.coordinator.data.get("temperature")


class MyEnergySensor(CoordinatorEntity, SensorEntity):
    """Energy sensor (for energy dashboard)."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
```

**SensorDeviceClass values:**

| Class | Description |
|-------|-------------|
| `APPARENT_POWER` | Apparent power (VA) |
| `AQI` | Air quality index |
| `ATMOSPHERIC_PRESSURE` | Pressure (Pa, hPa, bar) |
| `BATTERY` | Battery level (%) |
| `CO` | Carbon monoxide (ppm) |
| `CO2` | Carbon dioxide (ppm) |
| `CURRENT` | Current (A, mA) |
| `DATA_RATE` | Data rate (bit/s, kB/s) |
| `DATA_SIZE` | Data size (bit, kB, MB) |
| `DATE` | Date |
| `DISTANCE` | Distance (m, cm, mm, km) |
| `DURATION` | Duration (s, ms, min, h, d) |
| `ENERGY` | Energy (Wh, kWh, MWh) |
| `ENERGY_STORAGE` | Stored energy (Wh, kWh) |
| `ENUM` | Enumeration |
| `FREQUENCY` | Frequency (Hz, kHz, MHz) |
| `GAS` | Gas volume (m³, ft³) |
| `HUMIDITY` | Humidity (%) |
| `ILLUMINANCE` | Illuminance (lx) |
| `IRRADIANCE` | Irradiance (W/m²) |
| `MOISTURE` | Moisture (%) |
| `MONETARY` | Money |
| `NITROGEN_DIOXIDE` | NO₂ (µg/m³) |
| `NITROGEN_MONOXIDE` | NO (µg/m³) |
| `NITROUS_OXIDE` | N₂O (µg/m³) |
| `OZONE` | O₃ (µg/m³) |
| `PH` | pH value |
| `PM1` | PM1 (µg/m³) |
| `PM10` | PM10 (µg/m³) |
| `PM25` | PM2.5 (µg/m³) |
| `POWER` | Power (W, kW) |
| `POWER_FACTOR` | Power factor (%, None) |
| `PRECIPITATION` | Precipitation (cm, mm, in) |
| `PRECIPITATION_INTENSITY` | Precipitation rate |
| `PRESSURE` | Pressure (Pa, hPa, kPa, bar) |
| `REACTIVE_POWER` | Reactive power (var) |
| `SIGNAL_STRENGTH` | Signal strength (dB, dBm) |
| `SOUND_PRESSURE` | Sound pressure (dB, dBA) |
| `SPEED` | Speed (m/s, km/h, mph) |
| `SULPHUR_DIOXIDE` | SO₂ (µg/m³) |
| `TEMPERATURE` | Temperature (°C, °F, K) |
| `TIMESTAMP` | Timestamp |
| `VOLATILE_ORGANIC_COMPOUNDS` | VOC (µg/m³) |
| `VOLTAGE` | Voltage (V, mV) |
| `VOLUME` | Volume (L, mL, gal, ft³, m³) |
| `VOLUME_FLOW_RATE` | Flow rate |
| `VOLUME_STORAGE` | Volume storage |
| `WATER` | Water volume (L, gal, m³, ft³) |
| `WEIGHT` | Weight (kg, g, lb, oz) |
| `WIND_SPEED` | Wind speed (m/s, km/h) |

**SensorStateClass values:**

| Class | Description |
|-------|-------------|
| `MEASUREMENT` | Current value (temperature) |
| `TOTAL` | Total that can reset (rain gauge) |
| `TOTAL_INCREASING` | Monotonically increasing (energy meter) |

---

### Binary Sensor

On/off state sensors.

```python
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)


class MyMotionSensor(CoordinatorEntity, BinarySensorEntity):
    """Motion sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_has_entity_name = True
    _attr_name = "Motion"

    @property
    def is_on(self) -> bool | None:
        """Return true if motion detected."""
        return self.coordinator.data.get("motion")
```

**BinarySensorDeviceClass values:**

| Class | On Meaning |
|-------|------------|
| `BATTERY` | Low battery |
| `BATTERY_CHARGING` | Charging |
| `CO` | CO detected |
| `COLD` | Cold |
| `CONNECTIVITY` | Connected |
| `DOOR` | Open |
| `GARAGE_DOOR` | Open |
| `GAS` | Gas detected |
| `HEAT` | Hot |
| `LIGHT` | Light detected |
| `LOCK` | Unlocked |
| `MOISTURE` | Wet |
| `MOTION` | Motion detected |
| `MOVING` | Moving |
| `OCCUPANCY` | Occupied |
| `OPENING` | Open |
| `PLUG` | Plugged in |
| `POWER` | Power detected |
| `PRESENCE` | Present |
| `PROBLEM` | Problem detected |
| `RUNNING` | Running |
| `SAFETY` | Unsafe |
| `SMOKE` | Smoke detected |
| `SOUND` | Sound detected |
| `TAMPER` | Tampered |
| `UPDATE` | Update available |
| `VIBRATION` | Vibration detected |
| `WINDOW` | Open |

---

### Switch

Controllable on/off entities.

```python
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass


class MySwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity."""

    _attr_device_class = SwitchDeviceClass.OUTLET
    _attr_has_entity_name = True
    _attr_name = "Power"

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self.coordinator.data.get("power")

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on."""
        await self.coordinator.client.async_set_power(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off."""
        await self.coordinator.client.async_set_power(False)
        await self.coordinator.async_request_refresh()
```

**SwitchDeviceClass values:** `OUTLET`, `SWITCH`

---

### Light

Lighting control.

```python
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ATTR_COLOR_TEMP_KELVIN,
)


class MyLight(CoordinatorEntity, LightEntity):
    """Light entity."""

    _attr_has_entity_name = True
    _attr_name = "Light"
    _attr_supported_color_modes = {ColorMode.RGB, ColorMode.COLOR_TEMP}

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self.coordinator.data.get("on")

    @property
    def brightness(self) -> int | None:
        """Return brightness (0-255)."""
        return self.coordinator.data.get("brightness")

    @property
    def color_mode(self) -> ColorMode | None:
        """Return current color mode."""
        if self.coordinator.data.get("rgb"):
            return ColorMode.RGB
        return ColorMode.COLOR_TEMP

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return RGB color."""
        return self.coordinator.data.get("rgb")

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return color temperature in Kelvin."""
        return self.coordinator.data.get("color_temp")

    @property
    def min_color_temp_kelvin(self) -> int:
        """Return min color temp."""
        return 2700

    @property
    def max_color_temp_kelvin(self) -> int:
        """Return max color temp."""
        return 6500

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        rgb = kwargs.get(ATTR_RGB_COLOR)
        color_temp = kwargs.get(ATTR_COLOR_TEMP_KELVIN)

        await self.coordinator.client.async_set_light(
            on=True,
            brightness=brightness,
            rgb=rgb,
            color_temp=color_temp,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off."""
        await self.coordinator.client.async_set_light(on=False)
        await self.coordinator.async_request_refresh()
```

**ColorMode values:**

| Mode | Description |
|------|-------------|
| `ONOFF` | On/off only |
| `BRIGHTNESS` | Brightness only |
| `COLOR_TEMP` | Color temperature |
| `HS` | Hue/Saturation |
| `XY` | CIE XY color |
| `RGB` | RGB color |
| `RGBW` | RGBW color |
| `RGBWW` | RGBWW color |
| `WHITE` | White mode |

---

### Climate

HVAC/thermostat control.

```python
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)
from homeassistant.const import UnitOfTemperature


class MyThermostat(CoordinatorEntity, ClimateEntity):
    """Thermostat entity."""

    _attr_has_entity_name = True
    _attr_name = "Thermostat"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
    )
    _attr_fan_modes = ["auto", "low", "medium", "high"]
    _attr_preset_modes = ["home", "away", "sleep"]
    _attr_min_temp = 15
    _attr_max_temp = 30
    _attr_target_temperature_step = 0.5

    @property
    def current_temperature(self) -> float | None:
        """Return current temperature."""
        return self.coordinator.data.get("current_temp")

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        return self.coordinator.data.get("target_temp")

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current HVAC mode."""
        mode = self.coordinator.data.get("mode")
        return HVACMode(mode) if mode else None

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action."""
        if self.coordinator.data.get("heating"):
            return HVACAction.HEATING
        if self.coordinator.data.get("cooling"):
            return HVACAction.COOLING
        return HVACAction.IDLE

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        await self.coordinator.client.async_set_mode(hvac_mode.value)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set target temperature."""
        temp = kwargs.get("temperature")
        await self.coordinator.client.async_set_temperature(temp)
        await self.coordinator.async_request_refresh()
```

---

### Cover

Blinds, garage doors, etc.

```python
from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature,
    CoverDeviceClass,
)


class MyBlind(CoordinatorEntity, CoverEntity):
    """Blind cover entity."""

    _attr_device_class = CoverDeviceClass.BLIND
    _attr_has_entity_name = True
    _attr_name = "Blind"
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    @property
    def is_closed(self) -> bool | None:
        """Return if cover is closed."""
        return self.current_cover_position == 0

    @property
    def current_cover_position(self) -> int | None:
        """Return current position (0-100)."""
        return self.coordinator.data.get("position")

    async def async_open_cover(self, **kwargs) -> None:
        """Open cover."""
        await self.coordinator.client.async_set_position(100)
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs) -> None:
        """Close cover."""
        await self.coordinator.client.async_set_position(0)
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop cover."""
        await self.coordinator.client.async_stop()
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs) -> None:
        """Set cover position."""
        position = kwargs.get("position")
        await self.coordinator.client.async_set_position(position)
        await self.coordinator.async_request_refresh()
```

**CoverDeviceClass values:** `AWNING`, `BLIND`, `CURTAIN`, `DAMPER`, `DOOR`, `GARAGE`, `GATE`, `SHADE`, `SHUTTER`, `WINDOW`

---

### Button

One-time actions.

```python
from homeassistant.components.button import ButtonEntity, ButtonDeviceClass


class MyRestartButton(CoordinatorEntity, ButtonEntity):
    """Restart button."""

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_has_entity_name = True
    _attr_name = "Restart"
    _attr_entity_category = EntityCategory.CONFIG

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.client.async_restart()
```

**ButtonDeviceClass values:** `IDENTIFY`, `RESTART`, `UPDATE`

---

### Number

Numeric input/control.

```python
from homeassistant.components.number import NumberEntity, NumberMode


class MyBrightnessControl(CoordinatorEntity, NumberEntity):
    """Brightness control."""

    _attr_has_entity_name = True
    _attr_name = "Brightness"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current value."""
        return self.coordinator.data.get("brightness")

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self.coordinator.client.async_set_brightness(int(value))
        await self.coordinator.async_request_refresh()
```

---

### Select

Dropdown selection.

```python
from homeassistant.components.select import SelectEntity


class MyModeSelect(CoordinatorEntity, SelectEntity):
    """Mode selection."""

    _attr_has_entity_name = True
    _attr_name = "Mode"
    _attr_options = ["auto", "manual", "eco", "boost"]

    @property
    def current_option(self) -> str | None:
        """Return current option."""
        return self.coordinator.data.get("mode")

    async def async_select_option(self, option: str) -> None:
        """Select option."""
        await self.coordinator.client.async_set_mode(option)
        await self.coordinator.async_request_refresh()
```

---

### Text

Text input.

```python
from homeassistant.components.text import TextEntity, TextMode


class MyNameText(CoordinatorEntity, TextEntity):
    """Text entity for device name."""

    _attr_has_entity_name = True
    _attr_name = "Device Name"
    _attr_mode = TextMode.TEXT
    _attr_native_min = 1
    _attr_native_max = 32

    @property
    def native_value(self) -> str | None:
        """Return current value."""
        return self.coordinator.data.get("name")

    async def async_set_value(self, value: str) -> None:
        """Set new value."""
        await self.coordinator.client.async_set_name(value)
        await self.coordinator.async_request_refresh()
```

---

### Lock

Lock control.

```python
from homeassistant.components.lock import LockEntity


class MyLock(CoordinatorEntity, LockEntity):
    """Lock entity."""

    _attr_has_entity_name = True
    _attr_name = "Lock"

    @property
    def is_locked(self) -> bool | None:
        """Return true if locked."""
        return self.coordinator.data.get("locked")

    @property
    def is_locking(self) -> bool | None:
        """Return true if locking."""
        return self.coordinator.data.get("locking")

    @property
    def is_unlocking(self) -> bool | None:
        """Return true if unlocking."""
        return self.coordinator.data.get("unlocking")

    async def async_lock(self, **kwargs) -> None:
        """Lock."""
        await self.coordinator.client.async_lock()
        await self.coordinator.async_request_refresh()

    async def async_unlock(self, **kwargs) -> None:
        """Unlock."""
        await self.coordinator.client.async_unlock()
        await self.coordinator.async_request_refresh()
```

---

### Fan

Fan control.

```python
from homeassistant.components.fan import FanEntity, FanEntityFeature


class MyFan(CoordinatorEntity, FanEntity):
    """Fan entity."""

    _attr_has_entity_name = True
    _attr_name = "Fan"
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.OSCILLATE
        | FanEntityFeature.PRESET_MODE
    )
    _attr_speed_count = 3
    _attr_preset_modes = ["auto", "sleep", "nature"]

    @property
    def is_on(self) -> bool | None:
        """Return true if on."""
        return self.coordinator.data.get("on")

    @property
    def percentage(self) -> int | None:
        """Return speed percentage."""
        return self.coordinator.data.get("speed")

    @property
    def oscillating(self) -> bool | None:
        """Return oscillating state."""
        return self.coordinator.data.get("oscillating")

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs,
    ) -> None:
        """Turn on."""
        await self.coordinator.client.async_turn_on(
            speed=percentage,
            preset=preset_mode,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off."""
        await self.coordinator.client.async_turn_off()
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set speed."""
        await self.coordinator.client.async_set_speed(percentage)
        await self.coordinator.async_request_refresh()

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillating."""
        await self.coordinator.client.async_set_oscillating(oscillating)
        await self.coordinator.async_request_refresh()
```

---

### Media Player

Media device control.

```python
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)


class MyMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Media player entity."""

    _attr_has_entity_name = True
    _attr_name = "Player"
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
    )

    @property
    def state(self) -> MediaPlayerState | None:
        """Return current state."""
        state = self.coordinator.data.get("state")
        return MediaPlayerState(state) if state else None

    @property
    def volume_level(self) -> float | None:
        """Return volume (0-1)."""
        return self.coordinator.data.get("volume")

    @property
    def is_volume_muted(self) -> bool | None:
        """Return muted state."""
        return self.coordinator.data.get("muted")

    @property
    def media_title(self) -> str | None:
        """Return current track title."""
        return self.coordinator.data.get("title")

    @property
    def media_artist(self) -> str | None:
        """Return current artist."""
        return self.coordinator.data.get("artist")

    async def async_media_play(self) -> None:
        """Play."""
        await self.coordinator.client.async_play()
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Pause."""
        await self.coordinator.client.async_pause()
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume."""
        await self.coordinator.client.async_set_volume(volume)
        await self.coordinator.async_request_refresh()
```

---

### Camera

Camera streaming.

```python
from homeassistant.components.camera import Camera, CameraEntityFeature


class MyCamera(CoordinatorEntity, Camera):
    """Camera entity."""

    _attr_has_entity_name = True
    _attr_name = "Camera"
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, coordinator, entry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        Camera.__init__(self)
        self._attr_unique_id = f"{entry.entry_id}_camera"

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from camera."""
        return await self.coordinator.client.async_get_snapshot()

    async def stream_source(self) -> str | None:
        """Return stream source URL."""
        return self.coordinator.data.get("stream_url")
```

---

### Vacuum

Robot vacuum control.

```python
from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
)


class MyVacuum(CoordinatorEntity, StateVacuumEntity):
    """Vacuum entity."""

    _attr_has_entity_name = True
    _attr_name = "Vacuum"
    _attr_supported_features = (
        VacuumEntityFeature.START
        | VacuumEntityFeature.STOP
        | VacuumEntityFeature.PAUSE
        | VacuumEntityFeature.RETURN_HOME
        | VacuumEntityFeature.BATTERY
        | VacuumEntityFeature.FAN_SPEED
    )
    _attr_fan_speed_list = ["quiet", "normal", "turbo"]

    @property
    def state(self) -> str | None:
        """Return current state."""
        return self.coordinator.data.get("state")

    @property
    def battery_level(self) -> int | None:
        """Return battery level."""
        return self.coordinator.data.get("battery")

    @property
    def fan_speed(self) -> str | None:
        """Return fan speed."""
        return self.coordinator.data.get("fan_speed")

    async def async_start(self) -> None:
        """Start cleaning."""
        await self.coordinator.client.async_start()
        await self.coordinator.async_request_refresh()

    async def async_return_to_base(self, **kwargs) -> None:
        """Return to dock."""
        await self.coordinator.client.async_dock()
        await self.coordinator.async_request_refresh()
```

---

### Other Entity Platforms

| Platform | Base Class | Purpose |
|----------|------------|---------|
| `alarm_control_panel` | `AlarmControlPanelEntity` | Security panels |
| `calendar` | `CalendarEntity` | Calendar events |
| `device_tracker` | `ScannerEntity` / `TrackerEntity` | Presence detection |
| `event` | `EventEntity` | Event notifications |
| `humidifier` | `HumidifierEntity` | Humidity control |
| `image` | `ImageEntity` | Static images |
| `lawn_mower` | `LawnMowerEntity` | Lawn mower control |
| `notify` | `NotifyEntity` | Notifications |
| `remote` | `RemoteEntity` | Remote control |
| `scene` | `Scene` | Scene activation |
| `siren` | `SirenEntity` | Sirens/alarms |
| `stt` | `SpeechToTextEntity` | Speech to text |
| `tts` | `TextToSpeechEntity` | Text to speech |
| `todo` | `TodoListEntity` | Task lists |
| `update` | `UpdateEntity` | Firmware updates |
| `valve` | `ValveEntity` | Valve control |
| `wake_word` | `WakeWordDetectionEntity` | Wake word detection |
| `water_heater` | `WaterHeaterEntity` | Water heater control |
| `weather` | `WeatherEntity` | Weather data |

---

### Event Entity (HA 2024+)

Represents discrete events (button presses, doorbell rings).

```python
from homeassistant.components.event import (
    EventEntity,
    EventDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class MyButtonEvent(CoordinatorEntity, EventEntity):
    """Event entity for button presses."""

    _attr_device_class = EventDeviceClass.BUTTON
    _attr_event_types = ["single_press", "double_press", "long_press"]
    _attr_has_entity_name = True
    _attr_name = "Button"

    def __init__(self, coordinator, entry, device_id: str) -> None:
        """Initialize event entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{entry.entry_id}_{device_id}_button"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from coordinator."""
        event = self.coordinator.data.get(f"{self._device_id}_event")
        if event:
            # Trigger the event with type and optional attributes
            self._trigger_event(
                event["type"],
                {
                    "timestamp": event.get("timestamp"),
                    "button_id": event.get("button_id"),
                },
            )
        super()._handle_coordinator_update()


class MyDoorbellEvent(CoordinatorEntity, EventEntity):
    """Event entity for doorbell."""

    _attr_device_class = EventDeviceClass.DOORBELL
    _attr_event_types = ["ring", "motion"]
    _attr_has_entity_name = True
    _attr_name = "Doorbell"

    def trigger_ring(self) -> None:
        """Trigger doorbell ring event."""
        self._trigger_event("ring", {"source": "front_door"})


# From websocket/push handler
def on_device_event(event_type: str, device_id: str) -> None:
    """Handle device event from external source."""
    # Find the event entity and trigger it
    entity = get_event_entity(device_id)
    entity._trigger_event(event_type)
```

**EventDeviceClass values:**

| Class | Description |
|-------|-------------|
| `BUTTON` | Button press events |
| `DOORBELL` | Doorbell ring events |
| `MOTION` | Motion detection events |

---

### Todo Entity (HA 2024+)

Represents task/todo lists.

```python
from homeassistant.components.todo import (
    TodoListEntity,
    TodoItem,
    TodoItemStatus,
    TodoListEntityFeature,
)


class MyTodoList(CoordinatorEntity, TodoListEntity):
    """Todo list entity."""

    _attr_has_entity_name = True
    _attr_name = "Tasks"
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.SET_DUE_DATE_ON_ITEM
    )

    def __init__(self, coordinator, entry) -> None:
        """Initialize todo list."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_tasks"

    @property
    def todo_items(self) -> list[TodoItem]:
        """Return todo items."""
        items = []
        for task in self.coordinator.data.get("tasks", []):
            items.append(
                TodoItem(
                    uid=task["id"],
                    summary=task["title"],
                    status=(
                        TodoItemStatus.COMPLETED
                        if task.get("completed")
                        else TodoItemStatus.NEEDS_ACTION
                    ),
                    due=task.get("due_date"),
                    description=task.get("description"),
                )
            )
        return items

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a new todo item."""
        await self.coordinator.client.async_create_task(
            title=item.summary,
            due_date=item.due,
            description=item.description,
        )
        await self.coordinator.async_request_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update a todo item."""
        await self.coordinator.client.async_update_task(
            task_id=item.uid,
            title=item.summary,
            completed=item.status == TodoItemStatus.COMPLETED,
            due_date=item.due,
        )
        await self.coordinator.async_request_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete todo items."""
        for uid in uids:
            await self.coordinator.client.async_delete_task(uid)
        await self.coordinator.async_request_refresh()

    async def async_move_todo_item(
        self, uid: str, previous_uid: str | None = None
    ) -> None:
        """Move/reorder a todo item."""
        await self.coordinator.client.async_reorder_task(uid, after=previous_uid)
        await self.coordinator.async_request_refresh()
```

**TodoListEntityFeature values:**

| Feature | Description |
|---------|-------------|
| `CREATE_TODO_ITEM` | Can create new items |
| `DELETE_TODO_ITEM` | Can delete items |
| `UPDATE_TODO_ITEM` | Can update items |
| `MOVE_TODO_ITEM` | Can reorder items |
| `SET_DUE_DATE_ON_ITEM` | Supports due dates |
| `SET_DUE_DATETIME_ON_ITEM` | Supports due datetime |
| `SET_DESCRIPTION_ON_ITEM` | Supports descriptions |

---

## Device Info

Group entities under devices.

```python
from homeassistant.helpers.entity import DeviceInfo

device_info = DeviceInfo(
    # At least one identifier required
    identifiers={(DOMAIN, "unique_device_id")},

    # Optional but recommended
    name="My Device",
    manufacturer="Acme Corp",
    model="Model X",
    model_id="MX-001",
    sw_version="1.0.0",
    hw_version="2.0",
    serial_number="ABC123",

    # Connection info (alternative identifier)
    connections={("mac", "AA:BB:CC:DD:EE:FF")},

    # Links
    configuration_url="http://192.168.1.100/settings",

    # Device via another device
    via_device=(DOMAIN, "parent_device_id"),

    # Suggested area
    suggested_area="Living Room",
)
```

---

## Extra State Attributes

```python
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_BATTERY_LEVEL,
)


class MySensor(CoordinatorEntity, SensorEntity):
    """Sensor with extra attributes."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        return {
            ATTR_ATTRIBUTION: "Data provided by My Service",
            "last_update": self.coordinator.data.get("timestamp"),
            "raw_value": self.coordinator.data.get("raw"),
        }
```

---

## Availability

```python
class MyEntity(CoordinatorEntity, SensorEntity):
    """Entity with availability."""

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Check coordinator success
        if not self.coordinator.last_update_success:
            return False

        # Check specific device availability
        device_data = self.coordinator.data.get(self._device_id)
        if device_data is None:
            return False

        return device_data.get("online", False)
```

---

## Best Practices

### DO

- Always set `unique_id` (required for entity customization)
- Use `_attr_has_entity_name = True` for proper naming
- Inherit from `CoordinatorEntity` for automatic updates
- Set appropriate `device_class` for automatic icons/units
- Use `EntityCategory` for config/diagnostic entities
- Group entities with `DeviceInfo`

### DON'T

- Create entities without `unique_id`
- Use blocking I/O in entity methods
- Poll in entity properties (use coordinator)
- Hardcode entity names (use translation keys)
- Return stale data in properties

---

For data coordination, see `coordinator.md`.
For device registry, see `device-registry.md`.
