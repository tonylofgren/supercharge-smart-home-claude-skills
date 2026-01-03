# Polling Integration Template

Template for integrations that poll a cloud or local API at regular intervals using DataUpdateCoordinator.

## Features

- **DataUpdateCoordinator**: Centralized data fetching with automatic refresh
- **Error Handling**: Retry logic and ConfigEntryNotReady support
- **EntityDescription Pattern**: Easy to add multiple sensors
- **Async/Await**: Proper async API calls

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration setup, coordinator initialization |
| `coordinator.py` | DataUpdateCoordinator with polling logic |
| `sensor.py` | Sensor entities with EntityDescription |
| `const.py` | Constants, update interval |
| `manifest.json` | Integration metadata with requirements |

## Customization Steps

### 1. Configure Update Interval

In `const.py`:
```python
UPDATE_INTERVAL = timedelta(seconds=30)  # Adjust as needed
```

### 2. Implement API Call

In `coordinator.py`:
```python
async def _async_update_data(self):
    try:
        async with async_timeout.timeout(10):
            return await self.api.fetch_data()
    except ApiError as err:
        raise UpdateFailed(f"Error: {err}")
```

### 3. Define Sensor Descriptions

In `sensor.py`:
```python
SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Add more sensors...
]
```

### 4. Map Data to Sensors

In `sensor.py`:
```python
@property
def native_value(self):
    return self.coordinator.data.get(self.entity_description.key)
```

## Error Handling Patterns

### Temporary Failures (retry)

```python
except ConnectionError as err:
    raise UpdateFailed(f"Connection failed: {err}")
```

### Authentication Failures (trigger reauth)

```python
except AuthenticationError as err:
    raise ConfigEntryAuthFailed from err
```

### Rate Limiting

```python
self._rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
if self._rate_limit_remaining == 0:
    await asyncio.sleep(60)  # Wait for rate limit reset
```

## When to Use This Template

- Cloud APIs with polling endpoints
- Local devices without push notifications
- Any API that requires periodic fetching

## Resources

- [DataUpdateCoordinator Documentation](https://developers.home-assistant.io/docs/integration_fetching_data)
- [Entity Registry](https://developers.home-assistant.io/docs/entity_registry_index)

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
