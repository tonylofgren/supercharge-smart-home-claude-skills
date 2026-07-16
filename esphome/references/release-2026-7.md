# ESPHome 2026.7.0 - Complete Release Reference (July 2026)

**Release date:** July 2026 (2026.7.0; no patch release at the time of writing, latest is 2026.7.0)
**Source:** https://esphome.io/changelog/2026.7.0/

When the user is on this version, upgrading TO it, or asking "what's new", read this file BEFORE generating YAML. The default build toolchain flips to native ESP-IDF, a Modbus rewrite lands, a new security stack (NVS encryption, OTA downgrade protection, provisioning) arrives, `image:` becomes a platform, and several keys are renamed or removed. Older patterns can be invalid.

---

## What landed in 2026.7.0 at a glance

Ten themes worth knowing before you upgrade:

1. **Native toolchains are the default now.** On `esp32` the build backend switches from PlatformIO to native ESP-IDF, and on `nrf52` it switches to the native nRF Connect SDK. Configs with no explicit `toolchain:` compile the new way. `toolchain: platformio` is the opt-out on both.
2. **A coordinated security stack for EN18031.** Three opt-in pieces: NVS encryption on ESP32 (HMAC-derived key in an eFuse slot), OTA downgrade protection for signed images, and a transport-agnostic `provisioning` component that closes a setup window on a timeout.
3. **Modbus was rewritten.** A buffer-based, frame-length-aware parser replaces the old byte-by-byte one, the client and server internals split into separate hubs, single-register frames now avoid heap churn, and the client timing defaults were raised.
4. **LVGL grew a lot.** Full animation support, templated runtime rotation with `on_landscape` / `on_portrait` triggers, a `paused` option that suppresses drawing until you resume, and continued input/timer processing while an e-paper refresh is in flight (with a now-configurable refresh interval).
5. **Eleven new hardware components.** Touch controllers (cst328, st7123, gsl3670, cst9220/cst9217), e-paper panels plus the IT8951 controller, a QMI8658 IMU on the `motion` platform, the Divoom Pixoo 64 matrix, a UFM-01 ultrasonic flow meter, and the Waveshare CH32V003 I/O expander.
6. **`image:` became a platform component.** Images, animations, and online images move under `platform: file` / `platform: animation` / `platform: online_image`. The old top-level keys keep working through 2027.1.0 with a migration hint.
7. **Networking additions.** Gigabit Ethernet for the new ESP32-S31 (RGMII PHYs, needs ESP-IDF 6.1), ESP-NOW v2 payloads up to 1470 bytes, MQTT on LN882H boards, and FSK data whitening for SX126x.
8. **RTC-backed preferences on ESP32.** `safe_mode`, `wifi: fast_connect:`, and preferences can persist their small state in RTC memory instead of flash, avoiding flash wear.
9. **Zigbee moved to SDK 2.0.2 with endpoint merging.** Better ESP-IDF compatibility, new ESP32 variants, and single-endpoint multi-sensor devices. Existing Zigbee devices must be re-joined and reconfigured.
10. **Tooling, performance, and drops.** A single-precision float sweep across roughly 50 components, ccache on by default and machine-global toolchain caches, YAML merge-drop warnings, a component-rename alias mechanism (first used to rename `rp2040` to `rp2`), web server HTTP digest auth. The legacy Tornado dashboard and Python 3.11 support are gone.

---

## Upgrade Checklist (run through this BEFORE flashing 2026.7.0)

