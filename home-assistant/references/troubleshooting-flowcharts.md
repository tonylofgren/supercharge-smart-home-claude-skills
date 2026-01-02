# Home Assistant Troubleshooting Flowcharts

Visual decision trees for debugging common Home Assistant issues.

## Automation Not Triggering

```dot
digraph automation_debug {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="Automation not\ntriggering", shape=doublecircle];
    check_enabled [label="Automation\nenabled?", shape=diamond];
    check_trace [label="Trace shows\nany activity?", shape=diamond];
    check_trigger [label="Trigger\nconfigured correctly?", shape=diamond];
    check_condition [label="Condition\nevaluating true?", shape=diamond];
    check_entity [label="Trigger entity\nexists?", shape=diamond];
    check_state [label="Entity state\nchanging?", shape=diamond];

    fix_enable [label="Enable automation\nin UI or YAML", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_trigger [label="Review trigger\nconfiguration", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_condition [label="Test condition in\nDeveloper Tools", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_entity [label="Check entity_id\nspelling/existence", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_state [label="Verify device is\nsending updates", shape=box, style="rounded,filled", fillcolor=lightgreen];
    check_actions [label="Check action\nconfiguration", shape=box, style="rounded,filled", fillcolor=lightyellow];

    start -> check_enabled;
    check_enabled -> fix_enable [label="no"];
    check_enabled -> check_trace [label="yes"];
    check_trace -> check_entity [label="no"];
    check_trace -> check_condition [label="yes - stopped at condition"];
    check_trace -> check_actions [label="yes - completed"];
    check_entity -> fix_entity [label="no"];
    check_entity -> check_state [label="yes"];
    check_state -> fix_state [label="not changing"];
    check_state -> check_trigger [label="changing"];
    check_trigger -> fix_trigger [label="wrong"];
    check_condition -> fix_condition [label="false"];
}
```

**Debug Commands:**
```yaml
# Check automation state
{{ states.automation.your_automation.state }}

# Check last triggered
{{ states.automation.your_automation.attributes.last_triggered }}

# Force manual trigger for testing
service: automation.trigger
target:
  entity_id: automation.your_automation
```

---

## Entity Unavailable

```dot
digraph entity_unavailable {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="Entity shows\n'unavailable'", shape=doublecircle];
    check_device [label="Physical device\npowered on?", shape=diamond];
    check_network [label="Device on\nnetwork?", shape=diamond];
    check_integration [label="Integration\nloaded?", shape=diamond];
    check_logs [label="Errors in\nlogs?", shape=diamond];
    check_reload [label="Reload integration\nhelps?", shape=diamond];

    fix_power [label="Power cycle\ndevice", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_network [label="Check WiFi/\nEthernet connection", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_integration [label="Reinstall or\nreconfigure integration", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_logs [label="Address specific\nerror in logs", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_restart [label="Restart Home\nAssistant", shape=box, style="rounded,filled", fillcolor=lightgreen];
    check_bug [label="Check GitHub issues\nor report bug", shape=box, style="rounded,filled", fillcolor=lightyellow];

    start -> check_device;
    check_device -> fix_power [label="no"];
    check_device -> check_network [label="yes"];
    check_network -> fix_network [label="no"];
    check_network -> check_integration [label="yes"];
    check_integration -> fix_integration [label="not loaded"];
    check_integration -> check_logs [label="loaded"];
    check_logs -> fix_logs [label="yes"];
    check_logs -> check_reload [label="no"];
    check_reload -> fix_restart [label="no"];
    check_reload -> check_bug [label="still unavailable"];
}
```

**Useful Checks:**
```yaml
# Check all unavailable entities
{% for state in states if state.state == 'unavailable' %}
  {{ state.entity_id }}
{% endfor %}

# Check entity's last changed
{{ states.sensor.example.last_changed }}
```

---

## Template Error

```dot
digraph template_error {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="Template shows\nerror or 'unknown'", shape=doublecircle];
    check_syntax [label="Valid Jinja2\nsyntax?", shape=diamond];
    check_entity [label="All entities\nexist?", shape=diamond];
    check_attribute [label="Attributes\nexist?", shape=diamond];
    check_type [label="Correct data\ntype?", shape=diamond];
    check_default [label="Default value\nprovided?", shape=diamond];

    fix_syntax [label="Check brackets,\nquotes, filters", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_entity [label="Verify entity_id\nin Developer Tools", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_attribute [label="Use state_attr()\nwith default", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_type [label="Use int(), float(),\nor | default filter", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_default [label="Add | default(0)\nor | default('unknown')", shape=box, style="rounded,filled", fillcolor=lightgreen];

    start -> check_syntax;
    check_syntax -> fix_syntax [label="no"];
    check_syntax -> check_entity [label="yes"];
    check_entity -> fix_entity [label="missing"];
    check_entity -> check_attribute [label="exists"];
    check_attribute -> fix_attribute [label="missing"];
    check_attribute -> check_type [label="exists"];
    check_type -> fix_type [label="wrong type"];
    check_type -> check_default [label="correct"];
    check_default -> fix_default [label="no"];
}
```

**Common Template Fixes:**

```yaml
# BAD - No error handling
{{ states.sensor.temperature.state }}

# GOOD - With error handling
{{ states('sensor.temperature') | default('unknown') }}

# BAD - Attribute without default
{{ state_attr('sensor.example', 'battery') }}

# GOOD - Attribute with default
{{ state_attr('sensor.example', 'battery') | default(0) }}

# BAD - Math without type conversion
{{ states('sensor.value') + 10 }}

# GOOD - With type conversion
{{ states('sensor.value') | float(0) + 10 }}

# BAD - Assuming entity exists
{% if states.sensor.example.state == 'on' %}

# GOOD - Check existence first
{% if states('sensor.example') == 'on' %}
```

