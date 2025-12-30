# Publishing

HACS integration and Home Assistant core contribution guidelines.

## HACS (Home Assistant Community Store)

### Requirements

1. **Repository Structure**
```
my-integration/
├── custom_components/
│   └── my_integration/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── const.py
│       └── ...
├── hacs.json
├── README.md
├── LICENSE
└── .github/
    └── workflows/
        └── validate.yaml
```

2. **manifest.json Requirements**
```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "version": "1.0.0",
  "documentation": "https://github.com/user/my-integration",
  "issue_tracker": "https://github.com/user/my-integration/issues",
  "codeowners": ["@username"],
  "config_flow": true,
  "iot_class": "cloud_polling"
}
```

3. **hacs.json**
```json
{
  "name": "My Integration",
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

### hacs.json Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name in HACS |
| `render_readme` | No | Show README in HACS |
| `homeassistant` | No | Minimum HA version |
| `zip_release` | No | Use zip instead of clone |
| `filename` | No | Zip filename pattern |
| `content_in_root` | No | Integration in root (not custom_components) |
| `country` | No | Country codes for filtering |

### GitHub Workflow

```yaml
# .github/workflows/validate.yaml
name: Validate

on:
  push:
  pull_request:
  schedule:
    - cron: "0 0 * * *"

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: HACS Validation
        uses: hacs/action@main
        with:
          category: integration

      - name: Hassfest Validation
        uses: home-assistant/actions/hassfest@master
```

### Submit to HACS

1. Ensure all requirements met
2. Add topics to GitHub repo:
   - `hacs`
   - `home-assistant`
   - `homeassistant`
   - `custom-integration`
3. Go to https://hacs.xyz/docs/publish/include
4. Follow submission process

---

## Versioning

### Semantic Versioning

```
MAJOR.MINOR.PATCH
1.0.0 → 1.0.1 (patch: bug fix)
1.0.1 → 1.1.0 (minor: new feature)
1.1.0 → 2.0.0 (major: breaking change)
```

### Update Version

```json
// manifest.json
{
  "version": "1.2.3"
}
```

### GitHub Releases

1. Tag commit: `git tag v1.2.3`
2. Push tag: `git push origin v1.2.3`
3. Create release on GitHub

---

## Documentation

### README.md Structure

```markdown
# My Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/user/my-integration.svg)](https://github.com/user/my-integration/releases)

Integration description.

## Installation

### HACS (Recommended)
1. Open HACS
2. Search for "My Integration"
3. Install

### Manual
1. Download latest release
2. Copy `custom_components/my_integration` to your `custom_components`
3. Restart Home Assistant

## Configuration

1. Go to Settings → Integrations
2. Click "+ Add Integration"
3. Search for "My Integration"
4. Enter your credentials

## Entities

| Entity | Description |
|--------|-------------|
| `sensor.my_temperature` | Current temperature |
| `switch.my_power` | Power switch |

## Services

### my_integration.refresh
Refresh data from device.

## Troubleshooting

### Cannot Connect
- Check device is online
- Verify IP address

## Support
- [Report Issue](https://github.com/user/my-integration/issues)
- [Discussions](https://github.com/user/my-integration/discussions)
```

---

## Home Assistant Core Contribution

### Requirements

1. **Quality Standards**
   - 100% test coverage
   - Type hints everywhere
   - Follows coding guidelines
   - No blocking I/O

2. **File Structure**
```
homeassistant/components/my_integration/
├── __init__.py
├── manifest.json
├── config_flow.py
├── const.py
├── coordinator.py
├── entity.py
├── sensor.py
├── strings.json
└── translations/
    └── en.json
```

3. **Tests Required**
```
tests/components/my_integration/
├── __init__.py
├── conftest.py
├── test_config_flow.py
├── test_init.py
├── test_sensor.py
└── test_diagnostics.py
```

### Coding Standards

```python
# Type hints required
async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up integration from config entry."""

# Docstrings required
class MySensor(SensorEntity):
    """Sensor entity for My Integration."""

# Constants in const.py
from .const import DOMAIN, CONF_HOST
```

### manifest.json for Core

```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "codeowners": ["@username"],
  "config_flow": true,
  "documentation": "https://www.home-assistant.io/integrations/my_integration",
  "iot_class": "cloud_polling",
  "requirements": ["my-api-lib==1.0.0"],
  "quality_scale": "silver"
}
```

### Quality Scale

| Level | Requirements |
|-------|--------------|
| No score | Basic functionality |
| Bronze | config_flow, unique_id, tests |
| Silver | + diagnostics, reconfigure |
| Gold | + repairs, entity naming |
| Platinum | Full feature compliance |

### Contribution Process

1. **Fork core repository**
```bash
git clone https://github.com/home-assistant/core.git
cd core
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

2. **Create branch**
```bash
git checkout -b add-my-integration
```

3. **Add integration**
```bash
# Add files to homeassistant/components/my_integration/
# Add tests to tests/components/my_integration/
```

4. **Run checks**
```bash
# Run tests
pytest tests/components/my_integration/

# Run linting
pre-commit run --all-files

# Run type checking
mypy homeassistant/components/my_integration/
```

5. **Create PR**
   - Title: `Add My Integration integration`
   - Description: Feature summary
   - Link documentation PR

---

## Code Quality

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
```

### Ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D"]  # Skip docstrings for custom integrations
```

### Type Checking

```bash
# Install stubs
pip install homeassistant-stubs

# Run mypy
mypy custom_components/my_integration/
```

---

## CI/CD

### GitHub Actions for Testing

```yaml
# .github/workflows/tests.yaml
name: Tests

on: [push, pull_request]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install pytest pytest-homeassistant-custom-component
          pip install -r requirements_test.txt

      - name: Run tests
        run: pytest tests/ --cov=custom_components/my_integration

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Release Workflow

```yaml
# .github/workflows/release.yaml
name: Release

on:
  release:
    types: [published]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Update version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" \
            custom_components/my_integration/manifest.json

      - name: Commit version
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add .
          git commit -m "Update version to $VERSION"
          git push
```

---

## Maintenance

### Dependency Updates

```yaml
# .github/dependabot.yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
```

### Issue Templates

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yaml
name: Bug Report
description: Report a bug
body:
  - type: textarea
    id: description
    attributes:
      label: Describe the bug
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: Integration version
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Relevant log output
      render: shell
```

---

## Best Practices

### HACS

- Update version in manifest.json for each release
- Use GitHub releases for version tracking
- Include clear installation instructions
- Respond to issues promptly

### Core Contribution

- Start with an integration proposal issue
- Follow ADR (Architecture Decision Records)
- Include comprehensive tests
- Update documentation simultaneously

---

For testing patterns, see `testing.md`.
For debugging, see `debugging.md`.
