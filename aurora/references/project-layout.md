# Canonical Project Layout

Full directory tree for a project Aurora delivers. See `## Project Structure
Rule` in `aurora/SKILL.md` for the ownership table, README rules, and root
file whitelist — this file is just the tree for reference.

```
<project-name>/
├── README.md                          ← master document, links every part
├── aurora-project.json                ← snapshot (DEEP mode only)
├── esphome/                           ← Volt (firmware + install docs)
│   ├── <device-name>.yaml
│   ├── secrets.yaml.example
│   ├── INSTALL.md
│   └── TROUBLESHOOTING.md
├── hardware/                          ← Volt (PCB + safety artifacts)
│   ├── BOM.md                         ← when split out from README
│   ├── WIRING.md                      ← when split out from README
│   ├── HAZARD-ANALYSIS.md             ← Vera (required for battery/actuator/outdoor/>5V)
│   ├── SCHEMATIC.md                   ← custom-PCB and production tiers
│   ├── PCB-NOTES.md                   ← custom-PCB and production tiers
│   ├── MANUFACTURING.md               ← production tier only
│   ├── COST-ANALYSIS.md               ← production tier only
│   ├── CERTIFICATION.md               ← production tier only
│   └── TEST-JIG.md                    ← production tier only
├── automations/                       ← Sage (automations)
│   └── <automation-name>.yaml
├── scripts/                           ← Sage (scripts)
├── blueprints/                        ← Sage (blueprints)
├── packages/                          ← Sage (packages)
├── dashboards/                        ← Iris
│   └── <dashboard-name>.yaml
├── node-red-flows/                    ← River
│   └── <flow-name>.json
└── custom_components/                 ← Ada (HA standard)
    └── <integration_id>/
        ├── __init__.py
        ├── manifest.json
        └── ...
```
