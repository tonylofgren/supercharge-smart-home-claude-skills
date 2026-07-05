# Changelog

All notable changes to Aurora Smart Home skills are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Fixed

- **HA 2026.7 purpose-specific block guidance corrected.** HA 2026.7 made the purpose-specific trigger/condition blocks the default and renamed several Labs-era keys (the old keys no longer work, e.g. `vacuum.docked` is now `vacuum.returned_to_dock` and `timer.time_remaining` is `timer.remaining_time_reached`). The HA skill's 2026.7 notes now document the stable block envelope (`domain.name` plus `target:`/`options:`/`behavior:`/`for:`) and warn about the renames, verified against the official release notes and docs pages.

## [1.16.0] - 2026-07-05

### Added

- **Seeed XIAO board profiles**: `xiao-esp32-c3`, `xiao-esp32-c6`, and `xiao-esp32-s3` join the machine-readable board catalog (recipes, evals, and examples already referenced the family but the pin validator had nothing to check against). Pin maps, strapping pins, the C6 antenna-switch GPIOs (GPIO3/GPIO14), charge currents, and deep-sleep figures verified against the Seeed wiki, arduino-esp32 variant headers, PlatformIO board definitions, and Espressif datasheets. Unverifiable values (charging IC part numbers) stay null instead of guessed. 24 data-integrity tests.
- **PMS5003 and SGP40 component profiles**: the air-quality catalog now covers particulate matter (PM1.0/PM2.5/PM10, UART) and VOC index (I2C 0x59) in addition to CO2, bringing the component catalog to 16 parts. Electrical limits, calibration behavior, and variant confusion risks (PMS5003T/S, SGP41, SGP30) verified against Plantower/Sensirion datasheets and the ESPHome pmsx003/sgp4x docs. LCSC numbers verified live against the JLCPCB parts API (PMS5003 C91431, SGP40-D-R4 C2874215). 13 data-integrity tests.
- **Current platform data**: `aurora/references/platform-versions.md` gains HA 2026.6, HA 2026.7, ESPHome 2026.5, and ESPHome 2026.6 sections with routing hints; it previously called ESPHome 2026.4.5 current while the repo shipped the 2026.6 release reference. A new guard test (`test_platform_versions_guard.py`) fails whenever the doc lags the newest `esphome/references/release-*.md`.
- **HA 2026.6/2026.7 in the HA skill**: what's-new sections added; the legacy `platform: template` warnings now state that the removal shipped in HA 2026.6 (verified against the official release notes) instead of framing it as a future deadline.
- **node-red Delivery Contract**: the skill now carries the same written-to-disk delivery block as the other build skills, pointing at River's Iron Law 3; its checklist is renamed Pre-Completion for consistency.

### Changed

- **Orchestrator routing accuracy**: Volt gains mmWave/radar/LD2410/presence and DLMS/smart-meter trigger keywords; Nano gains SkyConnect/Connect ZBT-1/ZHA; the stray "sky connect" keyword is removed from Iris (it routed Zigbee-stick questions to dashboard design). The model tier audit is refreshed (sonnet now maps to Claude Sonnet 5), and the Step 5 routing output template gains the Language line the Language Rule already promised so specialists receive the detected language explicitly.

### Fixed

- **CHANGELOG 1.11.0 restored**: the v1.11.0 entry had been merged into 1.12.0 by mistake; it is split back out under its own 2026-06-12 header, matching the git tag history.
- **ROADMAP.md updated**: phases 2-8 are marked complete (all shipped by v1.6.x); the stale "contribution process is informal until Phase 8" note now points at CONTRIBUTING.md.
- **Freshness-check date** in `aurora/SKILL.md` had drifted (2026-05-23 while the banner said 2026-06-19); both now track the release date.

## [1.15.0] - 2026-06-19

### Added

- **ESPHome 2026.6.0 release reference** (`esphome/references/release-2026-6.md`), mirroring the 2026.5.0 reference: an at-a-glance summary, an upgrade checklist, sections with verified YAML for every new component, a compact breaking-changes table, a developer-facing breaking-changes section, a "what did not change" block, and four worked recipes (motion/IMU tilt sensor, PCM5122 HiFi player, router-speaker SPDIF/analog switcher, low-RAM ethernet node). Wired into `esphome/SKILL.md` Release Notes table. All YAML schemas verified against the upstream component docs.
- **New ESPHome component coverage** added as targeted markers in the topic reference files: the `motion` IMU hub with BMI270 and LSM6DS drivers (`sensors.md`), the PCM5122 audio DAC and `router` speaker plus any-bit-depth audio (`media-audio.md`), FTDI and Prolific USB-serial drivers and the DLMS/DSMR overhaul (`communication.md`), `light.effect.next` / `light.effect.previous` (`lights.md`), LVGL improvements and the Waveshare AMOLED panel (`displays.md`), YAML frontmatter, `esphome.build_flags`, and Codeberg sources (`packages-modular-config.md`), RP2040/RP2350 `variant` and `esp32` flash options (`boards.md`).

### Changed

- Documented the ESPHome 2026.6.0 platform changes: ESP8266 now defaults to `min_auth_mode: WPA2` (`security-hardening.md`), and `enable_on_boot: false` now reclaims internal SRAM on WiFi and ethernet (`power-management.md`).
- Reconciled the legacy-dashboard claims across the ESPHome skill: ESPHome Device Builder 1.0.0 replaced the retired in-tree dashboard and is now the default in the Home Assistant add-on.

## [1.14.0] - 2026-06-13

### Added

- **Four new verified component profiles**, expanding the catalog from 10 to 14, each with an LCSC part number checked live against the JLCPCB parts API and a stock status: SHT31 (C80862, temp/humidity), AHT20 (C2757850, temp/humidity), BH1750 (C78960, ambient light, new `light/` category), and INA219 (C2155799, current/power monitor, new `power/` category). All four are in stock and extended-library.
- **Two new recipes that use the expanded catalog**, growing the library from 12 to 14: `daylight-lights` (BH1750, dim/switch lights by measured lux) and `dc-power-monitor` (INA219, measure DC current and power). Both cite verified LCSC numbers.

### Changed

- `weather-station` recipe now offers SHT31/AHT20 as higher-accuracy temperature/humidity swaps for the BME280, and `motion-light` points at the BH1750 (and the new `daylight-lights` recipe) as the real source for its lux threshold, which previously had no sensor behind it.

## [1.13.1] - 2026-06-13

### Added

- **JLCPCB stock tracking.** Component profiles gain an optional `sourcing.jlcpcb_stock_status` (`in_stock` / `low_stock` / `out_of_stock`), refreshed from the live JLCPCB parts API via `sync_jlcpcb_status.py --stock` (also wired into the monthly sync Action). Coarse on purpose so the catalog does not churn on hourly count changes. All 9 verified parts populated; a live check found MH-Z19B (C242514) and PIR AM312 (C114881) currently out of stock, NTC 10K and LD2410 low.
- **Out-of-stock warnings in delivery.** Volt's Iron Law 8 and the BOM format now require flagging any selected part whose `jlcpcb_stock_status` is `out_of_stock` or `low_stock` in the BOM Notes (and calling out out-of-stock parts in the README), so a build does not send the user to checkout for a part JLCPCB cannot supply.

## [1.13.0] - 2026-06-13

### Added

- **DEEP-mode snapshot demo + replay test.** `examples/deep-mode-co2-demo` ships a complete, valid `aurora-project.json` showing three specialists (Volt then Sage then Iris) building through one shared snapshot, plus the artifacts it references. `test_deep_mode_snapshot_replay.py` replays the lifecycle on every `examples/**/aurora-project.json`: schema validity, clean pipeline drain, a result per completed agent with no orphans, field provenance, resolved conflicts, referential integrity, profile-matched board/components, and ordered timestamps.
- **Eval regression gate.** `aurora/evals/run_evals.py` grades a saved iteration and compares with-skill scores to `aurora/evals/golden-baseline.json`, failing on any regression (`--update` re-baselines). The harness does not spawn subagents (live, non-deterministic); it gates the manually produced runs. Golden baseline seeded from iteration-2 and kept in lockstep with `evals.json`.
- **Conformance levels in `check-delivery.py`** (minimal / standard / strict): every check is tagged, `--level` gates the exit code, and the report names the highest level reached. New CI template `aurora/references/templates/aurora-check-workflow.yml` lets users gate their own project repos.

### Changed

- **Definitive language check** in `check-delivery.py`: every human-readable doc in a project must share one language (Swedish-letter detection plus stop-word fallback, code fences stripped), replacing the old README-vs-INSTALL heuristic.
- `check-delivery.py` CLI output switched to ASCII (no em dash or box-drawing characters) so it no longer crashes on Windows cp1252 stdout.

## [1.12.0] - 2026-06-13

### Added

- **Recipe library** at `aurora/recipes/`: 12 curated starting points that Aurora suggests and then generates into a full project. Covers CO2 monitor, motion light, weather station, fridge/freezer monitor, room presence (mmWave), home/away routine, energy dashboard, notification hub, vacation mode, greenhouse, smart thermostat, and button scene controller. Each recipe has a metadata header (intent, specialists, hardware flag, match keywords), a BOM skeleton citing verified LCSC numbers for hardware recipes, an automation-pattern sketch, a dashboard skeleton, and a Customise section.
- `aurora/recipes/_recipe-format.md` (format spec) and `aurora/recipes/_index.md` (the keyword-matched suggestion table).
- `aurora/SKILL.md` wiring: **Step 1.5 Offer a Recipe** suggests the 3-5 closest recipes when intent is broad (and skips for already-specified requests), and **Step 7.6 Recipe-to-project flow** turns a chosen recipe into a generated project with the user customising afterward.
- 78 contract tests in `aurora/tests/test_recipe_library.py`: required header keys and sections, slug/name agreement, index/file agreement, no invented LCSC numbers, no em dashes, and the SKILL.md wiring. Suite: 836 passed.

## [1.11.0] - 2026-06-12

### Added

- **Verified LCSC part numbers in component profiles.** 9 of 10 sensor profiles now carry real JLCPCB part numbers verified live against the JLCPCB parts catalog (SCD40-D-R2 C3659421, MH-Z19B C242514, BME280 C92489, BMP280 C83291, AM2302/DHT22 C83988, DS18B20+ C9753, HLK-LD2410-P C5183133, AM312 C114881, MF52A 10k B3950 C5439712), all extended-library. The capacitive soil sensor v1.2 stays TBD: it is a hobby breakout JLCPCB does not stock. Volt copies verified numbers into schematic.json and BOM.csv instead of TBD.
- **JLCPCB parts-status sync.** Component profiles gain an optional `sourcing` block (LCSC number, library type, MOQ, check date; schema minor-bumped to 1.1). `aurora/scripts/sync_jlcpcb_status.py` fills status from the public CDFER jlcpcb-parts-database CSV (format verified live), and the monthly `jlcpcb-sync.yaml` GitHub Action keeps it current. All 10 profiles stubbed with `lcsc: TBD`; a contract test rejects C-numbers without a verification date so numbers cannot be invented.
- **Support agents wired into DEEP mode.** Glitch, Probe, Lens, and Manual gain the Snapshot-Aware Coordination Iron Law: they reconstruct state from `aurora-project.json` instead of chat history, write only `validation_results.<name>` and `conflict_log` entries, and are now covered by the same 9 contract tests as the core specialists (108 snapshot tests total). The handoff protocol documents their read-only pattern.
- `aurora/scripts/validate_schematic.py` - executable netlist validator for `hardware/schematic.json`: schema validation plus refdes uniqueness, pin-in-two-nets (short) detection, undeclared component references, duplicate nets, ground-net presence, and TBD part reporting. Required to pass with zero errors before custom-PCB/production delivery (Volt Iron Law 8).
- The pin, I2C address, voltage-level, and conflict validator procedures now accept `schematic.json` as a machine-readable input when the project has one.
- OpenSCAD render test for the enclosure template (skips when OpenSCAD is not installed); template verified to produce a manifold STL with all four standoffs, vents, cable opening, and lid.
- Eval design table in `aurora/evals/README.md` now documents routing evals 4-9.

