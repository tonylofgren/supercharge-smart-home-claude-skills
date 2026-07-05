# Current Platform Versions

## Home Assistant 2026.7 (released 2026-07-01, current patch 2026.7.1 from 2026-07-03)

- **Purpose-specific triggers and conditions become the default** (graduated from Labs): automations describe intent instead of raw entity/state plumbing; integrations can register their own trigger/condition types. Classic YAML triggers, conditions, and templates keep working; no migration needed. Route to **Sage**.
- **Activity timeline**: logbook rebuilt as a day-grouped timeline. No YAML impact.
- **Update all**: Updates page grouped into per-source cards with one-tap bulk update (ESPHome devices and HACS bundled; core/OS stay manual). Route to **Forge**.
- **Dedicated Infrared and Radio Frequency settings panels** when such devices exist. Route to **Volt** (firmware) plus **Sage**.
- **ZHA Zigbee device management overhaul**. Route to **Nano**.
- **Breaking**: Z-Wave JS requires zwave-js-server 3.9.0+; position-aware device trackers now report the smallest enclosing zone (zone-based automations can shift). Route breakage reports to **Glitch**.
- **10 new integrations** (Dropbox, MELCloud Home, KlikAanKlikUit, and more). Route to **Ada**.

## Home Assistant 2026.6 (released 2026-06-03)

- **Legacy `platform: template` entities REMOVED** (deprecated since 2025.12): old-style template entities under individual platform keys no longer load. Migration to the `template:` integration is mandatory. Route migrations to **Sage**, post-upgrade breakage to **Glitch**.
- **IR receiver event entities**: the Infrared platform now receives; ESPHome is the first transmitter integration, and received IR commands trigger automations as events. Route to **Volt** plus **Sage**.
- **Zone-based triggers/conditions in the automation editor (Labs)** with `for:` duration. Route to **Sage**.
- **Card picker by entity with live previews**; tile card weather forecast features and media remote controls. Route to **Iris**.
- **Z-Wave lock credential management in the UI**. Route to **Sage** or **Nano**.
- **Removed**: Konnected integration (migrate hardware to ESPHome, route to **Volt**), `velux.reboot_gateway` action.
- **16 new integrations**. Route to **Ada**.

## Home Assistant 2026.5 (released 2026-05-06)

- **Radio Frequency (RF) integration**: sub-GHz RC device control. Backends: Broadlink RM4 Pro, or ESPHome with a CC1101 transceiver (around 10 USD). Exposes covers, switches, buttons, binary sensors for 315/433/868/915 MHz devices (blinds, garage doors, RF outlets, doorbells, Honeywell String Lights, Novy cooker hoods). Route to **Volt** (firmware side) plus **Sage** or **Iris** (HA side).
- **Serial Port Proxy integration**: auto-discovers ESPHome devices running `serial_proxy` (stable since ESPHome 2026.3) and exposes the UART as if locally attached. Pairs with Modbus, DLMS, and the new Denon RS232 integration. Route to **Volt** plus **Ada** or **Sage**.
- **Battery Maintenance Dashboard**: central low-battery view at Settings > System > Battery Maintenance. Entities need both `device_class: battery` and `unit_of_measurement: "%"`. Route to **Sage** or **Iris**.
- **Media Player Tile features**: transport, volume, source selectors live in the tile card. Route to **Iris**.
- **Vacuum and Lawn Mower more-info redesign**: map view, zone selection, direct command buttons. Automatic for compatible integrations.
- **Dashboard background colors and card favorites** (per-view): route to **Iris**.
- **Code editor autocomplete** in Developer Tools and Automations editor.
- **12 new integrations**: EARN-E P1 Meter, OMIE energy prices, Denon RS232, Duco, Eurotronic, Fumis, Honeywell String Lights, Kiosker, Victron GX, OpenDisplay (ePaper), Novy Cooker Hood, Radio Frequency. Route most to **Ada**, energy-related to **Watt**.

