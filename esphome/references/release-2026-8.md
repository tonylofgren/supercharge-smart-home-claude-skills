# ESPHome 2026.8.0 - Complete Release Reference (August 2026)

**Release date:** August 19, 2026 (2026.8.0), with a patch release 2026.8.1 on August 24, 2026
**Source:** https://esphome.io/changelog/2026.8.0/

When the user is on this version, upgrading TO it, or asking "what's new", read this file BEFORE generating YAML. Bluetooth Low Energy stops being ESP32-only, several BLE and sensor keys are renamed, addressable LED strips move to a single `channel_colors` key, and Modbus gets another round of changes on top of the 2026.7.0 rewrite.

---

## What landed in 2026.8.0 at a glance

Bluetooth on more chips than ever is the headline. Eight themes worth knowing before you upgrade:

1. **BLE is no longer ESP32-only.** A new platform-neutral `ble_device_base` layer replaces the ESP32-specific foundation the 39 existing BLE sensor platforms sat on. Raspberry Pi Pico W/2 W, Beken BK72xx (common in Tuya switches, thermostats, plugs), and LibreTiny LN882H all gain BLE scanning trackers.
2. **BLE key rename.** `esp32_ble_id` becomes `ble_hub_id` across every advertisement-based BLE platform (presence, RSSI, scanner, BTHome, Xiaomi/mi-thermometer, Ruuvi, Mopeka, and more). The old key still works with a warning.
3. **Gas-index sensors renamed.** SGP4x and SEN5x/SEN6x `voc`/`nox` keys become `voc_index`/`nox_index`, matching what they actually publish (a unitless index, not a concentration). Auto-migrates with a warning.
4. **LED strips get one color key.** `esp32_rmt_led_strip`, `beken_spi_led_strip`, and `rp2040_pio_led_strip` replace `rgb_order`/`is_rgbw`/`is_wrgb` with a single `channel_colors` key that takes any RGB permutation plus an optional `W`.
5. **Dual Ethernet + WiFi on ESP32.** A `network: priority:` list picks the preferred interface, with runtime arbitration and automatic failover/failback on link change.
6. **Nine new components.** A platform-neutral BLE layer plus trackers for three more chip families, a 60 GHz presence radar, a Hörmann garage door cover, a DS248x 1-Wire bridge, nRF52 PWM output, and an ad-hoc Modbus transaction component for automations.
7. **Modbus keeps evolving.** Fair queue sharing across controllers, per-device offline tracking, server-mode coil/discrete-input support and function code 0x17, and two more deprecated no-op options (`command_throttle`, `allow_duplicate_commands`).
8. **Faster builds, smaller installs.** `ccache` now covers ESP8266, LibreTiny, RP2040, and host builds. A fresh ESP-IDF install only pulls toolchains for the variants you actually build, roughly halving install size.

---

## Upgrade Checklist (run through this BEFORE flashing 2026.8.0)