### Changed

- **ESPHome actions terminology adopted** after live verification against esphome.io: `api: actions:` with `- action:` items and `homeassistant.action` with `action:` replace the old service spellings across all ESPHome references, assets, and examples (60 renames). Old spellings remain supported upstream aliases; the skill never flags user configs that still use them.

## [1.10.0] - 2026-06-12

### Added

- **Fab-ready hardware delivery.** New machine-readable manufacturing exports specified in `aurora/references/deliverables/fab-export-format.md`:
  - `hardware/schematic.json` - netlist companion to SCHEMATIC.md, validated by the new `aurora/references/schemas/schematic.schema.json` (components with refdes/package/LCSC, nets with pins and design notes). Required at production tier, recommended at custom-PCB.
  - `hardware/BOM.csv` - JLCPCB-assembly-compatible BOM export (`Comment,Designator,Footprint,LCSC Part #`), prices stay in BOM.md.
  - `aurora/references/templates/enclosure.scad` - parametric OpenSCAD enclosure template (PCB standoffs, friction-fit lid, vents, cable opening, sensor window) ready to copy into `hardware/ENCLOSURE.scad`.
  - KiCad redraw workflow and a JLCPCB ordering workflow with a manual fab order log in MANUFACTURING.md (JLCPCB has no public status API).
  - Complete worked example shipped in `examples/water-leak-sensor/hardware/`, plus 17 tests in `aurora/tests/test_fab_export_specs.py`.
- Volt's Iron Law 8 tier lists, `pcb-format.md`, and `bom-format.md` wired to the new fab spec; `TBD` is allowed only in the LCSC column and never as an invented part number.

### Changed

- **Orchestrator working method hardened** after a full souls/routing audit:
  - New Routing Precedence rules break ties when keywords match several agents (Volt vs Nano, Echo sequences, Watt as pre-check, Glitch only for existing breakage).
  - New Step 2.6 Safety Gate: battery, mains, >5V, actuators, water, and outdoor projects must start with Vera hazard analysis; QUICK requests that trip the gate are promoted to DEEP mode.
  - Model recommendations audited: tier table now maps to concrete current models (Fable 5, Opus 4.8, Sonnet 4.6, Haiku 4.5), fable added as escalation tier, Probe downgraded to haiku.
  - Language Rule gains DEEP-mode consistency: language is detected once and recorded in the routing output; specialists never re-detect.
  - 14 contract tests in `aurora/tests/test_orchestrator_routing_rules.py` guard all of the above.

## [1.9.3] - 2026-06-12

### Added

- Four new reference files, each wired into its skill's Quick Reference:
  - `esphome/references/packages-modular-config.md` - `packages:` component, local/remote packages, `vars`, `!extend`/`!remove`, fleet pattern for short per-device files.
  - `home-assistant/references/jinja2-macros.md` - reusable Jinja2 macros via `custom_templates/`, imports, reload, limitations, recipes.
  - `home-assistant/references/labels-categories.md` - labels and categories for organizing entities and automations, label targeting in actions, label template functions.
  - `node-red/references/dashboard-2.md` - Dashboard 2.0 (@flowfuse/node-red-dashboard): core ui nodes, layout, HA sensor panel example, migration from Dashboard 1.
- `aurora/scripts/lint_ha_syntax.py` - CI-enforced guard against reintroduction of legacy HA syntax, with built-in knowledge of all intentional exceptions, plus strict parsing of every yaml-labelled markdown fence. 14 unit tests in `aurora/tests/test_lint_ha_syntax.py`.

### Changed

- **Repo-wide modernization to current HA automation syntax.** All starter templates, all 56 markdown files in `home-assistant/`, all `examples/*/automations.yaml` and dashboards, plus HA YAML snippets in `api-catalog`, `aurora`, `ha-dashboard-design`, `ha-integration-dev`, `node-red`, and the root TROUBLESHOOTING guide now use plural automation keys (`triggers:`, `conditions:`, `actions:`), `trigger:` instead of `platform:` in trigger lists, `action:` instead of `service:` in steps, and Lovelace `perform-action` instead of the deprecated `call-service` tap action. Intentional exceptions kept as-is: blueprint selector keys, sensor/device_tracker `platform:` keys, browser_mod fire-dom-event blocks, ESPHome `homeassistant.service:` and `api: services:` schema, and the legacy sides of before/after examples in `migration-guide.md` and the official 2026 snapshots.
- `migration-guide.md` now documents the HA 2024.8 action rename and the HA 2024.10 trigger/plural-key rename, and its "NEW" examples were brought up to current syntax.
- UI references updated across 16 files: "Developer Tools > Services" is now "Developer Tools > Actions", matching the renamed HA panel.
- 93 markdown fences that were never YAML (Jinja templates, entity lists, CLI output) relabeled from yaml to jinja2 or text, so fence validation is now strict.
- ESPHome syntax policy documented in `esphome/SKILL.md`: the repo keeps `api: services:` and `homeassistant.service:` until the upstream rename to `actions:`/`homeassistant.action` is verified against current ESPHome docs.
- `examples/pool-controller/README.md` attribution banner moved below the H1 per the canonical manual format (fixes a failing attribution test present since v1.9.0).
- Remaining Swedish comments and example strings translated to English in the M5Stack Atom Echo configs and the HA usage guide.
- HA skill Quick Reference now marks the official 2026 trigger/condition/action files as primary and the older curated files as supplementary legacy depth.

## [1.9.2] - 2026-05-30

### Changed

**Home Assistant reference refresh from official 2026 docs snapshot.** Four core reference files updated against the official HA documentation (snapshot 2026-05-30, HA 2026.5.4):

- `actions.md` — two new sections: Dashboard Actions (all seven Lovelace tap/hold action types plus confirmation dialogs) and Response Variables (capturing return data from weather, calendar, and other actions). All `service:` keys in YAML examples replaced with `action:`.
- `conditions.md` — new Device-Specific Conditions section covering seven logical groups (binary state, alarm, climate, numeric/threshold, mobile robots, timer, calendar) including `calendar.is_event_active`. New Selection Guide table. Deprecated `match: any` pattern corrected to `condition: not`.
- `triggers-advanced.md` — new Device Trigger Inventory covering 18+ domains grouped by type. New Calendar Trigger section. All `platform:` keys in YAML examples replaced with `trigger:`.
- `automations.md` — modernized throughout: all top-level automation keys use plural forms (`triggers:`, `conditions:`, `actions:`), all trigger list items use `trigger: state` instead of `platform: state`, all step keys use `action:` instead of `service:`.

**Quick Reference now covers all 50 reference files.** The HA YAML skill's Quick Reference table previously listed 27 files. Added the remaining 23: configuration, device-class-units, trigger-templates, utility-meter, statistics, customize, voice-assistants, zigbee-controllers, esphome-patterns, mqtt-integration, integrations-bluetooth, integrations-cameras, integrations-media, integrations-ai-llm, integrations-common, integrations-shelly, integrations-tasmota, integrations-tuya, weather-integration, backup-restore-migration, migration-guide, hacs-popular, system-monitor, custom-components, and custom-card-development.

**Official 2026 reference files wired into skill load order.** `home-assistant/SKILL.md` now includes a dedicated "Official Reference Files" section directing Claude to read `actions-2026-official.md`, `triggers-2026-official.md`, or `conditions-2026-official.md` before generating any automation YAML. These files supersede the older curated files for syntax questions.

## [1.9.1] - 2026-05-23

### Fixed

**`/aurora:aurora` path-resolution regression (latent since 2026-01-03).** The slash command at `commands/aurora.md` instructed Claude to "Read and follow `aurora/SKILL.md` exactly" using a relative path. Claude resolved that path against the user's current working directory rather than the plugin install directory, so `/aurora:aurora` invoked from any project that wasn't itself an Aurora-structured repo produced the message "the aurora directory doesn't exist in the project yet" and offered to create the file in the user's project. This regression existed in every release from the introduction of the aurora plugin structure (commit `1b8410e`, 2026-01-03, pre-v1.7.0) through v1.9.0, a total of 15 releases. It was not visible during local development because the developer's working directory was always the Aurora repo itself, where the relative path resolved correctly by coincidence. A demo-environment test in a non-Aurora working directory exposed it.

The fix updates `commands/aurora.md` to be explicit that the orchestrator file lives in the plugin install directory, not the user's project, and adds a "Path conventions" section at the top of `aurora/SKILL.md` that clarifies the same rule for every reference Aurora makes to its own files (`aurora/`, `esphome/`, `home-assistant/`, `ha-integration-dev/`, `node-red/`, `api-catalog/`, `ha-dashboard-design/`).

If you ever invoked `/aurora:aurora` from a project that wasn't a fresh smart-home build inside the aurora-smart-home repo and got a confusing "doesn't exist" response, this is the bug.

## [1.9.0] - 2026-05-22

### Added

**Full ESPHome 2026.5.0 alignment.** A new reference file at `esphome/references/release-2026-5.md` documents every user-visible change in the May 2026 ESPHome release: Sendspin multi-room synchronized audio, the `radio_frequency` entity type, Zigbee built into core for ESP32-C6 and H2, the `modbus_server` split, native ESP-IDF toolchain, OTA partition and bootloader updates over the wire, soft-brick recovery via `safe_mode` plus factory partition, the BLE coex fix that resolves `status=133` failures on Yale and August locks, and more. The file includes a step-by-step upgrade playbook, five complete worked recipes, and a separated developer-facing breaking-changes section.

**Examples library expanded from 4 to 27 projects.** Twenty-three new copy-paste-ready examples cover sensors (battery temp, soil moisture, water leak, mailbox, air quality), climate and HVAC (Panasonic AC, smart thermostat, pool), audio and voice (Sendspin whole-house audio, voice assistant on ESP32-S3-BOX), displays (e-paper weather station, LVGL wall panel, M5Stack ATOM), lighting and power (LED strip with effects, smart plug with BL0942 power monitor, motorized blinds), energy and EV (Growatt solar inverter Modbus polling, OpenEVSE charger control), Bluetooth and RF (proxied Yale/August locks, CC1101 RF gateway with `radio_frequency` entity), security and access (ESP32-CAM doorbell, fingerprint unlock), plus a battery-powered Zigbee temperature sensor on ESP32-C6. Each example ships the same five files: ESPHome YAML, README with wiring and safety and troubleshooting, ready-made Home Assistant automations, Lovelace dashboard, and secrets template.