- [ ] ESP32 config with no explicit `toolchain:`? -> it now builds with native ESP-IDF. Add `toolchain: platformio` under `esp32:` to keep the old backend.
- [ ] nRF52 config with no explicit `toolchain:`? -> it now builds with the native nRF Connect SDK. Add `toolchain: platformio` under `nrf52:` to keep the old backend.
- [ ] Installing ESPHome with `pip` on Python 3.11? -> upgrade to Python 3.12 or newer (add-on and Docker are already there).
- [ ] Using `esphome dashboard` from a `pip` install? -> install and run `esphome-device-builder` instead. The legacy dashboard is removed.
- [ ] ESP32 Zigbee devices? -> re-join, re-interview, and reconfigure each device after upgrading (storage layout changed).
- [ ] Set `enabled` or `coordinator` under Zigbee `reporting:`? -> remove those keys.
- [ ] Using `web_server: version: 1`? -> plan a move to v2 (default) or v3 before 2027.1.0; a warning is printed now.
- [ ] Address `web_server` entities by object ID in URLs? -> switch to the entity name; object-ID matching is removed.
- [ ] A browser page on another origin calls your `web_server`? -> add its origin to `web_server: allowed_origins:`.
- [ ] Relied on `web_server` Private Network Access being on by default? -> it is off now. Set `enable_private_network_access: true` and list the calling origins in `allowed_origins:`.
- [ ] Use `packages: !include mypackage.yaml`? -> wrap it in a list: `packages: [!include mypackage.yaml]`.
- [ ] Use `FOUR_SCAN_16PX_HIGH` / `FOUR_SCAN_32PX_HIGH` / `FOUR_SCAN_64PX_HIGH` for hub75 `scan_wiring`? -> rename to `SCAN_1_4_16PX_HIGH` / `SCAN_1_8_32PX_HIGH` / `SCAN_1_8_64PX_HIGH`.
- [ ] Set `disable_crc` under `modbus:`? -> remove it.
- [ ] Set `send_wait_time` or `turnaround_time` on a `modbus:` server? -> remove those keys (server mode no longer takes them).
- [ ] Rely on modbus client timing? -> defaults changed to `send_wait_time: 2000ms` and `turnaround_time: 600ms`. Review any overrides you added for the old parser.
- [ ] Use the `generic-ln882hki` board? -> switch to `generic-ln882h` or `generic-ln882h-tuya` depending on factory firmware.
- [ ] Use the LN882H `wb02a` board with `D1`, `D7`, `D8`, `D9`, or default I2C pin aliases? -> update pin numbers to the new mapping.
- [ ] Have lambdas or automations that set light brightness to `0`? -> the value is preserved now instead of being clamped to `1.0`.
- [ ] Two Home Assistant instances share one `bluetooth_proxy`? -> the newest subscriber now wins instead of the oldest.
- [ ] Build for nRF52 boards without a DCDC regulator? -> DCDC settings are no longer forced; generated code changes slightly.
- [ ] Lambdas call `value_accuracy_to_string()` or `MideaData::to_string()`? -> move to the buffer variants `value_accuracy_to_buf()` and `to_str(buffer)`.

---

## Native Toolchains Are the Default (ESP32 and nRF52)

The `toolchain:` option selects the build backend, not the framework. Both Arduino and ESP-IDF frameworks build under either backend; the native backend pulls Arduino in as an ESP-IDF component. What changed in 2026.7.0 is only the default backend.