- [ ] Set `esp32_ble_id:` on a BLE presence/RSSI/scanner/BTHome/Xiaomi/Ruuvi/Mopeka sensor? -> rename to `ble_hub_id`. The old key keeps working with a warning until 2027.2.0.
- [ ] Read `voc:` or `nox:` from an SGP4x, SEN5x, or SEN6x sensor? -> rename to `voc_index:` / `nox_index:`. Auto-migrates with a warning until 2027.2.0; update the key when you touch the config next.
- [ ] Use `rgb_order:`, `is_rgbw:`, or `is_wrgb:` on `esp32_rmt_led_strip`, `beken_spi_led_strip`, or `rp2040_pio_led_strip`? -> combine into a single `channel_colors:` key (e.g. `GRB`, `GRBW`, `WRGB`). Old keys work with a warning until 2027.3.0.
- [ ] Parse a 23-byte Apple manufacturer payload as an iBeacon? -> it must now carry the 0x02/0x15 iBeacon sub-type prefix to be recognized. Non-iBeacon Apple payloads of the same length no longer false-match.
- [ ] Rely on an AQI sensor pinning flat above 301 US AQI / 101 CAQI? -> it now interpolates past the top of the scale instead of capping.
- [ ] Use `ease_in`/`ease_out` LVGL animation weights above 1.0? -> these are now validation errors, not silently clamped.
- [ ] Assume RC522 over I2C defaults to address `0x2C`? -> the default is now `0x28`. Add `address: 0x2C` explicitly if your hardware is wired to the old default.
- [ ] Set `inverted: true` or `allow_other_uses: true` on `interrupt_pin` for `pcf8574`, `pca9554`, `tca9555`, `pca6416a`, `pi4ioe5v6408`, or `mcp23016`? -> remove them; both are now validation errors on those expanders.
- [ ] Use `command_throttle` or `allow_duplicate_commands` on `modbus_controller`? -> remove them (no-ops now); use `turnaround_time` on the `modbus` hub instead.
- [ ] Read a `custom_command: [0x17, ...]` Modbus response by `offset:`? -> subtract 1 from your offsets; the leading byte-count byte is no longer included.
- [ ] Run a `modbus_server` with `address: 0`? -> that address is now reserved for broadcast and will fail validation.
- [ ] Have a frontend or integration reading raw `web_server` JSON? -> the `id` field is now always `{domain}/{device?}/{name}` (the transitional `name_id` field is gone), and `alarm_control_panel` domain strings use underscores instead of hyphens.
- [ ] External component calls `cv.parse_esphome_version`? -> switch to `cv.require_esphome_version`; the old helper is a deprecated alias slated for removal in 2027.2.0.

---

## BLE Goes Platform-Neutral

The biggest structural change in this release: Bluetooth Low Energy scanning is no longer built on ESP32-specific foundations. A new `ble_device_base` component provides a shared advertisement layer that the 39 existing BLE sensor platforms were migrated onto, out of `esp32_ble_tracker`. Three new trackers plug into it:

- **`rp2_ble_tracker`**: passive and active BLE scanning for Raspberry Pi Pico W / Pico 2 W, running alongside a WiFi API connection.
- **`bk72xx_ble_tracker`**: BLE 5.x scanning for Beken BK72xx chips, the SoC inside many Tuya-based switches, thermostats, and plugs. Active scanning also qualifies BK72xx for Bluetooth Proxy.
- **`ln882h_ble_tracker`**: BLE 5.1 scanning with scan-response merging for LibreTiny LN882H devices.

Bluetooth Proxy itself also gained ground beyond ESP32: Pico W now supports full active BLE connections with 3 connection slots, matching ESP32 parity.

```yaml
# Pico W acting as a BLE-to-HA bridge alongside its WiFi connection
esphome:
  name: pico-ble-bridge
  friendly_name: Pico BLE Bridge

rp2040:
  board: rpipicow

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

rp2_ble_tracker:

sensor:
  - platform: ble_rssi
    mac_address: AA:BB:CC:DD:EE:FF
    name: "Tag RSSI"
    ble_hub_id: rp2_ble_tracker   # renamed from esp32_ble_id; only needed with multiple hubs
```

> Note: `ble_hub_id` is only required when more than one BLE hub is configured (for example, mixing a tracker with a proxy). A single tracker is picked up automatically.

---

## BLE and Sensor Key Renames

Two unrelated renames land together because both keys describe "which hub/what unit," and both had grown misleading names.

### `esp32_ble_id` becomes `ble_hub_id`

Every advertisement-based BLE platform picks up the new key: `ble_presence`, `ble_rssi`, `ble_scanner`, mi-thermometer, BTHome, Mopeka, Ruuvi, Airthings, Inkbird, RadonEye, ThermoPro, the Xiaomi family, `b_parasite`, and `exposure_notifications`. The rename reflects that a "hub" is no longer necessarily an ESP32 BLE tracker; it could be the new Pico, BK72xx, or LN882H trackers above. The old `esp32_ble_id` key keeps working with a deprecation warning until 2027.2.0.