**First vendored ESPHome component.** Aurora now ships a local copy of `panasonic_ac` (originally `DomiStyle/esphome-panasonic-ac`, MIT-licensed) at `esphome/components/panasonic_ac/`. Builds work offline without fetching from GitHub at compile time. The vendored directory preserves the upstream LICENSE verbatim, and a `NOTICE.md` records the upstream commit SHA, SHA-256 hash of each file, and a statement of any Aurora-side modifications (currently none).

**Twelve domain references gained 2026.5.0 sections.** `media-audio.md` got Sendspin multi-room audio, SPDIF speaker output, the new `audio_http` media source, and the WAV-codec and `codec_support_enabled` changes. `ble-proxy.md` got the `status=133` coex fix narrative and the `esp32_ble: use_psram` option. `power-management.md` got `esp32: watchdog_timeout`, the main-loop overhaul, and the per-platform idle-feed defaults. Lock OPENING and OPEN states landed in `alarm-security.md`. Additional 2026.5.0 content in `sensors.md`, `communication.md`, `displays.md`, `remote-rf-ir.md`, `voice-local.md`, `boards.md`, `popular-devices.md`, `security-hardening.md`, and `external-components.md`.

**README "What's new" section** highlights twelve user-visible ESPHome 2026.5.0 wins (multi-room audio, Zigbee on C6/H2, `radio_frequency` entity, longer battery life, BLE proxy reliability, ESPHome Device Builder beta, native ESP-IDF toolchain, more RAM via PSRAM Bluedroid, SPDIF audio, ESP32-P4 USB high-speed, lock OPENING/OPEN states, `modbus_server` split).

### Changed

- ESPHome compatibility badge bumped to 2026.5.0.
- `esphome/SKILL.md` Quick Reference now includes a Release Notes pointer to `release-2026-5.md`.
- **Skill orchestrator polish:** fixed a release-date mismatch between the banner and the freshness fallback in `aurora/SKILL.md`; added a cross-skill handoffs table to `home-assistant/SKILL.md` routing external-API, firmware, Python integration, visual-flow, and dashboard-styling requests to the right specialist; added a Process flowchart to `node-red/SKILL.md` for consistency with the other three specialists; documented the reactivation check's literal-string matching as a known boundary with a manual verification recipe.

### Compliance

- New `.claude/CLAUDE.md` "Copyright and Third-Party Content" section governs how Aurora vendors and attributes external code: never copy upstream prose verbatim, always preserve license notices, strip contributor handles from Aurora-authored summaries, paraphrase aggressively when in doubt.

## [1.8.1] - 2026-05-17

### Added

**Custom PCB builds are now first-class in Volt.** A new Mode C in the board selector triggers when you say "custom PCB", "bare chip", "bare module", or "production hardware". Volt loads three new Espressif module profiles -- ESP32-S3-WROOM-2 (16MB flash, 8MB OPI PSRAM), ESP32-C3-MINI-1 (13x17mm, 5uA deep sleep), ESP32-C6-MINI-1 (Thread/Zigbee/WiFi6, Matter-native) -- and always emits the prototype-first workflow: validate GPIO on the dev kit first, then swap to the bare module for PCB layout.

**All 20 board profiles now carry two new fields.** `esphome.board` gives the exact value to paste into the ESPHome `board:` key -- no more guessing or falling back to boards.md. `board_type` tags every profile as `dev_board`, `specialty_board`, `commercial_device`, or `module`, so the board selector can filter correctly.

### Fixed

**Commercial devices (Shelly, Sonoff) no longer appear as fresh-build recommendations.** The board selector now filters out `commercial_device` boards from Mode A results. They were never wrong choices technically, but recommending a Sonoff Basic R3 when someone asks "which ESP board should I buy" is confusing.

**LilyGO T-Display S3 default I2C pins silently conflict with the ESPHome logger.** GPIO43 (SDA) and GPIO44 (SCL) are also UART0 TX/RX -- the pins ESPHome's logger uses by default. Connecting an SCD40 or other I2C sensor to the default pins would cause silent communication failures. The conflict is now documented in `strapping_conflict_warnings` with the fix: add `logger: baud_rate: 0` or remap I2C.

**Board profile search documented as recursive.** `board-selector.md` now explicitly lists all subdirectories (`esp32/`, `esp8266/`, `rp/`, `special/`, `smart-home/`, `module/`) and flags that a flat search misses `special/` and `smart-home/` entirely.

**Data integrity tests added for three specialty boards.** Heltec WiFi LoRa32 v3, M5Stack Atom Lite, and M5Stack Core Basic now have targeted tests alongside the existing LilyGO T-Display S3 suite.

## [1.8.0] - 2026-05-15

### Added

**Aurora will now refuse to build a dangerous project without a safety review.** The moment your request includes a Li-ion battery, a relay switching mains, an outdoor enclosure, or anything above 5V — Vera steps in before Volt touches a single GPIO. She runs a structured hazard analysis, scores every risk on a severity-likelihood matrix, and writes `hardware/HAZARD-ANALYSIS.md` to disk: hazard table, required mitigations, residual risk, and a sign-off block. If she finds a Critical-rated hazard she raises a blocker and Volt cannot proceed until it is resolved. This is the first time an AI smart-home tool has said "not yet — fix this first" on safety grounds, and meant it.

**The question every Aurora build ends with — "but how do I get this into Home Assistant?" — now has four documented answers.** New `aurora/references/ha-integration/` covers every realistic path from generated file to running HA instance: paste into the UI editor with no server access at all; drop files into a folder and let `!include_dir_named` pick them up on restart; sync via Samba share, SCP, or the File Editor add-on; or pull from a git repo and get version history and one-command rollback for free. A `pattern-selector.md` walks you through which one to pick with a decision flowchart and a recommended default per agent.

**Aurora can now audit its own deliveries.** Run `python aurora/scripts/check-delivery.py <project-folder>` after any build and get a pass/fail verdict on every rule that matters: required files present, attribution banners in place, README has all its sections, BOM has a price datestamp, PCB files are in `hardware/` and not accidentally left in `esphome/`, INSTALL.md language matches the README. Every specialist's delivery contract — Volt's Iron Law 8, Sage's Iron Law 3, all of them — now ends with this step. No more "I think it's done." Either the script says DELIVERY APPROVED or it lists exactly what to fix.

### Changed

**Your electronics files finally have their own home.** `SCHEMATIC.md`, `PCB-NOTES.md`, `MANUFACTURING.md`, `COST-ANALYSIS.md`, `CERTIFICATION.md`, `TEST-JIG.md`, `HAZARD-ANALYSIS.md`, and split-out `BOM.md` / `WIRING.md` all move from `<project>/esphome/` to `<project>/hardware/`. The firmware folder stays clean. The hardware folder holds everything that describes the physical device. `check-delivery.py` flags any PCB file still living in `esphome/` as a placement error. **Breaking change from v1.7.x** — if you have an existing project with PCB files under `esphome/`, move them to `hardware/`.

**Vera is no longer a stub.** The original soul was a placeholder — a character sketch with no Iron Laws and no delivery contract. v1.8.0 ships the full implementation: two modes (hardware safety review and WAF review), six Iron Laws including the HAZARD-ANALYSIS.md requirement and the Critical-risk blocker, and full snapshot-aware coordination for DEEP mode. If you asked Vera for a safety review before today, you got a chat response. Now you get a file on disk.

## [1.7.12] - 2026-05-15

### Added

**Install-Format-Disclosure Rule: Sage now ships both automation and package format when the project has helpers, scripts, or template sensors alongside the automation.** Pick the install path at install-time, not at generation-time. The README "Installation" section presents Option A (paste into HA UI) and Option B (drop as package) clearly separated, with a one-line recommendation. Single automations still ship as one paste-ready file with no Option B noise.

**Iris dashboard installation now shows both options.** Option A: Raw Configuration Editor paste (recommended, fast, no restart). Option B: YAML-mode dashboard in `configuration.yaml` (advanced, file-on-disk, git-friendly).

**File-header comments in every generated YAML.** Every `automations/<name>.yaml`, `packages/<name>.yaml`, and `dashboards/<name>.yaml` opens with a 2-3 line `#` comment that names the install method and points at any alternative file. You know what the file is just from opening it; no need to flip back to the README.

**User override for project structure.** If you explicitly request "skip the project folder, just put the YAML in this directory" or "don't make subdirectories", Aurora confirms once and respects the choice. The Project Structure Rule is the default contract, not an absolute ban; you own your workspace.

### Fixed

**INSTALL.md, TROUBLESHOOTING.md, BOM.md, WIRING.md, and README.md are now written in your language.** A user reported that even when the conversation was in Swedish, INSTALL.md came back in English. The Language Rule for Deliverables in `aurora/SKILL.md` already required this, but the runtime kept defaulting INSTALL.md and TROUBLESHOOTING.md to English "because they are technical". Three layers of enforcement now defeat the regression: (1) `aurora/SKILL.md` Language Rule has an explicit per-file enforcement clause for the five human-readable files. (2) Volt's Iron Law 8 and `esphome/SKILL.md` Delivery Contract reference the Language Rule directly. (3) Every install template in `aurora/references/templates/install-*.md` opens with a TRANSLATE-FIRST banner so the specialist sees the translation instruction the moment she opens the template, not before. Quoted commands, file paths, and identifiers stay English; the surrounding prose follows you.

**Multi-agent README ownership is now defined.** Earlier versions left it ambiguous whether Volt + Sage projects produced one shared README or two competing ones. The Project Structure Rule now states: the FIRST specialist invoked writes the root README, and each subsequent specialist APPENDS an H2 section for its own contribution. No competing READMEs, no overwrites, no duplicate Attribution banners.

**HACS-ready integrations have an explicit root-level exception.** Ada's `hacs.json`, `LICENSE`, and `.github/workflows/validate.yaml` are allowed at the project root, listed in a closed whitelist in the Project Structure Rule. The "ONLY to its own subdirectory" rule has a documented exception list instead of a contradiction.

## [1.7.11] - 2026-05-15

### Added

**Project Structure Rule enforces a canonical hierarchical layout for every project Aurora delivers.** A user testing v1.7.10 reported that multi-agent projects (firmware + automation) scattered into separate top-level folders (`co2-monitor/` and `co2-alert/`) instead of living together in one project folder with subdirectories. The new rule lives in `aurora/SKILL.md` alongside Question Rule and Language Rule, and is enforced as an Iron Law by every specialist that writes files.

Canonical layout:

```
<project-name>/
├── README.md                  ← master document
├── aurora-project.json        ← snapshot (DEEP mode only)
├── esphome/                   ← Volt (firmware + INSTALL + TROUBLESHOOTING + PCB files)
├── automations/               ← Sage (automations)
├── scripts/                   ← Sage (scripts)
├── blueprints/                ← Sage (blueprints)
├── packages/                  ← Sage (packages)
├── dashboards/                ← Iris
├── node-red-flows/            ← River
└── custom_components/         ← Ada (HA standard, unchanged)
```

Per-agent ownership: each agent writes ONLY to its canonical subdirectory. The root `README.md` is written by the agent that started the project and links to each contribution by subdirectory.

### Changed