## Home Assistant 2026.4
- **IR Proxy** — Native infrared entity platform. ESPHome devices with IR transmitter expose `InfraredEntity`. HA sends commands through them. First integration: LG Infrared (LG TVs). → Route to **Volt** + **Sage**
- **Cross-domain automation triggers** — More intuitive triggers aligned to how users think (in Labs). → Route to **Sage**
- **Matter lock PIN management** — Full PIN code control for Matter locks. → Route to **Sage** or **Nano**
- **Dashboard: section background colors** — Sections can now have background colors. → Route to **Iris**
- **Dashboard: card favorites** — Pin favorite entities to cards. → Route to **Iris**
- **AI Assist transparency** — Visual indicator of what Assist is processing. → Route to **Mira**
- **Voice: vacuum area cleaning** — Ask Assist to clean a specific area. → Route to **Echo**
- **New integrations** — UniFi Access, WiiM, Solarman, TRMNL (e-paper display). → Route to **Grid** (UniFi), **Ada** (others)
- **Backup upload progress** — Per-location upload percentage visible. → Route to **Forge**

## ESPHome 2026.6 (released June 2026)

Full reference: `esphome/references/release-2026-6.md`.

- **Device Builder replaces the legacy dashboard**. Route to **Volt** plus **Forge**.
- **ESP8266 WiFi security raised to WPA2** (breaking for WEP/open networks). Route to **Volt**.
- **`enable_on_boot: false` frees RAM** for wifi/ethernet disabled at boot. Route to **Volt** plus **Watt**.
- **New `motion` IMU framework** (BMI270, LSM6DS drivers) with heading calibration actions. Route to **Volt**.
- **Audio stack modernization**: PCM5122 DAC, router speaker. Route to **Echo**.
- **New hardware**: XDB401 pressure sensor, USB-serial drivers, RP2040/RP2350 variant selection, ESP32 flash mode/frequency options. Route to **Volt**.

## ESPHome 2026.5 (released May 2026)

Full reference: `esphome/references/release-2026-5.md`.

- **Sendspin multi-room audio** (hub, group, and per-speaker devices), SPDIF speaker output, `audio_http` media source. Route to **Echo**.
- **Native ESP-IDF toolchain** plus main-loop and watchdog overhaul (`esp32: watchdog_timeout`). Route to **Volt**.
- **BLE coex fix for `status=133`** and `esp32_ble: use_psram`. Route to **Volt** or **Nano**.
- **Zigbee on ESP32-H2 and C6** (esp-idf framework only). Route to **Nano**.
- **LVGL improvements**; lock entities gain OPENING and OPEN states. Route to **Volt**.

## ESPHome 2026.4 (released 2026-04-15) + 2026.4.5 patch (2026-05-06)

- **ESP32 max CPU frequency as default**: 33% faster API operations. No config changes needed. Timing-sensitive code (IR, bitbanging) may need review. Route to **Volt**.
- **40KB extra IRAM unlocked** for ESP32.
- **Signed OTA verification** (`ota: verify_signature: true`). Route to **Volt** plus **Vera**.
- **Custom partition tables** in `esp32:` block for configs that overflow default flash layout.
- **GPIO Expander interrupt_pin**: MCP23017, PCF8574, and others can now interrupt instead of polling. Route to **Volt**.
- **SPI Ethernet expansion**: W5500, W5100/W5100S, W6100/W6300, ENC28J60 (Microchip 10BASE-T). Wired networking for ESP32 and RP2040 devices without WiFi. Route to **Volt** plus **Grid**.
- **Client-side state logging**: up to 46x faster sensor publishing, auto-enabled.
- **ESP8266 crash handler** now matches ESP32/RP2040 quality.
- **Substitution system redesign**: up to 18x faster config loading. Dynamic `!include` paths.
- **2026.4.5 patch (bugfix only, no new components)**: ha-addon Device Builder toggle, secrets bundle fix when `!secret` quoted, substitutions sibling refs, WiFi safe mode, Nextion text sensor.

## ESPHome 2026.3
- **IR/RF Proxy** (`ir_rf_proxy`) — Runtime IR/RF signal transmission without reflashing. Learns and replays commands. Works with `remote_transmitter` / `remote_receiver`. → Route to **Volt**
- **RP2040 / RP2350 first-class support** — pico-sdk 2.0, 143+ board definitions, BLE foundations, crash diagnostics. → Route to **Volt**
- **Media player redesign** — Pluggable sources, playlists, Ogg Opus support. → Route to **Echo**
- **Performance** — Main loop up to 99x faster, API protobuf 6–12x faster, 11–20KB flash savings. No config changes needed — just reflash.
- **ESP8266 heap crash fix** — Long-standing LWIP use-after-free bug resolved.