On `esp32`, a config with no explicit `toolchain:` now compiles with native ESP-IDF (PR #16910). On `nrf52`, it now builds with the native nRF Connect SDK 2.9.2 (PRs #16898, #17319). Setting `toolchain: platformio` keeps the previous behavior on both platforms. The framework-migration notice shown since 2026.1.0 was removed now that the default landed (PR #17023).

```yaml
# Native ESP-IDF is now the default backend, no toolchain: line needed.
esp32:
  board: esp32dev
  framework:
    type: esp-idf        # the framework, independent of the toolchain

# To pin the old PlatformIO backend instead:
# esp32:
#   board: esp32dev
#   toolchain: platformio
```

Important: this default flip is a build-backend change, and is transparent for most configs. It is **not** the same as ESP-IDF 6.1 becoming the default framework version. The framework `version:` still defaults to `recommended` (a 5.x line). Features that require ESP-IDF 6.1 (gigabit Ethernet on the ESP32-S31, PSRAM on S31/H4) still need an explicit development framework version and are not routine flashable configs yet. See the gated note below.

---

## Security and Provisioning Stack (EN18031 groundwork)

Three opt-in pieces land together (PRs #17004, #17315, #17152). All three help meet the secure-communication expectations of standards such as EN18031 for network-connected consumer devices.

### NVS encryption on ESP32

`esp32: nvs_encryption:` encrypts non-volatile storage (where ESPHome keeps things like WiFi credentials and the API key) using the chip's HMAC peripheral. The key is generated on the device the first time it boots, derived from an HMAC key in an eFuse slot you choose, so flash encryption is not required and no key material lives in your YAML.

```yaml
esp32:
  board: esp32-s3-devkitc-1
  nvs_encryption:
    key_id: 0            # eFuse HMAC key slot 0-5; pick one nothing else uses
```

> WARNING: burning the HMAC key to an eFuse slot is permanent. It happens on the device the first time it boots and cannot be changed or removed afterwards, even by erasing or re-flashing. Pick a `key_id` and keep it. Turning encryption on (or later off) clears previously saved preferences once, because the old data can no longer be read. Read the `esp32` component docs before enabling this.

Supported only on variants with the HMAC peripheral: S2, S3, C3, C5, C6, H2, and P4. The original ESP32 and the ESP32-C2 are not supported.

### OTA downgrade protection

`esp32: enable_ota_downgrade_protection: true` rejects an OTA update whose firmware version is older than the running one. The version comes from `esphome: project: version:`, is embedded in the signed image, and is compared before the boot partition is switched. It covers native, `http_request.ota`, and `web_server` OTA sources.

```yaml
esphome:
  name: hardened-node
  project:
    name: "acme.thermostat"
    version: "1.4.0"       # dotted-numeric; compared one number at a time

esp32:
  board: esp32-s3-devkitc-1
  enable_ota_downgrade_protection: true

ota:
  - platform: esphome
    # Requires a signed image to be effective; the version is read from inside
    # the signed payload. See the ota / signed-verification docs.
```

Requirements: a dotted-numeric `project: version:` and signed OTA verification enabled. Flashing the same version is always allowed.

### Provisioning component

The new `provisioning` component (PR #17152) manages a **provisioning window** for devices that ship without their credentials. The window opens at boot and closes once the device is provisioned (connected to a network and, when the API uses encryption, its key set) or when `timeout` elapses. On timeout, unprovisioned API clients are disconnected with a "provisioning closed" reason and BLE Improv stops accepting WiFi credentials. While unprovisioned, WiFi and API reboot timeouts pause so the device does not reboot while waiting. Power-cycling reopens the window.

```yaml
provisioning:
  timeout: 5min
  on_timeout:
    then:
      - logger.log: "Provisioning window closed; power-cycle to reopen"
```

At least one provisioning-capable source must exist. A configured `wifi:` or `ethernet:`, or an `api:` with `encryption:` and no `key:`, satisfies that.

---

## Modbus Overhaul

A major rework of the `modbus` component landed (PRs #11969, #11987, #17282, #17205, plus API settling in #17378 / #17434).

- **Rewritten parser.** Byte-by-byte parsing is replaced by a buffer-based, frame-length-aware parser that correctly handles peer server responses, unsupported function codes, and custom function codes. Response tracking now matches on address plus function code, which allows multiple devices per address.
- **Client and server split (internals).** The `Modbus` class splits into `ModbusClientHub` and `ModbusServerHub`, retiring the role enum internally. This is a developer-facing API change; the YAML surface (`modbus:` for the client hub, `modbus_server:` for server registers) is unchanged. External components must update against the new API.
- **Heap-free send path.** Common 8-byte frames (reads and single-register writes) now live inline in the queue node with no per-frame heap allocation.
- **Server improvements.** Multi-register values match by full span, overlapping registers are rejected, and a new `allow_partial_read` option is available per register range. The obsolete `RAW` value type is gone from server mode.
- **New callbacks.** The parser adds `on_modbus_no_response` and `on_modbus_not_sent` hooks at the C++/component level for detecting missing or unsent frames.

Timing defaults changed on the client: `send_wait_time` moves from `250ms` to `2000ms`, and `turnaround_time` from `100ms` to `600ms`. If you raised these to work around the old parser, check whether the overrides are still needed.

Removed keys: `disable_crc` (from `modbus:`), and `send_wait_time` / `turnaround_time` from server mode.

---

## LVGL: Animations, Rotation, and Runtime Updates

A substantial expansion of the `lvgl` component (PRs #16796, #16773, #15863, #16973, #17374).

- **Animations** (PR #16796): a top-level `animations:` list with from/to interpolation, timing functions, duration, looping, and `auto_start`, driven at runtime with the `lvgl.animation.start` / `lvgl.animation.stop` actions.
- **Dynamic rotation** (PR #16773): the `lvgl.display.set_rotation` action takes degrees (templatable), with new `on_landscape` and `on_portrait` triggers, and layout options that update in `lvgl.update`.
- **Direct `mapping` syntax** (PR #15863): cleaner LVGL text and image `src` updates using a mapping directly.
- **Boot pausing** (PR #16973): a `paused` option starts LVGL paused so nothing draws until `lvgl.resume`. Useful for e-paper panels that should not render invalid state before the API connects. `resume_on_input` resumes on a touch or button.
- **Activity while the display is busy** (PR #17374): with `update_when_display_idle` (typical for e-paper), LVGL keeps processing input and running timers during a refresh. The refresh interval, previously fixed at 16 ms, is now configurable with `refresh_interval`.

---

## New Hardware

The release adds broad display, touch, and sensor support, largely on M5Stack, Waveshare, and Seeed reTerminal families.

- **Touch controllers:** `cst328` (PR #8011), `st7123` integrated display-touch driver for the M5Stack Tab5 (PR #12075), `gsl3670` for the Seeed reTerminal D1001 (PR #16285), and `cst9220` covering CST9220 and CST9217 (PR #16888).
- **E-paper:** the `epaper_spi` component picks up several panels (Waveshare 7.5" V2 BWR, Seeed reTerminal E1004 13.3" 6-color, Waveshare 2.13" V4 BWR, Soldered Inkplate 2, Seeed reTerminal-sticky), and the new `it8951` controller drives M5Paper and Seeed reTerminal E1003/EE03 panels up to 1872x1404 at 16-level grayscale (PR #15346).
- **MIPI-SPI displays:** M5STACK ATOM3SR (PR #17344) and the Waveshare ESP32-S3-Touch-AMOLED-1.64 with SH8601 (PR #17386). A new `mipi_dsi` model covers the M5Stack Tab5 (PR #17500).
- **Divoom Pixoo 64:** the `pixoo` display component (PR #16974) drives the 64x64 RGB LED matrix over SPI and exposes a `pixoo` light platform for panel brightness.
- **Sensors and peripherals:** a `ufm01` ScioSense ultrasonic flow meter over UART (PR #16582), a `qmi8658` 6-axis IMU on the `motion` platform (PR #16889), and the `waveshare_io_ch32v003` I/O expander (PR #10071) with EXIO GPIO, PWM backlight, an ADC battery-voltage sensor, and RTC interrupt status.
- **Audio:** `pcm5122` gains analog gain, channel mixing, a configurable volume range, a standby/powerdown switch, and an XSMT enable pin, plus a clock-register page-bug fix (PR #17313). The `i2s_audio` speaker now accepts wider streams (for example 24-bit into a 16-bit device) and narrows them in place (PR #16821).

> Note: the MIPI display drivers (`mipi_spi`, `mipi_dsi`, `mipi_rgb`) now enforce mandatory companion components such as PSRAM and I/O expanders for the integrated boards whose hardware assignments they know (PR #17405).

---

## `image:` Becomes a Platform

`image:` was restructured into a platform component (PR #17416). The new form uses `platform: file`, `platform: animation`, and `platform: online_image`, with `animation` a sub-component of the file platform. The legacy top-level `image:`, `animation:`, and `online_image:` keys keep working through 2027.1.0 with copy-paste migration warnings at validation time.

```yaml
# New platform form
image:
  - platform: file
    id: logo
    file: "logo.png"
    type: RGB565

online_image:
  - platform: online_image
    id: weather_icon
    url: "https://example.com/icon.png"
    format: PNG
```

---

## RTC-Backed Preferences on ESP32

The ESP32 preferences backend can now persist small state in RTC memory instead of flash (PR #17073), the way ESP8266 already could. This avoids flash wear and survives software reboots, OTA, crashes, and deep sleep, but not a full power loss. The ESP32-C2 and ESP32-C61 have no RTC RAM and fall back to flash. Two verified surfaces:

```yaml
# safe_mode boot counter in RTC instead of flash
safe_mode:
  storage: rtc          # rtc | flash (default flash on ESP32)

# WiFi fast-connect details (BSSID + channel) in RTC
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect:
    enabled: true
    storage: rtc
```

The changelog also documents a `preferences: rtc_storage: true` surface for the preferences component itself; check the component docs for the exact key before relying on it. This is groundwork for a planned DHCP-lease cache.

---

## Zigbee: SDK 2.0.2 and Endpoint Merging

The `zigbee` component on ESP32 moves to esp-zigbee-sdk 2.0.2 for better ESP-IDF compatibility and picks up ESP32-H4, H21, and S31 variants (PR #16869). The dedicated Zigbee storage partition is retired in favor of the default NVS, and reporting config is simplified: the `enabled` / `coordinator` distinction under `reporting:` is gone. A follow-up (PR #17402) merges component endpoints by default and lets you combine them manually, enabling single-endpoint devices with multiple sensors. Both changes require existing Zigbee devices to be re-joined, re-interviewed, and reconfigured after upgrading.

---

## Tooling, Performance, and Memory

- **YAML merge-drop warnings** (PR #17246): a YAML merge (`<<:`) that silently drops a key now prints the source location, explains the merge, and suggests `packages:` for a deep merge. Toggle with `esphome: merge_warnings: false`.
- **Single-precision float sweep** (PRs #17252 and following): about 50 components had silent double-promotion patterns replaced with single-precision math. `hsv_to_rgb` code size dropped from 108 to 69 bytes on ESP32, and roughly 8 soft-double helper calls per site were removed. No YAML change.
- **ESP8266 DRAM savings** (PRs #17341, #17395, #17127): dropping never-read exception strings, silent lwIP DHCP stubs, and moving the `package_import_url` mDNS string to flash reclaim a useful chunk of DRAM. No behavior change.
- **ccache and shared toolchain caches** (PRs #17163, #17306, #17353): ccache is on by default for ESP-IDF builds when the binary is present (opt out with `IDF_CCACHE_ENABLE=0`), and toolchains install into a machine-global cache (`~/.cache/esphome/idf`, `~/.cache/esphome/sdk-nrf`) shared across projects. Docker and add-on users should pin these to persistent volumes; existing installs re-download once after upgrade.
- **Component alias infrastructure** (PR #16826): components can declare `ALIASES` so a rename does not break existing YAML. Its first user is the `rp2040` to `rp2` rename (PR #17145): the `rp2040:` key and `esphome.components.rp2040` imports keep working as deprecated aliases through 2027.7.0.
- **Web server HTTP digest auth** (PR #17541): `web_server: auth:` gains a `type:` of `basic` or `digest`. Digest keeps the password off the network (hashes only); both look the same in the browser. The default stays `basic` for now and changes to `digest` in 2027.1.0. Digest REST clients must request it (for example `curl --digest`).
- **Config validation is faster** (PRs #17214, #17215): deferring `aioesphomeapi.posix_tz` and `requests` imports cuts `esphome config` wall time notably on a host config.

---

## Dev-Gated: Gigabit Ethernet on ESP32-S31 (requires ESP-IDF 6.1)

The `ethernet` component gains `type: GENERIC` and `type: YT8531` RGMII PHYs for the new RGMII-capable ESP32-S31 (PR #17277), plus new `power_pin` and `phy_registers` options. PSRAM wiring for the S31 and H4 also landed (PR #17192).

These require **ESP-IDF 6.1 or later**, which is NOT the recommended default framework version in 2026.7.0 (the default is a 5.x line). Building for the S31 means pinning a development framework version and running on brand-new hardware. Do not flash this to a normal device. The block below is documentation, not a routine recipe; only emit it for a user who has explicitly opted into a dev build and has ESP32-S31 hardware.

```yaml
# Requires ESP-IDF 6.1 (development framework version, not the stable default)
# and ESP32-S31 hardware. Gated: do not use on a normal build.
esp32:
  board: esp32-s31        # example; use your actual S31 board id
  framework:
    type: esp-idf
    version: "6.1"        # development version; may change or break

ethernet:
  type: YT8531            # Motorcomm YT8531 RGMII PHY on the S31 Functional-Core Board
  mdc_pin: GPIO5
  mdio_pin: GPIO6
  power_pin: GPIO7        # PHY reset pin
```

---

## Breaking Changes Reference (compact)

| Area | Change | Migration |
|------|--------|-----------|
| ESP32 toolchain | Default backend now native ESP-IDF | Add `toolchain: platformio` to keep PlatformIO |
| nRF52 toolchain | Default backend now native nRF Connect SDK | Add `toolchain: platformio` to keep PlatformIO |
| Python | Minimum is now 3.12 | Upgrade `pip` installs from 3.11 (add-on/Docker unaffected) |
| Dashboard | Legacy Tornado dashboard removed | Use `esphome-device-builder` |
| Zigbee | SDK 2.0.2, storage layout changed; `reporting:` `enabled`/`coordinator` invalid | Re-join and reconfigure devices; remove those keys |
| Modbus | `disable_crc` removed; server `send_wait_time`/`turnaround_time` removed; client timing defaults raised | Remove the keys; review timing overrides |
| Packages | Single `!include` form removed | `packages: [!include mypackage.yaml]` |
| Web server | Object-ID URL matching removed; v1 deprecated; cross-origin rejected unless allowed; PNA off by default | Use entity names; move to v2/v3; add `allowed_origins:` |
| Hub75 | `FOUR_SCAN_*` scan_wiring names removed | Use `SCAN_1_4_16PX_HIGH` / `SCAN_1_8_32PX_HIGH` / `SCAN_1_8_64PX_HIGH` |
| Light | Brightness `0` no longer clamps to `1.0` | Restored to `1.0` at next turn-on if still `0` |
| LibreTiny (LN882H) | `generic-ln882hki` removed; `wb02a` pins shifted; default log UART now UART1 | Switch board id; update pin numbers |
| Bluetooth proxy | Newest advertisement subscriber wins | No config change; behavior differs after a HA restart |
| Display (MIPI) | `mipi_*` enforce mandatory PSRAM / I/O-expander companions on known integrated boards | Add the required components |

---

## Developer-Facing Breaking Changes (external components, lambdas)

If you only write YAML, skip this section.

- **Modbus API split.** `Modbus` splits into `ModbusClientHub` and `ModbusServerHub`; `ModbusDevice::set_parent()` takes `ModbusClientHub *`; `Modbus::register_device()` is removed. Ordering operators between `ModbusFunctionCode` and `uint8_t` are gone (cast explicitly or use `helpers::is_function_code_*()`). Further client-mode cleanup is planned for the next release. PRs #11969, #11987, #12376, #17378, #17434.
- **`Select::state` member removed.** Use `current_option()` or `active_index()`. PR #17027.
- **Scheduler `std::string` name overloads removed.** Pass `const char *` names to `set_timeout` and friends. PR #17111.
- **`value_accuracy_to_string()` removed.** Use `value_accuracy_to_buf(buf, value, accuracy)` with a `VALUE_ACCURACY_MAX_LEN` buffer. PR #17116.
- **`MideaData::to_string()` removed.** Use `to_str(buffer)`. PR #17117.
- **`GPIOPin::dump_summary()` returning `std::string` removed.** Override the buffer form. PR #17115.
- **`get_object_id()` and `get_compilation_time()` removed.** PR #17112.
- **UART `load_settings(bool)` is now pure virtual.** Every `UARTComponent` subclass must implement runtime settings updates. PR #16990.
- **`rp2040` renamed to `rp2`.** The `rp2040:` YAML key and `esphome.components.rp2040` imports work as deprecated aliases through 2027.7.0. PRs #17145, #16826.
- **`final` sweep.** Roughly 20 batches add `final` to runtime-instantiated concrete classes for devirtualization. PRs #16952 to #16972, #17129, #17130, #17147.

---

## What Did NOT Change (reassurance)

- **Existing `framework: type: esp-idf` configs stay valid.** The toolchain default flip is a build-backend change and is transparent for most configs. ESP-IDF 6.1 is not the default framework version.
- **All sensor / binary_sensor / switch / light platforms keep their existing YAML.** The big items are additive (new touch, e-paper, IMU, Pixoo, flow-meter platforms) or default flips with a documented escape hatch.
- **Modbus YAML is unchanged.** `modbus:` and `modbus_server:` keep their config surface; the client/server split is a C++ API change. Only `disable_crc` and the server timing keys were removed.
- **`image:` / `animation:` / `online_image:` legacy keys still work** through 2027.1.0.
- **ESP32 configs are unaffected by the Python and dashboard drops.** Those touch the host install, not the firmware.

---

## Recipes (complete worked examples)

### Recipe 1: Native ESP-IDF node (the new default) with a PlatformIO opt-out

**Goal:** a plain ESP32 sensor node that compiles with the native ESP-IDF backend that is now default, showing where the `toolchain: platformio` opt-out goes.

```yaml
esphome:
  name: idf-node
  friendly_name: IDF Node

esp32:
  board: esp32dev
  framework:
    type: esp-idf
  # toolchain: platformio   # uncomment to keep the old PlatformIO backend

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

sensor:
  - platform: uptime
    name: "Uptime"
```

### Recipe 2: EN18031-hardened node (provisioning + NVS encryption + OTA downgrade protection)

**Goal:** a device that ships unprovisioned, encrypts its stored secrets, and refuses to roll back to an older signed firmware.

```yaml
esphome:
  name: hardened-node
  friendly_name: Hardened Node
  project:
    name: "acme.thermostat"
    version: "1.4.0"           # dotted-numeric; used by downgrade protection

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf
  nvs_encryption:
    key_id: 0                  # eFuse HMAC slot 0-5; PERMANENT once burned
  enable_ota_downgrade_protection: true

# The device is "provisioned" once WiFi connects and the API key is set by HA.
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password
    # Signed OTA verification must be enabled for downgrade protection to work;
    # see the ota component docs for signature setup.

provisioning:
  timeout: 5min
  on_timeout:
    then:
      - logger.log: "Provisioning window closed; power-cycle to reopen"

logger:
```

> Reminder: `nvs_encryption` burns an eFuse slot permanently on first boot and cannot be undone. Only enable it on a device you are ready to commit. It works on S2, S3, C3, C5, C6, H2, and P4 only.

### Recipe 3: Modbus client reading a meter, plus a small Modbus server

**Goal:** poll a holding register from an RS485 meter (client), and expose an uptime value as a server register, using the 2026.7.0 timing defaults and the new server `allow_partial_read`.

```yaml
esphome:
  name: modbus-node
  friendly_name: Modbus Node

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

uart:
  - id: uart_bus
    tx_pin: GPIO17
    rx_pin: GPIO16
    baud_rate: 9600

# Client hub (defaults now: send_wait_time 2000ms, turnaround_time 600ms)
modbus:
  id: modbus_client
  uart_id: uart_bus
  flow_control_pin: GPIO4      # RS485 DE/RE if the transceiver needs it

modbus_controller:
  - id: meter
    modbus_id: modbus_client
    address: 0x01
    update_interval: 10s

sensor:
  - platform: modbus_controller
    modbus_controller_id: meter
    name: "Meter Power"
    register_type: holding
    address: 0x0000
    value_type: U_WORD

# Server registers exposed to another Modbus master on the same bus
modbus_server:
  - modbus_id: modbus_client
    address: 0x0A
    server_registers:
      - address: 0x0002
        value_type: U_DWORD_R
        allow_partial_read: true
        read_lambda: |-
          return id(uptime_sensor).state;

sensor:
  - platform: uptime
    id: uptime_sensor
    name: "Uptime"
```

> The rewritten parser also adds `on_modbus_no_response` and `on_modbus_not_sent` callbacks at the component level for detecting missing or unsent frames. Confirm the exact YAML surface in the modbus docs before wiring them into automations.

### Recipe 4: Animated, auto-rotating LVGL UI paused until the API connects

**Goal:** an LVGL screen that starts paused (so nothing invalid draws at boot), rotates its layout when the device is turned, and runs a looping animation once resumed.

```yaml
esphome:
  name: lvgl-ui
  friendly_name: LVGL UI

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

psram:
  mode: octal
  speed: 80MHz

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key
  on_client_connected:
    - lvgl.resume:            # draw only once HA is connected

ota:
  - platform: esphome
    password: !secret ota_password

logger:

# (display: and touchscreen: configured for your panel)

lvgl:
  paused: true               # start paused; resume on API connect above
  resume_on_input: true
  refresh_interval: 30ms     # previously fixed at 16ms
  on_landscape:
    - logger.log: "Now landscape"
  on_portrait:
    - logger.log: "Now portrait"
  animations:
    - id: pulse
      auto_start: true
      # from/to, duration, timing function and looping per the lvgl animation docs
  pages:
    - id: main_page
      widgets:
        - label:
            id: clock_label
            text: "Ready"

# Rotate the display from a template number or an automation
number:
  - platform: template
    name: "Screen Rotation"
    optimistic: true
    min_value: 0
    max_value: 270
    step: 90
    on_value:
      - lvgl.display.set_rotation: !lambda "return (int) x;"
```

### Recipe 5: QMI8658 tilt and orientation sensor (motion platform)

**Goal:** report pitch, roll, live acceleration, and on-chip temperature from a QMI8658 IMU. This extends the `motion` hub introduced in 2026.6.0, so calibration actions from that release apply here too.

```yaml
esphome:
  name: tilt-node
  friendly_name: Tilt Node

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

i2c:
  sda: GPIO8
  scl: GPIO9

motion:
  - platform: qmi8658
    id: imu
    address: 0x6B            # default; 0x6A when SA0 is low
    accelerometer_range: 4G  # 2G / 4G / 8G / 16G
    gyroscope_range: 2048DPS # 16DPS ... 2048DPS

sensor:
  - platform: motion
    type: pitch
    name: "Pitch"
  - platform: motion
    type: roll
    name: "Roll"
  - platform: motion
    type: acceleration_z
    name: "Accel Z"
  - platform: qmi8658
    type: temperature
    name: "IMU Temperature"
```

### Recipe 6: Divoom Pixoo 64 matrix with brightness control

**Goal:** drive the 64x64 Pixoo panel over its internal SPI bus and expose panel brightness to Home Assistant. The Pixoo runs ESPHome on its own on-board ESP32 on fixed internal pins.

```yaml
esphome:
  name: pixoo-panel
  friendly_name: Pixoo Panel

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

# Pixoo 64 fixed internal wiring (write-only, no miso)
spi:
  clk_pin: GPIO25
  mosi_pin: GPIO33

display:
  - platform: pixoo
    id: pixoo_display
    model: 64x64
    cs_pin: GPIO26
    lambda: |-
      it.line(0, 0, it.get_width() - 1, it.get_height() - 1, Color(0, 255, 0));

light:
  - platform: pixoo
    pixoo_id: pixoo_display
    name: "Pixoo Brightness"
```

### Recipe 7: M5Paper e-paper (IT8951) with LVGL idle updates

**Goal:** an M5Paper display driven by the new IT8951 controller, with LVGL configured to keep working while the slow e-paper refresh runs.

```yaml
esphome:
  name: epaper-node
  friendly_name: Epaper Node

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

psram:
  mode: octal
  speed: 80MHz

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

display:
  - platform: it8951
    id: epaper
    model: m5stack-m5paper    # integrated board; pins come from the model
    update_interval: 30s
    rotation: 270

lvgl:
  displays:
    - display_id: epaper
  update_when_display_idle: true   # keep input and timers alive during refresh
  paused: false
  pages:
    - id: info_page
      widgets:
        - label:
            text: "E-paper ready"
```

### Recipe 8: ESP-NOW v2 large-payload link

**Goal:** a low-latency link between two ESP32s using ESP-NOW v2 frames larger than the classic 250-byte cap. Requires ESP-IDF 5.4 or newer (within the recommended default line) or Arduino 3.2 or newer.

```yaml
esphome:
  name: espnow-node
  friendly_name: ESP-NOW Node

esp32:
  board: esp32dev
  framework:
    type: esp-idf

logger:

espnow:
  auto_add_peer: false
  max_payload_size: 1470        # v2 frames; 250 is the default. ~44 KB RAM at 1470 vs ~8 KB at 250
  peers:
    - 11:22:33:44:55:66
  on_receive:
    - logger.log:
        format: "Got %u bytes"
        args: ["size"]

# Send a frame to a peer, for example on a button press
button:
  - platform: template
    name: "Send Ping"
    on_press:
      - espnow.send:
          address: 11:22:33:44:55:66
          data: "ping"
```

### Recipe 9: RTC-backed preferences with digest-auth web server

**Goal:** reduce flash wear by keeping the safe-mode counter and WiFi fast-connect details in RTC memory, and secure the local web server with HTTP digest auth plus a cross-origin allowlist.

```yaml
esphome:
  name: rtc-web-node
  friendly_name: RTC Web Node

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect:
    enabled: true
    storage: rtc              # BSSID + channel in RTC, not flash

safe_mode:
  storage: rtc                # boot counter in RTC, avoids flash wear

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

web_server:
  version: 3
  auth:
    username: !secret web_username
    password: !secret web_password
    type: digest              # keeps the password off the network
  # Only allow this dashboard origin to call the endpoints cross-origin:
  allowed_origins:
    - "https://dashboard.local"
  enable_private_network_access: false
```

### Inline: migrating single-include packages

```yaml
# Before (removed in 2026.7.0):
# packages: !include common.yaml

# After:
packages: [!include common.yaml]
```

---

## Links

- Full changelog: https://esphome.io/changelog/2026.7.0/
- Provisioning: https://esphome.io/components/provisioning/
- ESP32 (NVS encryption, OTA downgrade): https://esphome.io/components/esp32/
- Modbus: https://esphome.io/components/modbus/
- Modbus server: https://esphome.io/components/modbus_server/
- LVGL: https://esphome.io/components/lvgl/
- QMI8658 IMU: https://esphome.io/components/motion/qmi8658/
- Divoom Pixoo: https://esphome.io/components/display/pixoo/
- IT8951 e-paper: https://esphome.io/components/display/it8951/
- Ethernet: https://esphome.io/components/ethernet/
- ESP-NOW: https://esphome.io/components/espnow/
- Web server: https://esphome.io/components/web_server/