**Iron Law 8 (Volt) updated.** Volt now writes only to `<project>/esphome/` plus the root `<project>/README.md`. All YAML, secrets template, INSTALL.md, TROUBLESHOOTING.md, and PCB-tier artifacts (SCHEMATIC.md, PCB-NOTES.md, MANUFACTURING.md, COST-ANALYSIS.md, CERTIFICATION.md, TEST-JIG.md) live under `esphome/`.

**Iron Law 3 (Sage, Ada, River, Iris) updated.** Each soul names its canonical subdirectory:

- Sage → `<project>/automations/`, `<project>/scripts/`, `<project>/blueprints/`, `<project>/packages/`
- Ada → `<project>/custom_components/<integration_id>/` plus root-level `hacs.json`, `LICENSE`, `.github/workflows/validate.yaml` for HACS-ready repos
- River → `<project>/node-red-flows/`
- Iris → `<project>/dashboards/`

**Same rule applies to QUICK and DEEP mode** so the layout is dependable regardless of project type. No flat fallback for single-agent projects — even a single Sage automation lives in `<project>/automations/<name>.yaml`.

### Testing infrastructure

- `test_skill_has_project_structure_rule` locks the Project Structure Rule section and the canonical-subdirectory list in `aurora/SKILL.md`.
- `test_souls_enforce_project_subdirectory` verifies each of Volt, Sage, Ada, River, Iris souls names its canonical subdirectory. A future edit that drops the subdirectory reference fails the build.

## [1.7.10] - 2026-05-15

### Changed

**Clustered questions now close with "run with recommendations?" instead of asking the user to type a string of numbers.** A user testing v1.7.9 reported that being asked to reply `1, 1, 1` to three clustered questions (board / manufacturing tier / deployment method) was high cognitive load — they had to read every option, remember three numbers, and worry about getting the order right. The Question Rule in `aurora/SKILL.md` now requires a "Clustered questions" sub-section that closes any multi-question prompt with a summary list of recommendations and a plain Yes / No / own-choices question:

```
Summary of recommendations:
- <recommended-1>
- <recommended-2>
- <recommended-3>

**Do you want to run with all the recommendations above? [Yes / No / your own choices]**
```

Three reply modes documented inline so the user never has to remember a magic word:

- `Yes` — Aurora uses every recommended value and starts generating.
- `No` — Aurora asks the questions one at a time so the user can think them through.
- Own choices (numbers like `2, 1, 3` or free-form text) — Aurora uses what the user specifies.

Single-question prompts skip the summary block — one question, one recommendation, one answer.

`test_clustered_questions_offer_run_with_defaults` in `test_skill_md_structure.py` locks the rule.

## [1.7.9] - 2026-05-15

### Fixed

**Question Rule no longer collapses to a single recommendation.** The v1.7.8 eval suite caught a case where Volt answered the deployment-method question by tagging one option as "Recommended" but skipped listing the alternatives. The user sees a recommendation without knowing what they are choosing against. The Question Rule now explicitly states that every available option must be listed first, and `Recommended:` is a tag attached to one of the listed options — never a replacement for the list.

**INSTALL.md commands now come from the template verbatim.** The same eval suite caught Volt paraphrasing `pip install esphome` to free-text equivalents. The user copy-pastes those commands; drift in spelling or flags breaks the paste. Volt's Iron Law 8 now declares a Template fidelity rule: placeholders (`{device_name}`, `{yaml_filename}`, etc.) are adapted, but everything else — code blocks, section headings, prose order, troubleshooting cases — is reproduced exactly. Project-specific additions go in a separate "Project-specific notes" section at the end, never inlined into template steps.

### Verified