```yaml
sensor:
  - platform: ble_presence
    mac_address: AA:BB:CC:DD:EE:FF
    name: "Phone Presence"
    ble_hub_id: ble_tracker   # was esp32_ble_id
```

### SGP4x / SEN5x / SEN6x: `voc`/`nox` become `voc_index`/`nox_index`

These sensors publish a unitless gas index (a relative baseline value), not a concentration in ppm or ppb. The key rename makes that explicit. Auto-migrates with a warning until 2027.2.0.

```yaml
sensor:
  - platform: sgp4x
    voc_index:        # was voc
      name: "VOC Index"
    nox_index:         # was nox
      name: "NOx Index"
    compensation:
      humidity_source: humidity_sensor
      temperature_source: temp_sensor
```

Aurora's own sensor catalog (`esphome/references/sensors.md`) documents SEN6x with `voc_index`/`nox_index` already and needed no change; SGP30, which uses unrelated `tvoc`/`eco2` keys, is a different driver and is unaffected by this rename.

---

## Addressable LED Strips: `channel_colors` Replaces Three Keys

`esp32_rmt_led_strip`, `beken_spi_led_strip`, and `rp2040_pio_led_strip` now take one `channel_colors` key instead of `rgb_order` plus the separate `is_rgbw`/`is_wrgb` flags. `channel_colors` accepts any permutation of `R`, `G`, `B`, with an optional `W` inserted anywhere: `GRB` for a plain strip, `GRBW`, `WRGB`, and so on. This also gives the RP2040 PIO strip driver white-channel positioning it did not have before. Old keys keep working with a warning until 2027.3.0.

```yaml
# Before (still works, but deprecated):
# light:
#   - platform: esp32_rmt_led_strip
#     chipset: SK6812
#     rgb_order: GRB
#     is_rgbw: true

# After:
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    rmt_channel: 0
    chipset: SK6812
    channel_colors: GRBW
    name: "SK6812 RGBW Strip"
```

Aurora's LED strip examples across `esphome/references/lights.md`, `popular-devices.md`, `voice-local.md`, `USAGE-GUIDE.md`, and `CHEATSHEET.md` were migrated to `channel_colors` as part of this release note; see the "Files touched" section at the end for the full list.

---

## Dual Ethernet + WiFi on ESP32

A new `network: priority:` list lets an ESP32 keep both an Ethernet and a WiFi interface configured and picks the preferred one for the default route. Preference is arbitrated at runtime, with automatic failover to the backup interface and failback to the preferred one within milliseconds of a link-state change, no reboot needed.

```yaml
esphome:
  name: dual-net-node
  friendly_name: Dual Net Node

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

ethernet:
  type: LAN8720
  mdc_pin: GPIO23
  mdio_pin: GPIO18

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

network:
  priority:
    - ethernet   # preferred default route
    - wifi       # automatic fallback on link loss

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
```

This is a good fit for a hub device (a garage controller, a hallway panel) wired to Ethernet but kept on WiFi as a backup path if the cable gets unplugged during a remodel.

---

## Modbus: Fairness, Offline Tracking, and Server-Mode Growth

On top of the 2026.7.0 parser rewrite, `modbus_controller` message handling was rebuilt again for fairness and reliability: controllers sharing a bus now get fair queue turns instead of one controller starving another, responses route to the exact command that sent them (not just the next one in line), each device tracks its own offline state independently, and the common command path no longer allocates on the heap.

Server mode (`modbus_server`) grew real capability: coil and discrete-input registers, function code 0x17 (read/write multiple registers in one transaction), spec-compliant broadcast writes, and byte-swapped word types.