---

## Service Call Failing

```dot
digraph service_debug {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="Service call\nfails", shape=doublecircle];
    check_service [label="Service\nexists?", shape=diamond];
    check_target [label="Target entity\nexists?", shape=diamond];
    check_data [label="Required data\nprovided?", shape=diamond];
    check_domain [label="Correct domain\nfor entity?", shape=diamond];
    check_state [label="Entity in valid\nstate for action?", shape=diamond];

    fix_service [label="Check service name\nin Developer Tools", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_target [label="Verify entity_id\nspelling", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_data [label="Add required\nservice data", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_domain [label="Use correct domain\n(e.g., light. vs switch.)", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_state [label="Check if entity is\navailable/on first", shape=box, style="rounded,filled", fillcolor=lightgreen];

    start -> check_service;
    check_service -> fix_service [label="no"];
    check_service -> check_target [label="yes"];
    check_target -> fix_target [label="no"];
    check_target -> check_data [label="yes"];
    check_data -> fix_data [label="missing"];
    check_data -> check_domain [label="complete"];
    check_domain -> fix_domain [label="mismatch"];
    check_domain -> check_state [label="correct"];
    check_state -> fix_state [label="invalid"];
}
```

**Common Service Issues:**

```yaml
# BAD - Wrong domain
service: switch.turn_on
target:
  entity_id: light.living_room  # This is a light, not switch!

# GOOD - Correct domain
service: light.turn_on
target:
  entity_id: light.living_room

# BAD - Missing required data
service: light.turn_on
target:
  entity_id: light.living_room
data:
  brightness: 255  # Missing brightness_pct OR brightness

# GOOD - Use homeassistant.turn_on for mixed domains
service: homeassistant.turn_on
target:
  entity_id:
    - light.living_room
    - switch.fan
```

---

## Script/Automation Hanging

```dot
digraph hanging_debug {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="Script/automation\nhangs or slow", shape=doublecircle];
    check_wait [label="Using wait_\nactions?", shape=diamond];
    check_timeout [label="Timeout\nconfigured?", shape=diamond];
    check_loop [label="Infinite loop\npossible?", shape=diamond];
    check_blocking [label="Blocking service\ncalls?", shape=diamond];
    check_condition [label="Condition never\nbecoming true?", shape=diamond];

    fix_wait [label="Check wait_for_trigger\nconditions", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_timeout [label="Add timeout:\nwith continue_on_timeout", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_loop [label="Add exit condition\nor counter limit", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_parallel [label="Use parallel:\nfor concurrent actions", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_condition [label="Review wait condition\nlogic", shape=box, style="rounded,filled", fillcolor=lightgreen];

    start -> check_wait;
    check_wait -> check_loop [label="no"];
    check_wait -> check_timeout [label="yes"];
    check_timeout -> fix_timeout [label="no"];
    check_timeout -> check_condition [label="yes"];
    check_condition -> fix_condition [label="yes"];
    check_loop -> fix_loop [label="yes"];
    check_loop -> check_blocking [label="no"];
    check_blocking -> fix_parallel [label="yes"];
}
```

**Timeout Pattern:**

```yaml
# Wait with timeout
- wait_for_trigger:
    - platform: state
      entity_id: binary_sensor.door
      to: "off"
  timeout:
    minutes: 5
  continue_on_timeout: true

# Check if timed out
- if:
    - condition: template
      value_template: "{{ wait.trigger == none }}"
  then:
    - service: notify.mobile
      data:
        message: "Door still open after 5 minutes!"
```

---

## Quick Debug Tools

### Developer Tools - States

```yaml
# Check entity state
Developer Tools → States → Filter by entity_id

# Common state issues to look for:
# - 'unavailable': Device offline
# - 'unknown': No data received yet
# - 'None': Template error or missing attribute
```

### Developer Tools - Services

```yaml
# Test any service call
Developer Tools → Services → Select service → Fill data → Call Service

# Example test:
Service: light.turn_on
Entity: light.living_room
Service Data:
  brightness_pct: 50
```

### Developer Tools - Template

```yaml
# Test templates live
Developer Tools → Template

# Paste your template:
{{ states('sensor.temperature') | float * 1.8 + 32 }}
# Result shows immediately
```

### Logs

```yaml
# Filter logs for specific integration
Configuration → Settings → Logs → Filter

# Increase log level temporarily:
logger:
  default: info
  logs:
    homeassistant.components.automation: debug
    custom_components.your_integration: debug
```

### Trace

```yaml
# View automation execution trace
Settings → Automations → Click automation → Traces

# Shows:
# - Trigger that fired
# - Condition evaluations
# - Each action step with timing
# - Any errors
```

---

## Common Issues Reference

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Entity unavailable | Device offline | Check power/network |
| Template shows 'unknown' | Entity doesn't exist | Verify entity_id |
| Automation never triggers | Wrong trigger type | Check trigger config |
| Automation triggers but no action | Condition false | Test conditions |
| Service call fails | Wrong domain | Match service to entity type |
| Script hangs | No timeout on wait | Add timeout |
| 'NoneType' error | Missing attribute | Use `default()` filter |
| Float/int error | Wrong type | Use type conversion |

---

## See Also

- [automations.md](automations.md) - Automation reference
- [jinja2-templates.md](jinja2-templates.md) - Template syntax
- [troubleshooting.md](troubleshooting.md) - Common errors
