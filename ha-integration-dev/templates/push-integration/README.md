# Push Integration Template

Template for integrations that receive real-time updates via WebSocket or Server-Sent Events (SSE).

## Features

- **WebSocket Support**: Real-time bidirectional communication
- **Auto-Reconnect**: Handles connection drops gracefully
- **CoordinatorEntity**: Automatic entity state updates
- **Fallback Polling**: Optional polling when WebSocket unavailable

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration setup, WebSocket initialization |
| `coordinator.py` | WebSocket handler with reconnect logic |
| `const.py` | Constants and WebSocket URL |
| `manifest.json` | Integration metadata |

## Customization Steps

### 1. Configure WebSocket URL

In `const.py`:
```python
WEBSOCKET_URL = "wss://api.example.com/ws"
```

### 2. Handle Incoming Messages

In `coordinator.py`:
```python
async def _handle_message(self, message):
    data = json.loads(message)
    if data["type"] == "state_update":
        self.async_set_updated_data(data["payload"])
```

### 3. Implement Authentication

```python
async def _connect_websocket(self):
    async with websockets.connect(self._url) as ws:
        # Authenticate
        await ws.send(json.dumps({"token": self._api_key}))
        auth_response = await ws.recv()
        if not json.loads(auth_response).get("success"):
            raise ConfigEntryAuthFailed("WebSocket auth failed")
        # Listen for messages
        async for message in ws:
            await self._handle_message(message)
```

### 4. Add Reconnect Logic

```python
async def _websocket_loop(self):
    while True:
        try:
            await self._connect_websocket()
        except websockets.ConnectionClosed:
            _LOGGER.warning("WebSocket disconnected, reconnecting...")
            await asyncio.sleep(5)
        except Exception as err:
            _LOGGER.error("WebSocket error: %s", err)
            await asyncio.sleep(30)
```

## Patterns

### WebSocket Only

For devices/APIs that only support WebSocket:
```python
# No update_interval in coordinator
# All updates come from WebSocket
```

### WebSocket + Polling Fallback

For reliability:
```python
# Set update_interval as fallback
update_interval=timedelta(minutes=5)

# Primary updates from WebSocket
# Polling only if WebSocket fails
```

### Event-Based Updates

For APIs that send events:
```python
async def _handle_event(self, event):
    self.hass.bus.async_fire(
        f"{DOMAIN}_event",
        {"type": event["type"], "data": event["data"]}
    )
```

## When to Use This Template

- APIs with WebSocket endpoints
- Real-time device updates
- Low-latency requirements
- Server-Sent Events (SSE)

## Resources

- [Python websockets library](https://websockets.readthedocs.io/)
- [aiohttp WebSocket](https://docs.aiohttp.org/en/stable/client_quickstart.html#websockets)

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