Two more client-side options are now deprecated no-ops: `command_throttle` and `allow_duplicate_commands` on `modbus_controller`. Use `turnaround_time` on the `modbus:` hub instead (raised to 600ms as its default back in 2026.7.0). A side effect of the fairness work: shared-range polling now widens to the widest sensor sharing a range, which can trigger read exceptions on strict Modbus devices that reject over-wide reads, worth checking if you see new exceptions after upgrading.

### New: ad-hoc `modbus_client` component

For automations that need a one-off Modbus transaction instead of a polled sensor, the new `modbus_client` component exposes typed read/write actions plus a plain device handle for lambdas, and can read or write multiple registers in a single transaction.

```yaml
modbus:
  id: modbus_hub
  uart_id: uart_bus

modbus_client:
  id: meter_client
  modbus_id: modbus_hub
  address: 0x01

button:
  - platform: template
    name: "Reset Meter Totalizer"
    on_press:
      - modbus_client.write:
          modbus_client_id: meter_client
          register_type: holding
          address: 0x0010
          value: 0
```

> Confirm the exact action names and value types against the `modbus_client` component docs before shipping; this is a new component and its YAML surface may still be settling.

---

## New Hardware

- **`ld6002b`** (sensor): Hi-Link HLK-LD6002B 60 GHz 3D presence radar. Per-target position tracking, configurable detection/interference zones, sensitivity and power management.
- **`hoermann_hcp`** (cover): controls Hörmann garage door motors over the HCP bus, with cover control, garage light, and a connectivity sensor.
- **`ds248x`** (one_wire platform): DS2482-100/-101/-800 and DS2484 I2C-to-1-Wire bridges, letting Dallas temperature sensors hang off up to 8 bridged channels from one I2C device.
- **`zephyr_pwm`** (output): PWM outputs for nRF52 boards.
- **CH390 SPI Ethernet**: WCH CH390 single-chip 10/100 MAC+PHY, verified at 100 Mbps full duplex.
- **Displays**: JC8012P4A1-V2 panel revision (`mipi_dsi`); Waveshare ESP32-S3-Touch-LCD-3.5B and an ST77916-based ESP-VoCat round display (both `mipi_spi`); Guition JC8012P4A1 touchscreen (`gsl3670`); 7-color Soldered Inkplate 6COLOR e-paper.
- **OpenThread diagnostics**: 13 new numeric sensors for MAC/MLE counters plus parent link quality and RSSI.
- **Haier short IR messages** for `remote_transmitter`/`remote_receiver`.
- **Configurable I2S PDM microphone downsampling.**

```yaml
# Hörmann garage door over HCP bus
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 19200

hoermann_hcp:
  id: garage_bus

cover:
  - platform: hoermann_hcp
    hoermann_hcp_id: garage_bus
    name: "Garage Door"

light:
  - platform: hoermann_hcp
    hoermann_hcp_id: garage_bus
    name: "Garage Light"
```

> Verify pin assignments and the exact bus wiring against the `hoermann_hcp` component docs; the HCP bus timing is device-specific.

---

## Tooling and Performance

- **`ccache` reaches more platforms**: ESP8266, LibreTiny, RP2040, and host builds now share the cache ESP-IDF already had. Opt out with `ESPHOME_CCACHE_ENABLE=0`.
- **Smaller ESP-IDF installs**: a fresh install now only pulls toolchains for the variants you actually build (roughly halves a clean install), skips unused gdb/ULP toolchains, and prunes download caches afterward.
- **Leaner CLI**: the validated-config cache is now stored as JSON, cutting cache-hit parsing from 1-2ms to about 0.05ms; upload subprocesses use less RAM; `esphome logs` can tail a device over the `web_server` event stream, useful for `web_server:`-only devices that skip `api:` entirely.
- **Better ESP32 crash reports**: the crash handler now captures the faulting memory address and raw exception cause, and stamps crash records with the build that produced them so they are not decoded against the wrong firmware ELF.
- **Multi-key OTA signature verification**: an update is accepted if any of up to 3 signature blocks matches a trusted compiled-in key, enabling signing-key rotation and independent backup keys. Bootloader updates are now signature-checked too.
- **Runtime wake word management**: `micro_wake_word` can add or remove wake word models at runtime, loading them into PSRAM with validation. Groundwork for Home Assistant-driven model downloads.
- **ESP8266 stability**: encrypted API handshake time dropped from multi-second stalls to sub-second via rate-limited yields in the TCP and crypto paths, and three crash classes were fixed (a WiFi-disconnect crash, watchdog resets from serial RX interrupts, and a captive-portal teardown reboot affecting ESPAsyncWebServer platforms across ESP8266, RP2040, LibreTiny, and LN882x).
- **Idle-loop savings**: `espnow` no longer polls the WiFi driver every loop, and queued-mode `script` stops polling an empty queue.

