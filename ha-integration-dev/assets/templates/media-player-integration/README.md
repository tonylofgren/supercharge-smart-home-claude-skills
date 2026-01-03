# Media Player Integration Template

Template for integrations that control media playback devices (speakers, TVs, streaming boxes).

## Features

- **Full Media Player Entity**: Play, pause, volume, source selection
- **Media Browser**: Browse media libraries and playlists
- **Media Type Support**: Music, video, TV, podcasts
- **Coordinator Pattern**: Efficient state polling

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration setup |
| `config_flow.py` | Device discovery and setup |
| `coordinator.py` | State polling |
| `media_player.py` | Full media player entity |
| `const.py` | Constants and supported features |
| `manifest.json` | Integration metadata |
| `strings.json` | UI strings |

## Customization Steps

### 1. Define Supported Features

In `media_player.py`:
```python
_attr_supported_features = (
    MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.BROWSE_MEDIA
)
```

### 2. Implement Playback Controls

```python
async def async_media_play(self):
    await self.coordinator.api.play()
    await self.coordinator.async_request_refresh()

async def async_media_pause(self):
    await self.coordinator.api.pause()
    await self.coordinator.async_request_refresh()

async def async_set_volume_level(self, volume):
    await self.coordinator.api.set_volume(int(volume * 100))
    await self.coordinator.async_request_refresh()
```

### 3. Add Source Selection

```python
@property
def source_list(self):
    return ["TV", "HDMI 1", "Bluetooth", "Spotify"]

@property
def source(self):
    return self.coordinator.data.get("current_source")

async def async_select_source(self, source):
    await self.coordinator.api.select_source(source)
```

### 4. Implement Media Browser

```python
async def async_browse_media(self, media_content_type=None, media_content_id=None):
    if media_content_id is None:
        # Return root
        return BrowseMedia(
            title="Library",
            media_class=MediaClass.DIRECTORY,
            media_content_type="library",
            media_content_id="",
            can_play=False,
            can_expand=True,
            children=[
                BrowseMedia(
                    title="Playlists",
                    media_class=MediaClass.PLAYLIST,
                    ...
                ),
            ],
        )
    # Fetch content for media_content_id
    return await self._build_browse_item(media_content_id)
```

### 5. Add Now Playing Info

```python
@property
def media_title(self):
    return self.coordinator.data.get("track_name")

@property
def media_artist(self):
    return self.coordinator.data.get("artist")

@property
def media_album_name(self):
    return self.coordinator.data.get("album")

@property
def media_image_url(self):
    return self.coordinator.data.get("artwork_url")

@property
def media_duration(self):
    return self.coordinator.data.get("duration")

@property
def media_position(self):
    return self.coordinator.data.get("position")
```

## Media Player Patterns

### Basic Player (Play/Pause/Volume)

Minimum implementation:
```python
_attr_supported_features = (
    MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.VOLUME_SET
)
```

### Full-Featured Player

With browsing, queue, and seeking:
```python
_attr_supported_features = (
    MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.SEEK
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.BROWSE_MEDIA
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.SHUFFLE_SET
    | MediaPlayerEntityFeature.REPEAT_SET
)
```

### TV/Video Player

With channel support:
```python
_attr_device_class = MediaPlayerDeviceClass.TV
_attr_supported_features |= (
    MediaPlayerEntityFeature.SELECT_SOURCE  # Input source
)
```

## When to Use This Template

- Smart speakers (Sonos, Google Home)
- Streaming devices (Chromecast, Roku)
- TVs and receivers
- Music players and streamers

## Resources

- [Media Player Entity](https://developers.home-assistant.io/docs/core/entity/media-player)
- [Media Browser](https://developers.home-assistant.io/docs/core/entity/media-player#media-browser)
- [MediaClass](https://developers.home-assistant.io/docs/core/entity/media-player#mediaclass)

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