Re-ran eval-1 and eval-3 against this commit. Both runs now pass every assertion (3/3 and 4/4, up from 2/3 and 3/4 in v1.7.8's iteration-1).

## [1.7.8] - 2026-05-15

### Added

**Regression eval suite for the v1.7.7 runtime principles.** A new `aurora/evals/` folder ships three test prompts that exercise the four principles introduced in v1.7.7 (specific-board confirmation, deployment-method question, Question Rule with recommendations, Language Rule for deliverables). For each prompt, paired subagent runs (with-skill + baseline) produce outputs that a grader scores against explicit assertions. The principle-pinning pytests in `aurora/tests/test_v177_principles.py` check that the rules are written down; this eval suite checks that an actual agent follows them when handed a real prompt.

The suite is human-triggered — running it spawns paired subagents and costs API tokens, so CI runs the structural validation in `aurora/tests/test_evals_suite.py` (4 cases) but does not spawn agents. `aurora/evals/README.md` documents the workflow.

First iteration ran on this commit gave the with-skill version a +27 percentage-point edge over baseline (9/11 vs 6/11 across three evals), with the biggest gains on attribution-banner enforcement and INSTALL.md generation under the Language Rule.

## [1.7.7] - 2026-05-15

### Added

**Question Rule — every question Aurora or a specialist asks now ships with a recommendation and a reason.** Listing bare options put the decision burden on someone who came to Aurora precisely because they did not have that domain knowledge. Picking a board, a deployment method, or a sensor variant is exactly the kind of decision Aurora is supposed to help with. The rule lives in `aurora/SKILL.md` so every specialist inherits it.

**Language Rule — generated project folders follow your language for human-readable docs.** A Swedish user who types "bygg en CO2-mätare" now gets a Swedish `README.md`, `INSTALL.md`, and `TROUBLESHOOTING.md`. YAML keys, entity IDs, GPIO labels, and the attribution banner stay English because they are code. The boundary is documented explicitly so the agent does not over-translate identifiers or under-translate human text.

**Deployment-method question for hardware projects.** Volt now asks how you want to flash the firmware before generating YAML, with four options:

1. **HA ESPHome Add-on** (recommended) — paste YAML into Home Assistant, HA compiles server-side and flashes via USB or OTA.
2. **GitHub Actions + web.esphome.io** — for users without HA and without a local Python toolchain; GitHub compiles the firmware and the project's `.github/workflows/build-firmware.yml` publishes a `.bin` that flashes from the browser.
3. **Local ESPHome CLI** — for users with `esphome` installed locally.
4. **Docker self-hosted ESPHome dashboard** — for power users running a home server.

Each option ships its own `INSTALL.md` content and supplementary files (workflow YAML for option 2, `docker-compose.yml` for option 4). Template snippets live in `aurora/references/templates/install-*.md`.

### Fixed

**Volt no longer defaults to a generic breadboard config when the user says only "ESP32-S3".** Iron Law 1 now demands the **specific board model** (ESP32-S3-DevKitC-1, Lolin S3 Mini, XIAO ESP32-S3, M5Stack Atom S3, etc.), not just the chip family. Reference data in `aurora/references/boards/` ships per dev-board, and picking the wrong board profile means validators check the wrong GPIO map and miss real conflicts. If the user names only a chip family, Volt asks which specific board, applying the Question Rule.

**Volt no longer recommends `esphome run` as the default install path.** Local CLI is now option 3 of 4, reserved for users who already have ESPHome installed. The default for HA users is the Home Assistant ESPHome Add-on.

## [1.7.6] - 2026-05-15

### Added

**Reactivation Check skips the banner on repeat `/aurora:aurora` invocations.** Previously, typing `/aurora:aurora` a second time in the same conversation re-ran the version check (a `gh` API call), reprinted the full banner, and re-asked the opening question. Aurora now detects that the banner has already been shown earlier in the conversation and responds with a short acknowledgement before going straight to routing. No more banner spam mid-session, no wasted gh calls.

### Changed

**README "How Aurora works" diagram clarified.** The previous diagram showed `/aurora:aurora + "build a CO2 monitor"` as a single combined input, which was ambiguous about whether you can activate Aurora on its own and then ask in a second turn. The diagram now shows both flows side by side (inline vs two-step) and notes that re-running `/aurora:aurora` later in the same conversation skips the banner.

## [1.7.5] - 2026-05-14

### Fixed

**Stale attribution propagated into delivered files.** Templates, example projects, and reference snippets still carried pre-v1.3 plugin names (`esphome@aurora-smart-home`, `ha-yaml@aurora-smart-home`, `ha-integration@aurora-smart-home`, `node-red@aurora-smart-home`, `supercharge-*-skill`, `esphome-assistant vN`) in their `Generated by` lines. Agents copy these templates verbatim, so the wrong attribution was reaching user projects even after the v1.6.6 cleanup of the SKILL.md rule. All 112 affected template, example, script, and reference files updated to the canonical `aurora@aurora-smart-home (<sub-skill> skill) v1.7.5` form.

**Version-check could miss newer releases due to string comparison.** The version-check at `/aurora:aurora` invocation now applies an explicit integer-tuple semver comparison rule (with a Python reference snippet inlined in `aurora/SKILL.md`). Earlier wording allowed a runtime to treat the version segments as strings, in which case `1.7.10` would be incorrectly judged less than `1.7.4` and no update notice would appear.

**LICENSE files were inconsistent.** Root `LICENSE`, `esphome/LICENSE`, and `node-red/LICENSE` carried different name spellings and different copyright years. All three now read `Copyright (c) 2024-2026 Tony Löfgren`, matching the owner field in `.claude-plugin/marketplace.json`.

### Changed

**Banner clarity: `3 Model Tiers` → `Opus / Sonnet / Haiku`.** The previous wording was ambiguous - the table below the banner lists subscription tiers (Free, Pro, Team/Max) which are also three, so users could not tell which "tiers" the banner referred to. The new line names the three models directly. Banner box width unchanged.

**Attribution moved to top-of-file banner in three more docs.** `TROUBLESHOOTING.md`, `SKILL-INTEGRATION.md`, and `examples/complete-smart-room/README.md` previously carried a footer `Generated with [aurora-smart-home](...)` line. These now use the v1.7.2 banner-blockquote form (`> *Generated by [aurora@aurora-smart-home (<skill> skill)](...)*`) placed under the H1. Three example READMEs that were missing the banner entirely (`energy-monitor`, `smart-garage`, `smart-greenhouse`) got it added.

**Stale repository name removed.** Six files (`esphome/INSTALLATION.md`, `esphome/USAGE-GUIDE.md`, `esphome/references/{arduino-conversion,cookbook,solar-energy}.md`, `home-assistant/INSTALLATION.md`) still linked to the pre-rename `supercharge-smart-home-claude-skills` GitHub repository. All now point at `aurora-smart-home`.

## [1.7.4] - 2026-05-14

### Fixed

**Runtime regression: Iron Law 8 / Iron Law 3 silently bypassed.** A user testing v1.7.3 reported that `/aurora:aurora` for an ESP32 + LD2410 project generated the YAML file at the workspace root, without a project folder, without a README, without BOM/wiring/installation/troubleshooting/recovery sections, and without the attribution banner. Root cause: two layers were wrong.

1. **`esphome/SKILL.md`, `home-assistant/SKILL.md`, and `ha-integration-dev/SKILL.md`** all offered a `Copy from chat` output option and said `save to current directory`. That text actively contradicted Iron Law 8 / Iron Law 3 in the souls.
2. **`aurora/SKILL.md`** never instructed the orchestrator to **load the specialist's soul file** before delegating. Iron Laws lived in `aurora/souls/<agent>.md` but were not in the runtime context when the specialist started work.

### Changed

**`Copy from chat` removed from three SKILL.md files:**

- `esphome/SKILL.md` First Step + Output method now both create a project folder. `Copy from chat` gone.
- `home-assistant/SKILL.md` Output method removed; project-folder-only.
- `ha-integration-dev/SKILL.md` Output method removed; project-folder-only.

**Delivery Contract block added to top of `esphome/SKILL.md`:**

A new block placed BEFORE `## First Step` states explicitly: "Every output is a set of files in a project folder on disk. Chat output is not delivery. A described BOM is not a written BOM." The block lists the required artifacts and points at Iron Law 8 (in `aurora/souls/volt.md`) and the format specs in `aurora/references/deliverables/`. Putting the contract before the scope question is what gets Volt to read it first.

**`aurora/SKILL.md` Step 2.5 added: Load Specialist Soul:**

After routing to an agent in Step 2, Aurora now loads the agent's soul file from `aurora/souls/` before delegating. This puts Iron Law 8 (Volt) and Iron Law 3 (Sage / Ada / River / Iris) into the runtime context so the specialist actually follows the delivery contract instead of falling back to generic skill instructions.

### Testing infrastructure

- New `test_delivery_contract_in_skills.py` with parametrised tests across `esphome`, `home-assistant`, and `ha-integration-dev` SKILL.md:
  - No SKILL.md may offer "Copy from chat" as an output option.
  - Each SKILL.md must mention "project folder".
  - Each SKILL.md must state explicitly that chat output is not delivery.
  - Plus esphome-specific spot checks: Delivery Contract block exists before First Step, and references volt.md + the deliverables specs.
- `test_skill_md_structure.py` extended with `test_aurora_skill_loads_specialist_soul_before_delegating` (locks the Step 2.5 instruction).

## [1.7.3] - 2026-05-14

### Changed

**Version check simplified to gh CLI only, WebFetch fallback removed:**

- `aurora/SKILL.md` Version Check now uses a single best-effort path: `gh release view --json tagName -R tonylofgren/aurora-smart-home --jq '.tagName'`. If gh succeeds and returns a newer tag, the update notice is shown. If gh fails for any reason (missing, unauthenticated, no releases, parse error), Aurora proceeds to the banner silently.
- The WebFetch fallback in v1.7.2 leaked tool errors to the user when the runtime had a context-mode-style WebFetch wrapper. Claude Code's tool runtime emits "Error: WebFetch blocked" before Aurora can decide to suppress it, so any chained fallback that includes WebFetch shows the error regardless of SKILL.md instructions. Removing WebFetch is the only way to keep the path quiet on blocked runtimes.
- `WebFetch` removed from `aurora/SKILL.md` `allowed-tools` since it is no longer used.
- Test contracts updated: `test_skill_version_check_uses_gh_cli` replaces the previous WebFetch-presence test; `test_skill_version_check_does_not_use_webfetch` and `test_skill_allowed_tools_excludes_webfetch` lock the removal.

## [1.7.2] - 2026-05-14

### Changed

**Version check hardened with `gh` CLI primary + WebFetch fallback:**

- Version Check in `aurora/SKILL.md` now tries `gh release view --json tagName -R tonylofgren/aurora-smart-home --jq '.tagName'` first, then falls back to `WebFetch` against the raw marketplace.json. The `gh` path is more robust because it works through Bash (not blocked by context-mode-style WebFetch wrappers), authenticates via the user's gh-token (5000 req/hour instead of 60), and returns the exact release tag rather than the full marketplace.json that has to be parsed.
- Silent on every failure mode: gh missing, WebFetch blocked, network down, parse error all skip the check without surfacing any technical message to the user. Network errors and runtime sandbox restrictions are the same outcome from the user's perspective.
- Retroactive GitHub releases: `v1.7.0`, `v1.7.1`, and `v1.7.2` tagged on their respective bump commits so `gh release view` has releases to compare against.

**Attribution moved from README footer to README banner (top, under H1):**

- The project README's Aurora attribution is now a Markdown blockquote directly under the H1 title, not a footer at the end of the file. Format: `> *Generated by [aurora@aurora-smart-home (<skill> skill)](https://github.com/tonylofgren/aurora-smart-home)*`. The footer position made the GitHub repo invisible to anyone who did not scroll all the way down. The banner position puts the link at eye-height where it belongs.
- Updated across `aurora/references/deliverables/manual-format.md` (the "Attribution banner" section replaces the old "Attribution footer" section with per-skill examples and a top-of-README structural example).
- Updated in all four skill SKILL.md Code Attribution sections (esphome, home-assistant, node-red, ha-integration-dev) so the Markdown bullet point now reads `as a blockquote banner directly under the H1 title (top of file)` instead of `as a footer`.
- Updated in five soul files (Volt Iron Law 8; Sage / Ada / River / Iris Iron Law 3) so the language consistently says "banner" and "top of file" instead of "footer" and "ends with".
- The HACS README template inside `ha-integration-dev/SKILL.md` now places the attribution blockquote directly under `# My Integration` (above the HACS / GitHub Release badges) and removes the previous footer block.

### Added

**`made-with-aurora-skill` GitHub topic for discovery:**

- Every Aurora-generated project that gets published to GitHub should carry the `made-with-aurora-skill` topic. This is the universal discovery hook for the Aurora community across HACS integrations, ESPHome projects, automations, Node-RED flows, and dashboards. Findable via `https://github.com/topics/made-with-aurora-skill` or `gh search repos --topic made-with-aurora-skill`.
- `aurora/references/deliverables/manual-format.md` reorganised: the topics section is split into Discovery topic (always `made-with-aurora-skill`) and Domain topics (ecosystem-specific). The gh paste-blocks for Ada (HACS publish) and Volt (ESPHome publish) now start with `gh repo edit --add-topic made-with-aurora-skill`. Sage / River / Iris get their own short topic recipe.
- The agent never runs `gh` commands itself. The block is informational; the user runs it when they want to publish.

## [1.7.1] - 2026-05-14

### Added

**Version check at every `/aurora:aurora` activation:**

- Aurora now fetches `https://raw.githubusercontent.com/tonylofgren/aurora-smart-home/main/.claude-plugin/marketplace.json` via `WebFetch` before emitting the banner. The fetched `version` field is compared against the installed version. If GitHub has a newer version, Aurora prints a notice with the exact version delta plus the update command before the banner appears.
- The fetch is silent on success and silent on failure (no network, GitHub down, parse error). Network problems never block a session.
- The previous 90-day local Freshness Check is kept as a fallback for when WebFetch is unavailable.
- `WebFetch` added to `aurora/SKILL.md` `allowed-tools`. Four new pytest contracts lock the version-check section, the WebFetch reference, the URL target, and the `allowed-tools` inclusion.

## [1.7.0] - 2026-05-14

### Added

**Complete-delivery contracts across every DEEP-mode specialist:**

- Volt's new **Iron Law 8 (Complete Delivery)** blocks hardware-project delivery until every required artifact exists on disk in the project folder: `<device-name>.yaml`, `secrets.yaml.example`, and a `README.md` carrying What this does, BOM with estimated unit prices and a dated total, wiring (connection table + ASCII diagram + power budget + safety notes), installation steps, calibration procedures, troubleshooting for the three most likely failures, and recovery instructions.
- Manufacturing tier (`breadboard` / `perfboard` / `custom-PCB` / `production`) asked at project start determines extra artifacts. Custom-PCB tier adds `SCHEMATIC.md` and `PCB-NOTES.md`. Production tier additionally adds `MANUFACTURING.md`, `COST-ANALYSIS.md`, `CERTIFICATION.md`, `TEST-JIG.md`. Aurora produces text specifications; KiCad binaries are explicitly out of scope.
- **Iron Law 3 (Complete Delivery)** added to Sage, Ada, River, and Iris for software-only projects. Each agent now writes a project folder containing the working YAML / Python / JSON plus a `README.md` with agent-specific Installation, Troubleshooting, and Recovery sections. Ada additionally produces a HACS-ready repo layout (`hacs.json`, `LICENSE`, `.github/workflows/validate.yaml`) when requested.

**Four new deliverable format specs in `aurora/references/deliverables/`:**

- `bom-format.md` — required columns (Component, Qty, Source, Unit price USD, Notes), production-tier additions (LCSC part number, Package), and a mandatory dated total footer. Price-free BOMs are not deliverable.
- `wiring-format.md` — required parts (connection table, ASCII diagram, power budget paragraph, safety notes). Diagram is required even when the connection table exists.
- `manual-format.md` — README structure with required H2 sections plus agent-specific Installation variants for all five specialists (Volt, Sage, Ada, River, Iris).
- `pcb-format.md` — manufacturing tier table, schematic text format with reference designators and net lists, PCB layout notes, production-tier files (MANUFACTURING / COST-ANALYSIS / CERTIFICATION / TEST-JIG), and an explicit disclaimer that KiCad files are not generated.

**Attribution rule covers every generated file, not just YAML/Python/flow JSON:**

- All four skill SKILL.md Code Attribution sections expanded to cover every file type the skill produces (YAML, Python, JSON, Markdown, shell). The marker form is `aurora@aurora-smart-home (<sub-skill> skill)` plus the repo URL in the format appropriate to the file.
- Sub-skill markers updated to current names: `(home-assistant skill)` replaces legacy `(ha-yaml skill)`; `(ha-integration-dev skill)` replaces legacy `(ha-integration skill)`. Hardcoded `v1.1.0` removed from the rule template.

### Changed

**README rewritten for clarity and accuracy:**

- 651 lines reduced to roughly 312 lines (about 52% shorter).
- New "What gets delivered" section showing the per-agent project folder structure and which sections the project README carries.
- New glossary collapsible (plugin / command / skill / agent / validator / snapshot) for first-time Claude Code users.
- New "What Aurora refuses to do" framing in surrounding messaging plus a vasser "Who this is for" rewrite with three concrete personas.
- Validator count corrected from "15 validators" to 12 validators plus three supporting specs (`_tiered-errors`, `retroactive-yaml-review`, `board-selector`).
- Skill table now includes `api-catalog` and `ha-dashboard-design`, both previously omitted despite shipping in the marketplace.
- All em-dashes removed per the no-em-dash docs preference.

**README anchor and line-break fixes:**

- Restored `## Meet the Aurora team` H2 so the roster-section test can locate the block.
- Collapsed line breaks that split "1 orchestrator + 20 named specialists" and the Nabu Casa funding sentence across lines.
- Voice-tagline regex now accepts em-dash or pipe as the agent-entry separator so the roster respects the no-em-dash preference without breaking the contract.

### Testing infrastructure

- New `test_volt_iron_law_8.py` with 12 contract tests for Volt's Iron Law 8 (project folder, manufacturing tier, required files per tier, required README sections, BOM price + date stamp, disk check, attribution, deliverable-spec references).
- New `test_deliverable_specs.py` covering the four format specs (existence, BOM price column and dated total, manual installation variants per agent, wiring required parts, PCB tier enumeration, KiCad disclaimer).
- New `test_complete_delivery_propagation.py` with parametrised contract tests for Sage / Ada / River / Iris plus agent-specific spot checks (HACS path, manifest.json, flow JSON, dashboard YAML).
- `test_volt_iron_laws.py` extended to cover Iron Laws 1–8 (was 1–6).
- `test_readme_agent_roster.py` voice-tagline regex updated to accept em-dash or pipe.
- 606 tests pass.

## [1.6.7] - 2026-05-14

### Added

**CI / CD pipeline runs pytest (Plan 8):**
- New `pytest-suite` job in `.github/workflows/validate.yaml` runs the full 539-test pytest suite on every push to `main` and on every pull request to `main`. Python 3.13 pinned, dependencies installed from `requirements-dev.txt`, pip caches between runs, per-run summary reported in the GitHub Actions UI. Schema regressions, validator contract drift, soul Iron Law removals, and reference-data corruption now fail the build before merge instead of after.
- Workflow path triggers extended to include `aurora/**`, `.claude-plugin/**`, and `requirements-dev.txt` so changes to schemas, profiles, souls, validators, or test dependencies actually trigger CI. The existing YAML lint, Markdown lint, structure check, and ESPHome config validation jobs are unchanged.

**Schema-versioning operational doc (Plan 8):**
- `aurora/references/schemas/SCHEMA-VERSIONING.md` spells out when to bump major / minor / patch on profile `schema_version` fields, what counts as a backwards-incompatible change, the in-PR workflow for landing schema changes (decide bump size, edit schema, re-run pytest, update profiles in the same PR for major bumps, add CHANGELOG entry), and what schema versioning explicitly does NOT cover. Calls out per-version `$id` URLs and migration tooling as future work rather than pretending they are solved.

### Testing infrastructure

- 14 new pytest tests covering the CI workflow's pytest job (pytest invoked, `aurora/tests` target, Python version pinned, pip caching configured, install from `requirements-dev.txt`), the schema-versioning doc (file exists, bump rules enumerated, backwards-compat addressed, pytest gate named), and contribution-flow docs (top-level `CONTRIBUTING.md`, PR template, bug report and feature request issue templates, requirements-dev.txt pins pytest + jsonschema).
- 539 tests total (plus 5 intentionally-skipped tests).

### Plan 8 closes the session

Plans 5 (cross-agent hand-off + per-agent validators), 6 (community-component infrastructure), 7 (tiered errors + retroactive YAML review), and 8 (CI/CD + schema versioning) have all shipped between 1.6.0 and 1.6.7. Recommended freeze after this release. The aurora plugin grew from a generation-only skill into a validation-first orchestrator with 11 markdown validator specs, 8 DEEP-mode specialist souls each carrying both Iron Laws, full hand-off protocol, community-component infrastructure with explicit unknown-component handling, tiered error output, retroactive YAML review, and CI-enforced contract tests.

## [1.6.6] - 2026-05-14

### Added

**Retroactive YAML review protocol (Plan 7):**
- `aurora/references/validators/retroactive-yaml-review.md` — protocol agents follow when the user pastes existing YAML and asks for review (rather than generation). Four phases: extract facts from the source YAML (board, GPIO, components, I2C addresses, secrets) with line numbers per fact; run the validator suite (pin, conflict, i2c-address, voltage-level, ota-safety, version, entity-id producer, secrets for Volt; entity-id consumer + version + secrets for Sage); anchor every finding back to the user's line numbers; emit tiered output where the Fix line references the specific source lines. Clean passes list which validators ran. Auto-fixing the user's YAML is deliberately out of scope.
- Volt's Iron Law 6 now invokes the retroactive protocol whenever the user pastes ESPHome YAML for review.

### Changed

**"Generated by" attribution rule refreshed across all skill SKILL.md files:**
- `esphome/SKILL.md`, `home-assistant/SKILL.md`, `node-red/SKILL.md`, `ha-integration-dev/SKILL.md` previously instructed agents to emit pre-v1.3 plugin names (`esphome@aurora-smart-home v1.5.1`, `ha-yaml@aurora-smart-home v1.1.0`, etc.) in "Generated by" comments and `generated_with` fields. Those plugin names no longer exist after the v1.3 unification.
- The rule template now reads `aurora@aurora-smart-home (<sub-skill> skill)` with no hardcoded version (versions drifted every release and stale comments accumulated in users' files). The sub-skill marker survives so users still see which module produced the file.

### Testing infrastructure

- 18 new pytest tests covering the retroactive review protocol (required phases, line-number anchoring, full validator suite enumeration, Sage's consumer-mode invocation, no-autofix rule, pass-message format, tiered-format reference, Volt's soul references the protocol) and the attribution-rule freshness (no legacy plugin names in "Generated by" rules across all four skill SKILL.md files; positive assertion that the current `aurora@aurora-smart-home` name IS used; no hardcoded versions inside rule templates). 525 tests total (plus 5 intentionally-skipped tests).

## [1.6.5] - 2026-05-14

### Added

**Community component infrastructure (Plan 6):**
- `aurora/references/schemas/external-component.schema.json` — JSON Schema Draft 2020-12 for community ESPHome `external_components` modules. Required fields: `external_component_id`, `source`, `esphome` (with `min_version` and `supported_chips` enum), `lifecycle` (active / experimental / deprecated / abandoned / merged_to_core), `last_verified`. Optional: `maintainer`, `warnings`, `verified_by`, `documentation_url`, `datasheet_url`. `additionalProperties: false` at the top level so unknown fields fail validation.
- `aurora/references/schemas/hacs-integration.schema.json` — JSON Schema for HACS-distributed Home Assistant integrations. Required fields: `hacs_integration_id`, `source`, `homeassistant` (with `min_version` and `domains`), `category` (enumerated), `lifecycle`, `last_verified`. Carries `requires_credentials` and `cloud_calls` flags that the secrets-validator and llm-config-validator paths can consume when an integration is later added to the catalog.
- `aurora/references/validators/unknown-component-validator.md` — protocol agents follow when the user names a community component for which no profile exists. Asks three concrete questions (source URL, version requirements, docs link), records the answer in the project snapshot's `notes[]` with author/timestamp/source, and emits a mandatory caution block in the output. If the user cannot answer a required question, the agent refuses rather than fabricates plausible-but-wrong configuration.
- `aurora/references/external_components/CONTRIBUTING.md` and `aurora/references/hacs_integrations/CONTRIBUTING.md` — verification floor for adding catalog entries: contributor must have personally installed the component, maintainer activity within 6 months, `verified_by` required for non-experimental status, `last_verified` within 30 days of submission. The catalogs ship empty by design — adding seed entries risks readers treating them as a curated "endorsed" list, which is exactly the failure mode this design avoids.

### Documentation

- README hero, "Already Installed? Update to v1.6.5", "What's New in v1.6.5" section explain Plan 6 with the "no catalog entries" framing visible up front. Validated-today marker bumped.

### Testing infrastructure

- 18 new pytest tests covering schema validity, required-field coverage, top-level `additionalProperties: false`, lifecycle-status enum consistency between the two schemas, supported-chips enum completeness, category enum coverage, CONTRIBUTING docs presence, both catalogs shipping empty, and the unknown-component protocol's contract (three questions, refusal on missing answers, snapshot recording, caution block, tiered-format reference).
- 507 tests total (plus 5 intentionally-skipped tests where the planned-validator-acknowledgement check is not applicable).

## [1.6.4] - 2026-05-14

### Added

**Two more validators (Plan 5 Phase 3, completing the Mira / River cut):**
- `aurora/references/validators/llm-config-validator.md` — Mira validator that enumerates the known LLM providers, flags provider-key casing errors, malformed local endpoint URLs, missing `api_key` on cloud providers, prompt-template token budget warnings, streaming-flag mismatches, `expose:` lists referencing entities not in `snapshot.entity_ids_generated`, intent-script-action mismatches with the expose list, and privacy warnings when cloud LLMs receive sensitive entity state.
- `aurora/references/validators/node-red-syntax-validator.md` — River validator that catches the legacy node type names (`ha-state-changed` → `trigger-state`, `ha-call-service` → `api-call-service`, etc.) that silently fail to deploy in node-red-contrib-home-assistant-websocket 4.x, plus missing `server` references, missing `domain` / `service` on `api-call-service`, entity ID format errors on `trigger-state`, function nodes that import sync HTTP libraries (warning), and function nodes that contain literal credentials.

**Iron Law 2 propagation completed (Plan 5 Phase 4 — Mira + River):**
- **Mira** gains Iron Law 2: invokes `llm-config-validator`, `entity-id-validator` in consumer mode for `expose:` lists and intent script `action:` blocks, `secrets-validator` for cloud LLM API keys in YAML, and `async-correctness-validator` for custom `llm_api` Python integrations.
- **River** gains Iron Law 2: invokes `node-red-syntax-validator` and `entity-id-validator` in consumer mode for every entity referenced in `trigger-state`, `api-current-state`, or `api-call-service` `target.entity_id`.
- Every DEEP-mode specialist (Volt, Ada, Sage, Iris, Vera, Atlas, Mira, River) now carries both Iron Laws: snapshot-aware coordination and validate-before-generating. No DEEP-mode soul stays at Law 1 only.

### Testing infrastructure

- New tests for the two new validators (per the test_phase3_validators_docs parametrized suite).
- The Iron Law 2 propagation test moves Mira and River out of the parked-souls list. `PARKED_SOULS` is now empty.
- The tiered-errors validator-count minimum bumps from 9 to 11 so silent removal of a validator fails the test.
- 482 tests total (plus 5 intentionally-skipped tests where planned-validator acknowledgement is not applicable).

## [1.6.3] - 2026-05-13

### Added

**Tiered error output (Plan 7 §3.13):**
- `aurora/references/validators/_tiered-errors.md` — shared output format spec used by every validator. Defines the four labelled tiers: `❌ Problem` (short, one line), `📚 Explanation` (medium, why it's wrong), `🔧 Fix` (concrete action with file/line where applicable), `💡 Deeper` (optional educational context). Warnings use the same shape with `⚠️ Warning` instead of `❌ Problem`. Tiers 1 and 3 are mandatory; tier 2 fills in over time; tier 4 is optional.
- Every validator's Output section now references the spec so the format is consistent across the suite. Affected: `pin-validator`, `conflict-validator`, `entity-id-validator`, `secrets-validator`, `ota-safety-validator`, `i2c-address-validator`, `voltage-level-validator`, `version-validator`, `async-correctness-validator`.

### Testing infrastructure

- 24 new pytest tests covering the shared format spec (mandatory tiers, emoji prefixes, complete example) and asserting every validator references `_tiered-errors.md` inside its Output section. 451 tests total (plus 2 intentionally-skipped negative tests for Mira / River).

### Documentation

- README hero line and a new "What's New in v1.6.3" section show a complete four-tier example so first-time readers see the contract before encountering it in agent output.

## [1.6.2] - 2026-05-13

### Added

**Five more validators (Plan 5 Phase 3 D+):**
- `aurora/references/validators/ota-safety-validator.md` — Volt validator that enforces the board profile's `min_required_features_for_unbricking`. Disabling WiFi or removing the `ota:` block on a board without USB CDC recovery is a failure. AP fallback recommendations and strapping-pin factory-reset warnings round it out.
- `aurora/references/validators/i2c-address-validator.md` — Volt validator that verifies no two devices on the same I2C bus share an address. Calls out the I2C-reserved 7-bit ranges (`0x00-0x07`, `0x78-0x7F`), supports multiplexer (TCA9548A) channel isolation, GPIO expander address collisions, and speed-mismatch warnings.
- `aurora/references/validators/voltage-level-validator.md` — Volt validator that verifies supply voltages stay inside each component profile's range. Flags 5V sensors on 3.3V-only boards and recommends BSS138 (I2C) or TXS0108E (general-purpose) level shifters, with concrete profile references.
- `aurora/references/validators/version-validator.md` — Volt + Sage validator that cross-checks every referenced feature, component, and integration against `aurora/references/platform-versions.md` and the user's running ESPHome / Home Assistant version. Date-style semver comparison spelled out explicitly. Handles deprecation warnings and experimental-feature flags.
- `aurora/references/validators/async-correctness-validator.md` — Ada + Mira validator that catches the high-frequency HA async bugs LLM-generated integrations commonly ship: `datetime.now()` instead of `dt_util.now()`, `requests.get/post/...` instead of `aiohttp`, `time.sleep` in coroutines, `subprocess.run`, sync `open(` inside async functions. Tight, enumerated pattern list with documented exemptions (imports, comments, docstrings, string literals).

**Iron Law 2 propagation to three more specialists (Plan 5 Phase 4):**
- **Ada** gains full Iron Law 2 (`Validate Before Generating`): invokes `async-correctness-validator` on every Python file and `entity-id-validator` in producer mode for every entity the integration creates. Notes `python-secrets-validator` as planned-but-not-shipped and steers credentials to `config_entry` / environment variables until it lands.
- **Iris** gains thin Iron Law 2: invokes `entity-id-validator` in consumer mode for every card reference. Iris is read-only of `entity_ids_generated`; missing references become `conflict_log` entries asking Volt / Ada / Sage to add the entity, not invented `sensor.fake_thing` references.
- **Atlas** gains thin Iron Law 2: invokes `secrets-validator` on every YAML snippet that wires an external API or community integration, including snippets included with recommendations.
- Mira and River intentionally stay at Iron Law 1 (snapshot-aware coordination) until their domain validators (`llm-config-validator`, `node-red-syntax-validator`) ship.

**Volt's Iron Law 6 expanded:**
- From 2 named validators (pin, conflict) at the start of v1.6.0 to 8 named validators at v1.6.2: pin, conflict, i2c-address, voltage-level, ota-safety, version, entity-id (producer mode), secrets. Restructured as a bulleted suite for readability. The graceful fallback for missing reference data is unchanged.

### Documentation

- README hero line mentions v1.6.2's headline changes (five new validators + Iron Law 2 propagation).
- README notes Aurora has **no runtime dependencies** — the plugin is markdown + JSON, consumed by Claude reading files directly. Python + pytest are only needed if a developer wants to run the test suite locally.

### Testing infrastructure

- 59 new pytest tests (427 total, plus 2 intentionally-skipped negative tests for Mira / River): 36 covering the five new validator docs, 23 covering Iron Law 2 propagation across Ada / Iris / Atlas (plus negative tests asserting Mira and River do NOT yet have Iron Law 2).

## [1.6.1] - 2026-05-13

### Added

**Cross-agent hand-off protocol (DEEP mode):**
- JSON Schema for project snapshots (`aurora/references/schemas/project-snapshot.schema.json`) with format-checked UUIDs, ISO 8601 timestamps, and Home Assistant `entity_id` patterns
- Hand-off protocol documentation (`aurora/references/handoff/_protocol.md`) defining storage location, lifecycle, per-field ownership table, and conflict handling
- Runnable example multi-agent snapshot (`aurora/references/handoff/examples/living-room-sensor.json`) covering Volt → Sage → Iris workflow
- Orchestrator wiring in `aurora/SKILL.md` (Step 7: DEEP Mode Hand-Off) — when to create the snapshot, what initial fields to write, how to update between specialists, per-field ownership reminder, conflict handling, QUICK mode exemption
- `aurora/references/handoff/` registered in the Reference Data section so specialists discover the protocol
- Snapshot-Aware Coordination Iron Law added to every DEEP-mode specialist soul (Volt, Ada, Sage, Iris, Vera, Atlas, Mira, River). Each law is tailored to the agent's per-field ownership: writers list the fields they own, read-only agents (Iris, Vera) state the prohibition explicitly. All agents share the QUICK-mode exemption and the `conflict_log` escape hatch instead of overwriting peer fields.

**First cross-agent validators (Plan 5 Phase 3 — C1 + C2 + C3):**
- `aurora/references/validators/entity-id-validator.md` — markdown spec for the entity-id validator, covering producer mode (Volt/Ada/Sage creating new IDs) and consumer mode (Sage/Iris/Mira/River referencing existing IDs). Hooks into the snapshot's `entity_ids_generated` field, which makes the Phase 1 hand-off protocol load-bearing for the first time.
- `aurora/references/validators/secrets-validator.md` — markdown spec for credential scanning in YAML output. Tightly scoped: enumerates a fixed list of high-risk keys (`password`, `api_key`, `token`, `secret`, `client_secret`, `private_key`, `ota_password`, `wifi_password`, etc.) and requires their values to be `!secret <name>` references. Intentionally excludes generic entropy/base64 scanning (false-positive tarpit), inline comments, and inspects block scalars / templated values only via warnings. Suggests concrete secret names in failure messages.
- Volt's Iron Law 6 now references entity-id-validator and secrets-validator alongside pin-validator and conflict-validator. When generating sensor entity IDs, Volt runs the entity-id-validator in producer mode (format, uniqueness, ownership); before delivering YAML, Volt runs the secrets-validator on the full file and blocks delivery on literal credentials.
- Sage gains its own validation Iron Law (Iron Law 2 — Validate Before Generating) in addition to the snapshot-aware Law 1 from Phase 2B. Sage now invokes entity-id-validator in consumer mode for every referenced ID (with QUICK-mode warning fallback) and in producer mode for helper entities it creates, plus secrets-validator on every generated YAML file. Failures block delivery. yaml-syntax and version validators are spec'd in §3.14 but not yet shipped; Sage's law explicitly notes them as planned.

**Documentation:**
- README agent roster — Aurora reframed as a small smart home agency: 1 orchestrator + 20 named specialists across 7 departments (Hardware, Home Assistant, Field intelligence, Quality desk, Research library, Operations, Design studio). Each entry has an emoji, a domain, and a voice tagline drawn from its soul file. Replaces the previous one-line domain summary.

**Testing infrastructure:**
- 130 new pytest tests covering snapshot schema validity, example correctness, SKILL.md wiring (Step 7 contract), per-soul snapshot awareness, README agent roster integrity, entity-id-validator doc structure, secrets-validator doc structure, and Sage's Iron Law 2 contract (368 total)

### Changed / Fixed

- Update instructions across README, SKILL.md, MANUAL, and all INSTALLATION docs now show the two methods that actually work: `/reload-plugins` (inside Claude Code, refreshes all installed plugins) and `claude plugin update aurora@aurora-smart-home` (CLI). The previously documented `/plugin update <name>` slash command does not accept arguments in Claude Code and silently did nothing.
- Stale references to pre-v1.3 plugin names (`ha-yaml`, `ha-integration`, `esphome`, `node-red`, `supercharge-*`) collapsed to the single `aurora@aurora-smart-home` plugin across README, MANUAL, skill READMEs, and all INSTALLATION docs.
- Removed redundant freshness note from README update section; the banner and SKILL.md freshness check already cover that information.

## [1.6.0] - 2026-05-13

### Added

**Schemas and validators:**
- JSON Schema for board profile, component profile, GPIO expander, and voltage shifter (`aurora/references/schemas/`)
- Pin validator and conflict validator (`aurora/references/validators/`)
- Board selector validator for picking the right board per project requirements
- Volt Iron Law 6: validate before generating (with graceful fallback when reference data is missing)

**Board profiles (17 boards):**
- **ESP dev boards (7)**: ESP32-S3 DevKit C-1, ESP32 DevKit V1, ESP32-S2 Mini, ESP32-C3 Super Mini, ESP32-C6 DevKit, ESP32-H2 DevKit, Wemos D1 Mini (ESP8266, marked legacy with C3 Mini as successor)
- **Smart home boards (4)**: Shelly Plus 1, Shelly Plus 2PM, Sonoff Basic R3 (legacy), Sonoff Mini R3
- **Maker boards (4)**: LilyGo T-Display S3, M5Stack Atom Lite, M5Stack Core Basic, Heltec WiFi LoRa 32 V3
- **Raspberry Pi Pico (2)**: Pico W (RP2040 + WiFi), Pico 2 W (RP2350 + WiFi, marked experimental)
- Each profile carries: GPIO layout, capability matrix, OTA safety, lifecycle status, `recommended_for` / `not_recommended_for` use cases
- `experimental` added to `lifecycle.status` enum

**Project templates (7 ready-to-use scaffolds):**
- Bluetooth proxy, Voice assistant (ESP32-S3 + INMP441 mic + MAX98357A amp)
- Air quality monitor (SCD40), Presence sensor (LD2410 radar)
- Battery-powered soil moisture sensor, Multi-relay controller (PCF8574 + 8 relays)
- Temperature/humidity room monitor (BME280)
- Each template has YAML scaffold + customization guide with recommended board and external hardware list

**Component profiles (10 sensors):**
- Temperature: BME280, BMP280 (with mutual disambiguation), DHT22, DS18B20, NTC thermistor 10K
- Air quality: MH-Z19B, SCD40
- Motion: PIR AM312, LD2410 radar
- Moisture: capacitive soil v1.2

**GPIO expanders (4 chips):**
- PCF8574 (8-bit I2C IO), MCP23017 (16-bit I2C IO), PCA9685 (16-channel PWM), TCA9548A (I2C multiplexer)

**Voltage level shifters (2 chips):**
- TXS0108E (8-channel bidirectional), BSS138 (MOSFET-based, recommended for I2C)

**Testing infrastructure:**
- pytest test suite covering schemas, data integrity, and Volt workflow simulation (238 tests at 1.6.0 release)
- Schema validation in CI, negative tests, URI format enforcement

**Documentation and disclaimers:**
- DISCLAIMER.md with no-warranty, hardware safety, AI-content, and no-liability clauses
- ROADMAP.md with phased development plan
- README hero disclaimer block
- README validation flow diagram and hardware coverage tables

---

## [1.5.1] - 2026-05-11

### Added

#### Home Assistant: 2026.5 Coverage

- `references/integrations-esphome.md` - Radio Frequency (RF) Integration section: Broadlink RM4 Pro flow plus ESPHome CC1101 adoption flow, sub-GHz protocols (rc_switch, somfy, came, nice_flor_s), learning unknown codes
- `references/integrations-esphome.md` - Serial Port Proxy Integration section: auto-discovery flow for ESPHome `serial_proxy`, use cases (Modbus RS485, DLMS, Denon RS232), security considerations
- `references/dashboard-cards.md` - HA 2026.5 Card Features section: Media Player Tile features, Battery Maintenance Dashboard, Vacuum and Lawn Mower more-info redesign, dashboard background colors and card favorites, code editor autocomplete
- HA SKILL.md - What's new in HA 2026.5 section listing 12 new integrations plus core feature changes
- HA README.md - Target Version updated to 2024.x through 2026.5

#### ESPHome: HA 2026.5 Cross-references

- `references/remote-rf-ir.md` - CC1101 section now notes compatibility with HA 2026.5 Radio Frequency integration
- `references/communication.md` - Serial Proxy section now notes compatibility with HA 2026.5 Serial Port Proxy integration plus security guidance
- ESPHome SKILL.md - 2026.4.5 patch note (5 bugfixes: ha-addon toggle, secrets bundle, substitutions sibling refs, WiFi safe mode, Nextion text sensor) and HA 2026.5 cross-platform compatibility section
- ESPHome README.md - v1.3.1 entry covering the cross-references and patch note

### Changed

- Plugin version: 1.5.0 → 1.5.1
- ESPHome skill: v1.3.0 → v1.3.1 (cross-references only; no firmware-side changes)

### Notes

- ESPHome 2026.4.5 is the latest stable ESPHome release as of 2026-05-11. It is a bugfix-only patch with no new components or breaking changes.
- HA 2026.5's RF and Serial Port Proxy integrations consume already-stable ESPHome components (`cc1101` and `serial_proxy`), so no firmware upgrade is required.
- ESPHome 2026.5.0 stable release is expected the first Wednesday of June 2026. Any new components introduced there will be covered in a follow-up release.

---

## [1.2.0] - 2026-03-26

### Added

#### ESPHome: New Component Coverage (ESPHome 2025.2 - 2026.3)

**New Reference Files (3):**
- `references/alarm-security.md` - Alarm Control Panel (template platform, zones, bypass, code support), Lock (template, output), Valve (template, position control)
- `references/media-audio.md` - Redesigned media player architecture (2026.3): Speaker Media Player, Speaker Source, I2S Audio, Mixer/Resampler speakers, Microphone (I2S, UDP), Audio DAC (ES8311, ES8388), Audio File embedding, migration guide from legacy I2S Media Player
- `references/input-entities.md` - Datetime (date/time/datetime types), Event entity platform with on_event trigger

**New Templates (3):**
- `assets/templates/alarm-panel.yaml` - Template alarm control panel with PIR + door sensors, zone bypass, arming buzzer
- `assets/templates/media-player.yaml` - Speaker Media Player with ESP32-S3, MAX98357A DAC, INMP441 mic, rotary encoder volume
- `assets/templates/irrigation-controller.yaml` - 4-zone valve-based irrigation with pump safety, soil moisture sensor, scheduling

### Changed

**ESPHome: Updated Reference Files (7):**
- `references/boards.md` - RP2040/RP2350 first-class support (pico-sdk 2.0, 143+ boards, WiFi, BLE, OTA), nRF52 BLE+serial OTA via mcumgr
- `references/displays.md` - MIPI DSI Display Driver for ESP32-P4 high-performance displays
- `references/communication.md` - Z-Wave Proxy (network serial proxy), Serial Proxy (generic), DLMS Smart Meter (European smart meters)
- `references/sensors.md` - Dew Point (native computed sensor), HDC302x, SEN6x all-in-one environmental sensor
- `references/covers-fans.md` - Cover movement state triggers (on_open_started, on_close_completed, etc.)
- `references/home-assistant.md` - API action responses (bidirectional), conditional package inclusion
- `references/matter-bridge.md` - Zigbee platform expansion for ESP32-C6/H2

**ESPHome SKILL.md:**
- Version bump to v1.2.0
- Updated skill description with new component keywords
- Breaking changes section expanded to cover ESPHome 2025.2 - 2026.3
- Reference table updated with 3 new entries

---

## [1.5.0] - 2026-05-02

### Added

#### ESPHome: 2026.4.0 Updates

**Breaking Changes section (ESPHome 2026.4+):**
- ESP32 max CPU frequency as default — 33% faster API, no config changes required
- 40KB extra IRAM unlocked for ESP32
- Signed OTA verification (`ota: verify_signature: true`)
- Custom partition tables support in `esp32:` block
- GPIO Expander `interrupt_pin` — eliminates I2C/SPI polling entirely
- W5500/W5100/W5100S SPI Ethernet — five new chip types incl. RP2040 (WIZnet EVB-Pico)
- Client-side state logging — up to 46x faster sensor publishing, auto-enabled
- ESP8266 crash handler — now matches ESP32/RP2040

**New Components table:**
- `W5500/W5100 SPI Ethernet` — wired networking for ESP32/RP2040 without WiFi

**ESPHome SKILL.md:**
- Version bump to v1.3.0
- Breaking Changes heading updated to cover 2025.2 - 2026.4

**Aurora SKILL.md:**
- Version bump to v1.5.0
- Platform version updated to ESPHome 2026.4
- What's New highlight added after banner with ESPHome 2026.4 key features

---

## [1.4.0] - 2026-04-12

### Added

#### Aurora: Hardware Documentation Layer (IoT/ESPHome)

Closes the gap between firmware generation and physical hardware — Aurora now
delivers all three layers for IoT projects: hardware/dimensioning, installation,
and software.

**New agents (2):**
- `aurora/souls/watt.md` — **Watt**: Power budget specialist. Calculates full
  current draw table (µA/mA per state × time), battery runtime in days, and solar
  panel sizing with seasonal correction. Triggered automatically for any project
  using `deep_sleep`, battery, solar, or power bank. Model: haiku.
- `aurora/souls/manual.md` — **Manual**: Installation documentation specialist.
  Generates `INSTALL.md` and `TROUBLESHOOTING.md` with actual entity IDs and file
  names from the project — never generic placeholders. Model: haiku.

**New Iron Laws:**
- Volt: Generate wiring diagram for every GPIO — no GPIO without a diagram
- Volt: Generate calibration procedure (with actual entity IDs) for sensors that require it
- Volt: Flag Watt before finalising any BOM with battery, solar, or deep sleep
- Vera: Hardware Safety Review mandatory BEFORE Volt for battery/actuator/outdoor/>5V
- Watt: No battery/solar recommendation without a full power budget table
- Manual: Reference actual entity IDs and file names — never generic placeholders

**Updated agents:**
- `aurora/souls/volt.md` — 5 Iron Laws added (board-first, wiring diagram,
  calibration, power budget, troubleshooting)
- `aurora/souls/vera.md` — Hardware Safety Review (Mode 1) added: reviews battery
  protection, high-current safety, mixed voltages, ADC limits, outdoor IP rating,
  and mains isolation; blocks Volt if critical risks found

**ESPHome SKILL.md:**
- Updated process flow: Safety check → Power budget → YAML → Wiring diagram →
  Calibration → Troubleshooting → Checklist
- New **Wiring Diagrams** section with ASCII format and required additions table
  (flyback diodes, voltage dividers, pull-ups, common GND strategy)
- New **Calibration Register**: 7 sensor types with procedure template and
  entity ID references (capacitive moisture, NTC, CO₂, water level, pressure,
  LDR, CT clamp)
- Extended Pre-Completion Checklist with wiring, calibration, power, and
  troubleshooting categories

**Aurora SKILL.md:**
- Registry updated: 19 → 21 agents
- Watt added to Smart Home Hardware table
- Manual added to Development Support table
- 7 new Iron Laws in Iron Laws Reference section

**workflows.md:**
- New **Battery/Outdoor IoT Project** workflow:
  Vera (Safety) → Watt → Volt → Sage → Manual → Vera (WAF)
- Note added to New Sensor Device workflow for battery/actuator/outdoor projects

---

## [1.3.0] - 2026-04-09

### Added

#### Structural Improvements (All Skills)
- **Overview section** with announcement pattern in all SKILL.md files
- **Iron Law** - Non-negotiable rules for each skill domain
- **Red Flags tables** - Rationalization prevention patterns
- **Graphviz workflow diagrams** - Visual process flows
- **Pre-Completion Checklists** - Validation before declaring complete
- **Integration sections** - Cross-skill relationship documentation

#### New Reference Files

**ESPHome** (3 new):
- `references/ble-proxy.md` - BLE Proxy setup, Xiaomi sensors, presence detection
- `references/voice-local.md` - Local voice assistant with Micro Wake Word
- `references/matter-bridge.md` - Matter/Thread configuration for ESP32-C6

**HA Integration Dev** (2 new):
- `references/conversation-agent.md` - ConversationEntity, LLM agents, custom intents
- `references/multi-coordinator.md` - Multiple DataUpdateCoordinator patterns

**Home Assistant Automation** (4 new):
- `references/assist-patterns.md` - Custom sentences for Assist voice control
- `references/presence-detection.md` - PIR, mmWave, Bayesian presence
- `references/notification-patterns.md` - Actionable notifications, rate limiting
- `references/calendar-automation.md` - Calendar triggers, vacation mode, schedules

#### New Templates

**ESPHome** (3 new):
- `assets/templates/ble-proxy.yaml` - Production-ready BLE Proxy
- `assets/templates/voice-assistant.yaml` - Enhanced voice satellite with LED status
- `assets/templates/matter-light.yaml` - Matter-compatible light for ESP32-C6

**HA Integration Dev** (2 new template folders):
- `templates/bluetooth-integration/` - Complete BLE device integration (7 files)
  - Bluetooth discovery, passive/active scanning
  - Config flow with device picker
  - Coordinator with advertisement parsing
  - EntityDescription-based sensors
- `templates/conversation-agent/` - LLM-powered voice assistant (8 files)
  - Multi-provider support (Ollama, OpenAI, Anthropic)
  - Conversation history management
  - Home Assistant context injection
  - Action execution via JSON parsing

#### Documentation

- `SKILL-INTEGRATION.md` - Cross-skill integration guide with workflows
- `examples/complete-smart-room/` - Complete example project (6 files)
  - ESP32-S3 multi-sensor (mmWave, temp, humidity, light, LED strip)
  - ESP32-S3 voice satellite
  - HA automations (presence lighting, climate, modes)
  - Scenes (work, relax, movie, night)
  - Input helpers
- Updated `README.md` with "Getting Started" guide

### Changed

- Updated Quick Reference tables in all SKILL.md files with new references
- Updated template counts in README (ESPHome: 19, HA Integration: 8)
- Enhanced existing `voice-assistant.yaml` template with better documentation

---

## [1.0.0] - 2025-01-01

### Added

#### ESPHome Skill
- 26 reference guides covering 160+ ESPHome components
- 600+ example prompts for device configurations
- 19 ready-to-use templates
- Support for ESP32, ESP32-S3, ESP32-C3, ESP32-C6, ESP8266
- Device conversion guides (Shelly, Sonoff, Tuya)
- Arduino to ESPHome migration guide

#### Home Assistant Automation Skill
- 49 reference guides covering 50+ integrations
- 300+ example automation prompts
- 17 production-ready templates
- Blueprint creation and usage guides
- Dashboard and Mushroom card documentation
- Jinja2 template patterns

#### Home Assistant Integration Dev Skill
- 17 reference guides for custom integration development
- 129 development prompts
- 8 starter templates (basic, polling, push, OAuth2, hub, service, Bluetooth, conversation)
- DataUpdateCoordinator patterns
- Config flow and options flow guides
- HACS publishing workflow

---

## Version Numbering

- **Major** (X.0.0): Breaking changes, major restructuring
- **Minor** (0.X.0): New features, new references, new templates
- **Patch** (0.0.X): Bug fixes, documentation updates, minor improvements

---

## Contributing

When contributing, please update this changelog with your changes under the `[Unreleased]` section.

Categories:
- **Added** - New features, files, or capabilities
- **Changed** - Updates to existing functionality
- **Deprecated** - Features to be removed in future
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security-related changes