---

## Notable Bug Fixes

- ESP32-P4 with no explicit `board:` was building the pre-v3 bootloader layout since 2026.7.0, causing bootloops on production silicon. The production layout is now the default.
- `image:` platform entries (`file`/`animation`/`online_image`) had lost support for sharing `defaults:`/`files:` options across images since the 2026.7.0 platform migration. Restored.
- `ld2420` radar boot-loop from an out-of-range message table index, plus a UART setup-priority race that could leave the bus dead on ESP-IDF.
- Modbus custom-command responses with function codes outside user-defined ranges (for example Sofar inverters' `0x49`) had been silently dropped since 2026.7.0. Fixed via universal CRC-scan frame-end detection.
- The sensor `delta` filter had been swallowing NaN since 2026.2.0, so a `timeout:` plus `delta:` combo held the last reading forever instead of marking the sensor unavailable. Fixed.
- A beta API entity-key hashing bug that caused Home Assistant to recreate every entity on first connect was reverted to the sanitized object-ID hash.
- `rotary_encoder` reset pin now respects `min_value` instead of always resetting to `0`.

---

## Patch Release 2026.8.1 (August 24, 2026)

- Fixed a loop stall in the `api` component that could trigger the task watchdog when sending large entity lists.
- Fixed `espnow` `dump_config` crash when `enable_on_boot` is false.
- Fixed `emontx` sensor `state_class` defaults not applying correctly.
- Fixed ESP8266 reporting stale crash state after hardware watchdog resets.
- `esp32_ble_tracker` reverted to scanning at the default window while a GATT connection is active (a follow-up refinement to the BLE/WiFi coexistence fix below).
- Fixed a Windows path corruption bug for templated `!include` filenames.
- BK7238 BLE builds are blocked pending a LibreTiny bonding-partition fix. This is a safety gate, not a feature removal.

---

## Not Flagged as Breaking, Worth a Troubleshooting Mention

- `cv.parse_esphome_version` was removed and then restored as a deprecated helper after external components calling it broke. It now warns and points to `cv.require_esphome_version`; removal is planned for 2027.2.0.
- ESP32 BLE scan window: with WiFi coexistence on ESP-IDF 5.5.5+, the `esp32_ble_tracker` `window` now defaults to match `interval` (Espressif's recommendation). This fixes a regression where BLE trackers and proxies were missing most advertisements alongside active WiFi since 2026.7.1. If a device on 2026.7.x was seeing flaky BLE presence detection with WiFi also active, this release should resolve it without any config change.

---

## Breaking Changes Reference (compact)

| Area | Change | Migration |
|------|--------|-----------|
| BLE hub key | `esp32_ble_id` renamed | Rename to `ble_hub_id` (old key works until 2027.2.0) |
| iBeacon parsing | 23-byte Apple payloads need the 0x02/0x15 sub-type prefix | No config change; tightens false-positive matching |
| Gas index sensors | SGP4x/SEN5x/SEN6x `voc`/`nox` renamed | Rename to `voc_index`/`nox_index` (auto-migrates with a warning until 2027.2.0) |
| AQI sensor | Over-range values now interpolate instead of pinning flat | No config change; behavior differs above 301 US AQI / 101 CAQI |
| LVGL | `ease_in`/`ease_out` weights above 1.0 now rejected | Keep animation weights at or below 1.0 |
| RC522 I2C | Default address changed `0x2C` -> `0x28` | Add `address: 0x2C` if your hardware needs the old default |
| LED strips | `rgb_order`/`is_rgbw`/`is_wrgb` deprecated | Use `channel_colors:` (old keys work until 2027.3.0) |
| GPIO expanders | `interrupt_pin` `inverted:`/`allow_other_uses:` now validation errors | Remove those keys on pcf8574/pca9554/tca9555/pca6416a/pi4ioe5v6408/mcp23016 |
| Modbus | `command_throttle`/`allow_duplicate_commands` are no-ops; `custom_command: [0x17,...]` offsets shift by 1; `modbus_server` can't use `address: 0` | Use `turnaround_time`; adjust offsets; avoid address 0 on servers |
| Web server JSON | `id` field fully migrated to `{domain}/{device?}/{name}`; alarm domain uses underscores | Only affects custom frontends reading the raw API |

---

## Developer-Facing Changes (external components, lambdas)

If you only write YAML, skip this section.

- Modbus hub: `send_pdu()` renamed to `queue_pdu()` (old name kept as a deprecated alias); new `succeeded()` helper.
- Modbus server: read lambdas can now decline a read by returning an empty optional (previously silently returned `0`).
- VEML3235: `gain: AUTO` removed from schema (it never worked); non-functional power-on/shutdown code removed.
- Zigbee: `is_connected` renamed to `is_joined()`; `joined`/`started`/`factory_new` members are now protected.
- Web server base: credential setters now take `const char *` instead of `std::string`.

---

## What Did NOT Change (reassurance)

- **Modbus YAML surface is unchanged.** `modbus:`, `modbus_controller:`, and `modbus_server:` keep their existing keys; the fairness and offline-tracking work is internal. Only `command_throttle` and `allow_duplicate_commands` became no-ops.
- **Existing BLE sensor configs keep working.** The `ble_hub_id` rename has a deprecation window through 2027.2.0; nothing breaks on upgrade.
- **`image:` / `animation:` / `online_image:` legacy keys still work** through 2027.1.0, per the 2026.7.0 migration window; this release only fixed a regression in their `defaults:`/`files:` sharing.
- **Non-SGP4x/SEN5x/SEN6x VOC sensors are unaffected.** SGP30's `tvoc`/`eco2` keys are a different driver and unchanged.
- **A single BLE tracker still needs no `ble_hub_id`.** The key only matters when more than one BLE hub is configured.

---

## Recipes (complete worked examples)

### Recipe 1: Multi-chip BLE presence, mixing an ESP32 tracker and a Pico W tracker

**Goal:** two BLE hubs on the same Home Assistant instance (an ESP32 tracker in one room, a Pico W tracker in another), each reporting presence for the same tag, disambiguated with `ble_hub_id`.

```yaml
esphome:
  name: ble-presence-hallway
  friendly_name: BLE Presence Hallway

esp32:
  board: esp32dev
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

esp32_ble_tracker:
  id: hallway_tracker

sensor:
  - platform: ble_rssi
    mac_address: AA:BB:CC:DD:EE:FF
    name: "Phone RSSI (Hallway)"
    ble_hub_id: hallway_tracker   # renamed from esp32_ble_id
```

### Recipe 2: SGP41 VOC/NOx index sensor with humidity/temperature compensation

**Goal:** an SGP41 gas sensor publishing the renamed `voc_index`/`nox_index` keys, compensated against a companion SHT4x reading.

```yaml
esphome:
  name: air-quality-node
  friendly_name: Air Quality Node

esp32:
  board: esp32-c3-devkitm-1
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

i2c:
  sda: GPIO4
  scl: GPIO5

sensor:
  - platform: sht4x
    id: sht4x_sensor
    temperature:
      name: "Temperature"
      id: temp_sensor
    humidity:
      name: "Humidity"
      id: humidity_sensor
    update_interval: 30s

  - platform: sgp4x
    voc_index:            # was voc
      name: "VOC Index"
    nox_index:              # was nox
      name: "NOx Index"
    compensation:
      humidity_source: humidity_sensor
      temperature_source: temp_sensor
    store_baseline: true
```

### Recipe 3: RGBW LED strip on the new `channel_colors` key

**Goal:** a plain WS2812 strip and an SK6812 RGBW strip on the same ESP32, both configured with `channel_colors` instead of the deprecated `rgb_order`/`is_rgbw` pair.

```yaml
esphome:
  name: led-node
  friendly_name: LED Node

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    rmt_channel: 0
    chipset: WS2812
    channel_colors: GRB
    name: "Hallway Strip"

  - platform: esp32_rmt_led_strip
    pin: GPIO26
    num_leds: 30
    rmt_channel: 1
    chipset: SK6812
    channel_colors: GRBW
    name: "Under Cabinet RGBW Strip"
```

### Recipe 4: Dual Ethernet/WiFi with automatic failover

**Goal:** an Ethernet-wired hub device that falls back to WiFi if the cable is unplugged, and back to Ethernet once it is restored, without a reboot.

```yaml
esphome:
  name: hub-node
  friendly_name: Hub Node

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

ethernet:
  type: LAN8720
  mdc_pin: GPIO23
  mdio_pin: GPIO18

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

network:
  priority:
    - ethernet
    - wifi

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:
```

### Recipe 5: DS2482 I2C-to-1-Wire bridge with two Dallas sensors

**Goal:** read two DS18B20 temperature sensors through a DS2482-100 bridge instead of dedicating a native 1-Wire GPIO pin.

```yaml
esphome:
  name: ds248x-node
  friendly_name: DS248x Node

esp32:
  board: esp32dev
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

i2c:
  sda: GPIO21
  scl: GPIO22

one_wire:
  - platform: ds248x
    id: bridge

sensor:
  - platform: dallas_temp
    one_wire_id: bridge
    address: 0x1c0000031ecf2810
    name: "Sensor A"
  - platform: dallas_temp
    one_wire_id: bridge
    address: 0x3c0000031f5c2810
    name: "Sensor B"
```

> Confirm channel-selection options against the `ds248x` component docs if wiring more than one bridge or using the DS2482-800's 8 channels.

### Recipe 6: RC522 I2C tag reader with an explicit legacy address

**Goal:** an RC522 wired for I2C on hardware that expects the pre-2026.8.0 default address, kept working with an explicit `address:`.

```yaml
esphome:
  name: rc522-node
  friendly_name: RC522 Node

esp32:
  board: esp32dev
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

i2c:
  sda: GPIO21
  scl: GPIO22

rc522_i2c:
  address: 0x2C   # explicit: the 2026.8.0 default changed to 0x28
  update_interval: 1s

binary_sensor:
  - platform: rc522
    uid: AA-BB-CC-DD
    name: "NFC Tag 1"
```

> Verify `rc522_i2c` config keys against the component docs; this repository's other RC522 examples use the SPI variant (`rc522_spi`), which is unaffected by this address change.

---

## Links

- Full changelog: https://esphome.io/changelog/2026.8.0/
- Blog overview: https://esphome.io/blog/2026/08/19/esphome-2026-8/
- BLE device base: https://esphome.io/components/ble_device_base/
- Modbus: https://esphome.io/components/modbus/
- Modbus client: https://esphome.io/components/modbus_client/
- LED strip (ESP32 RMT): https://esphome.io/components/light/esp32_rmt_led_strip/
- SGP4x: https://esphome.io/components/sensor/sgp4x/
- RC522: https://esphome.io/components/binary_sensor/rc522/
- Networking priority: https://esphome.io/components/network/
