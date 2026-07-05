# Home Assistant 2026.7 - Release Reference for Aurora (July 2026)

**Release dates:** 2026.7.0 on 2026-07-01, current patch 2026.7.1 on 2026-07-03. This file also carries the 2026.6 breaking change that is still in effect.
**Source:** https://www.home-assistant.io/blog/2026/07/01/release-20267/ and https://www.home-assistant.io/blog/2026/06/03/release-20266/

Read this before generating or reviewing automation YAML for a user on HA 2026.6 or newer. One removal and one default change here invalidate patterns that were valid a few months ago.

---

## Breaking change still in effect (shipped in 2026.6): legacy `platform: template` removed

The single most important thing to check on a 2026.6+ system. Old-style template entities declared under an individual platform key no longer load at all. This covers `alarm_control_panel`, `binary_sensor`, `cover`, `fan`, `light`, `lock`, `sensor`, `switch`, `vacuum`, and `weather`. The syntax was deprecated back in 2025.12; as of 2026.6 the removal is live and those entities silently disappear from the system.

Migrate every one to the modern `template:` integration.

```yaml
# Old (no longer loads on HA 2026.6+)
sensor:
  - platform: template
    sensors:
      hallway_comfort:
        friendly_name: "Hallway comfort"
        value_template: "{{ states('sensor.hallway_temp') | float(0) }}"

# New (template: integration)
template:
  - sensor:
      - name: "Hallway comfort"
        state: "{{ states('sensor.hallway_temp') | float(0) }}"
```

If a user reports "my template sensors vanished after updating," this is almost always the cause. Route the migration to **Sage**; route post-upgrade breakage reports to **Glitch**.

---

## What's new in 2026.7 at a glance

1. **Purpose-specific triggers and conditions are the default.** Graduated from Labs. Automations can describe intent instead of raw entity/state plumbing, and integrations register their own trigger and condition types. Classic YAML keeps working unchanged. This is the headline; details below.
2. **Activity timeline.** The logbook is rebuilt as a day-grouped timeline with colored state dots. No YAML impact.
3. **Update all.** The Updates page groups pending updates into per-source cards with one-tap bulk update. ESPHome devices and HACS are bundled; core and OS stay manual.
4. **Dedicated Infrared and Radio Frequency settings panels** appear when such devices exist.
5. **ZHA Zigbee device management overhaul.** Route Zigbee questions to **Nano**.
6. **Zone reporting change (behavioral breaking).** Position-aware device trackers now report the smallest enclosing zone instead of the nearest zone center. Automations that count or compare zones can shift.
7. **Z-Wave server floor raised (breaking).** Z-Wave JS now requires zwave-js-server 3.9.0+ (Z-Wave JS UI 11.19.1+).
8. **10 new integrations,** including Dropbox, MELCloud Home, and KlikAanKlikUit.

---

## Upgrade checklist (run before or right after updating to 2026.7)

- [ ] Any `platform: template` entities still in config? Migrate to `template:` (see above) or they stop loading.
- [ ] Automations that count zones or key off "nearest zone"? Re-test them. 2026.7 reports the smallest enclosing zone now.
- [ ] Running Z-Wave? Confirm zwave-js-server is 3.9.0+ before updating core, or Z-Wave drops offline.
- [ ] Built automations on the 2026.6 Labs zone triggers? Some Labs-era block keys were renamed for the 2026.7 default. Re-open and re-save them in the editor, or update the key names by hand (see below).

---

## The headline: purpose-specific triggers and conditions

In 2026.7 the intent-based trigger and condition model that was in Labs since 2026.6 becomes the default surface in the automation editor. Instead of wiring a raw state change and then filtering it, you state what you mean, and integrations can contribute their own domain-specific trigger and condition types.

The key compatibility fact: **classic YAML triggers, conditions, and templates keep working exactly as before.** Nothing you already wrote needs to change. There is no forced migration. Purpose-specific blocks are an additional, richer way to express automations, not a replacement for `trigger: state` and friends.

The new blocks use a consistent envelope. A trigger names a `domain.name` type and carries `target:` (what it applies to), `options:` (type-specific parameters), `behavior:` (how it fires), and an optional `for:` duration:

```yaml
triggers:
  - trigger: zone.entered
    target:
      entity_id: person.alex
    options:
      zone: zone.home
    for:
      minutes: 2
```

Conditions follow the same shape with `condition: domain.name`:

```yaml
conditions:
  - condition: zone.is_in
    target:
      entity_id: person.alex
    options:
      zone: zone.home
```

Two cautions when generating this syntax:

- **It is optional.** For most automations, classic `trigger: state` / `trigger: numeric_state` is still the clearest and most portable choice. Reach for purpose-specific blocks when an integration exposes a type that genuinely simplifies the automation (zone occupancy, assist-satellite events, battery thresholds), not by default.
- **Labs key names changed.** Blocks built against the 2026.6 Labs preview may use key names that were renamed when the feature graduated. If an automation authored in the 2026.6 editor throws on 2026.7, re-open and re-save it in the editor to let HA rewrite the keys, or correct them by hand.

Route purpose-specific automation work to **Sage**. When a device or integration is involved (Zigbee, Z-Wave, ESPHome), pair with **Nano** or **Volt** as appropriate.

---

## Zone automations: verify after upgrading

The 2026.7 device-tracker change (smallest enclosing zone rather than nearest center) is subtle but real. If you have overlapping zones (for example a small "front door" zone inside a larger "home" zone), a tracker that used to resolve to `home` may now resolve to `front_door`. Automations that branch on `zone` state or count occupants per zone should be re-tested. This pairs with the 2026.6 zone-based triggers, which replaced the older `entered_home` / `left_home` device-tracker shorthand with explicit enter / leave / occupied / empty semantics.

Route zone-automation breakage to **Glitch**; route the rebuild to **Sage**.

---

## Aurora routing quick reference

| Change | Route to |
|--------|----------|
| `platform: template` migration | **Sage** |
| Purpose-specific triggers/conditions | **Sage** |
| Zone automation shifts / breakage | **Glitch** then **Sage** |
| ZHA Zigbee management | **Nano** |
| Z-Wave server version breakage | **Glitch** |
| Bulk update / Updates page | **Forge** |
| New integrations adoption | **Ada** |
| IR / RF panels (firmware side) | **Volt** |

For the exhaustive per-type trigger, condition, and action tables, repo-local development also has the official-docs snapshots under `home-assistant/references/` (see `SKILL.md`). This release file is self-contained for the changes that matter in 2026.6 and 2026.7.
