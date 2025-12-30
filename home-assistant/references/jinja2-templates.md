# Home Assistant Jinja2 Templates Reference

## Table of Contents
- [Introduction](#introduction)
- [Basic Syntax](#basic-syntax)
- [Accessing States](#accessing-states)
- [Accessing Attributes](#accessing-attributes)
- [Built-in Filters](#built-in-filters)
- [Home Assistant Filters](#home-assistant-filters)
- [Built-in Tests](#built-in-tests)
- [Home Assistant Functions](#home-assistant-functions)
- [Control Structures](#control-structures)
- [Variables and Macros](#variables-and-macros)
- [Common Patterns](#common-patterns)
- [Template Sensors](#template-sensors)
- [Debugging Templates](#debugging-templates)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Introduction

Jinja2 is the templating engine used throughout Home Assistant for dynamic values. Templates are used in:
- Automations (triggers, conditions, actions)
- Scripts
- Template sensors and binary sensors
- Notifications
- Dashboard cards

### Template Locations

| Location | Syntax |
|----------|--------|
| Automation action data | `"{{ template }}"` |
| Notification message | `"{{ template }}"` |
| Template sensor | `>` or `|-` multiline |
| Condition value_template | `"{{ template }}"` |

---

## Basic Syntax

### Expressions

```jinja
{# Output a value #}
{{ expression }}

{# Comment (not rendered) #}
{# This is a comment #}

{# Statement (control flow) #}
{% if condition %}
  content
{% endif %}
```

### String Literals

```jinja
{# Single quotes #}
{{ 'Hello World' }}

{# Double quotes #}
{{ "Hello World" }}

{# With variables #}
{{ "Hello " ~ name }}
```

### Numbers

```jinja
{{ 42 }}
{{ 3.14 }}
{{ 1e6 }}
```

### Boolean

```jinja
{{ true }}
{{ false }}
{{ True }}   {# Also works #}
{{ False }}  {# Also works #}
```

### Lists

```jinja
{{ [1, 2, 3] }}
{{ ['a', 'b', 'c'] }}
{{ [states('sensor.a'), states('sensor.b')] }}
```

### Dictionaries

```jinja
{{ {'key': 'value', 'number': 42} }}
```

---

## Accessing States

### Get Entity State

```jinja
{# Get state value #}
{{ states('sensor.temperature') }}
{# Returns: "22.5" (always a string) #}

{# Get state with domain #}
{{ states.sensor.temperature.state }}

{# Check if state is available #}
{{ states('sensor.temperature') not in ['unknown', 'unavailable'] }}
```

### Get All States

```jinja
{# All states (list of state objects) #}
{% for state in states %}
  {{ state.entity_id }}: {{ state.state }}
{% endfor %}

{# All states for a domain #}
{% for light in states.light %}
  {{ light.entity_id }}: {{ light.state }}
{% endfor %}

{# Count entities in a state #}
{{ states.light | selectattr('state', 'eq', 'on') | list | count }}
```

### State Object Properties

```jinja
{% set sensor = states.sensor.temperature %}

{{ sensor.entity_id }}     {# sensor.temperature #}
{{ sensor.state }}         {# "22.5" #}
{{ sensor.domain }}        {# sensor #}
{{ sensor.object_id }}     {# temperature #}
{{ sensor.name }}          {# Temperature (friendly name) #}
{{ sensor.last_changed }}  {# datetime object #}
{{ sensor.last_updated }}  {# datetime object #}
{{ sensor.attributes }}    {# dict of attributes #}
```

---

## Accessing Attributes

### Get Single Attribute

```jinja
{# Using state_attr function (recommended) #}
{{ state_attr('light.bedroom', 'brightness') }}

{# Using states object #}
{{ states.light.bedroom.attributes.brightness }}

{# With default value if missing #}
{{ state_attr('light.bedroom', 'brightness') | default(0) }}
```

### Get All Attributes

```jinja
{% set attrs = states.light.bedroom.attributes %}

{{ attrs.brightness }}
{{ attrs.color_temp }}
{{ attrs.friendly_name }}
{{ attrs.supported_features }}
```

### Check Attribute Exists

```jinja
{% if state_attr('light.bedroom', 'brightness') is not none %}
  Brightness: {{ state_attr('light.bedroom', 'brightness') }}
{% endif %}

{# Or using 'in' #}
{% if 'brightness' in states.light.bedroom.attributes %}
  Has brightness attribute
{% endif %}
```

---

## Built-in Filters

### String Filters

```jinja
{# Uppercase/lowercase #}
{{ "hello" | upper }}        {# HELLO #}
{{ "HELLO" | lower }}        {# hello #}
{{ "hello" | capitalize }}   {# Hello #}
{{ "hello world" | title }}  {# Hello World #}

{# Trim whitespace #}
{{ "  hello  " | trim }}     {# hello #}

{# Replace #}
{{ "hello_world" | replace("_", " ") }}  {# hello world #}

{# Truncate #}
{{ "long string" | truncate(5) }}  {# lo... #}

{# Default value #}
{{ undefined_var | default("fallback") }}

{# Join list to string #}
{{ ['a', 'b', 'c'] | join(', ') }}  {# a, b, c #}

{# Split string to list #}
{{ "a,b,c" | split(',') }}  {# ['a', 'b', 'c'] #}

{# Regex replace #}
{{ "hello123world" | regex_replace('[0-9]+', '-') }}  {# hello-world #}

{# Regex match #}
{{ "hello123" | regex_match('[a-z]+([0-9]+)') }}  {# True #}

{# Regex find all #}
{{ "a1b2c3" | regex_findall('[0-9]+') }}  {# ['1', '2', '3'] #}
```

### Number Filters

```jinja
{# Convert to types #}
{{ "42" | int }}            {# 42 #}
{{ "42" | int(0) }}         {# 42, with default 0 if fails #}
{{ "3.14" | float }}        {# 3.14 #}
{{ "3.14" | float(0) }}     {# 3.14, with default 0 if fails #}

{# Rounding #}
{{ 3.14159 | round(2) }}    {# 3.14 #}
{{ 3.5 | round(0) }}        {# 4 #}
{{ 3.4 | round(0) }}        {# 3 #}
{{ 3.5 | round(0, 'floor') }}  {# 3 #}
{{ 3.5 | round(0, 'ceil') }}   {# 4 #}

{# Absolute value #}
{{ -5 | abs }}              {# 5 #}

{# Format number #}
{{ 1234567 | format_number }}  {# 1,234,567 (based on locale) #}
```

### List Filters

```jinja
{# First/last #}
{{ [1, 2, 3] | first }}     {# 1 #}
{{ [1, 2, 3] | last }}      {# 3 #}

{# Length #}
{{ [1, 2, 3] | length }}    {# 3 #}
{{ [1, 2, 3] | count }}     {# 3 (alias) #}

{# Min/max #}
{{ [5, 2, 8, 1] | min }}    {# 1 #}
{{ [5, 2, 8, 1] | max }}    {# 8 #}

{# Sum/average #}
{{ [1, 2, 3, 4] | sum }}    {# 10 #}
{{ [1, 2, 3, 4] | average }} {# 2.5 #}

{# Sort #}
{{ [3, 1, 2] | sort }}      {# [1, 2, 3] #}
{{ [3, 1, 2] | sort(reverse=true) }}  {# [3, 2, 1] #}

{# Unique #}
{{ [1, 1, 2, 2, 3] | unique | list }}  {# [1, 2, 3] #}

{# Random #}
{{ [1, 2, 3, 4, 5] | random }}  {# Random element #}

{# Shuffle #}
{{ [1, 2, 3, 4, 5] | shuffle | list }}  {# Shuffled list #}

{# Slice #}
{{ [1, 2, 3, 4, 5][1:3] }}  {# [2, 3] #}
{{ [1, 2, 3, 4, 5][:3] }}   {# [1, 2, 3] #}
{{ [1, 2, 3, 4, 5][2:] }}   {# [3, 4, 5] #}

{# Map (apply filter to each) #}
{{ ['a', 'b'] | map('upper') | list }}  {# ['A', 'B'] #}

{# Select (filter list) #}
{{ [1, 2, 3, 4, 5] | select('gt', 3) | list }}  {# [4, 5] #}

{# Reject (inverse of select) #}
{{ [1, 2, 3, 4, 5] | reject('gt', 3) | list }}  {# [1, 2, 3] #}

{# Select/reject attr (for objects) #}
{{ states.light | selectattr('state', 'eq', 'on') | list }}
{{ states.sensor | rejectattr('state', 'in', ['unknown', 'unavailable']) | list }}
```

### Dictionary Filters

```jinja
{# Get items #}
{{ {'a': 1, 'b': 2} | items | list }}  {# [('a', 1), ('b', 2)] #}

{# Get keys #}
{{ {'a': 1, 'b': 2} | keys | list }}   {# ['a', 'b'] #}

{# Get values #}
{{ {'a': 1, 'b': 2} | values | list }} {# [1, 2] #}

{# Combine dicts #}
{{ {'a': 1} | combine({'b': 2}) }}     {# {'a': 1, 'b': 2} #}
```

---

## Home Assistant Filters

### Type Conversion

```jinja
{# Boolean #}
{{ 'on' | bool }}           {# True #}
{{ 'off' | bool }}          {# False #}
{{ 'true' | bool }}         {# True #}
{{ '1' | bool }}            {# True #}
{{ 0 | bool }}              {# False #}

{# With default #}
{{ 'invalid' | bool(false) }}  {# False #}
```

### Time Filters

```jinja
{# Timestamp conversion #}
{{ now() | as_timestamp }}  {# Unix timestamp #}
{{ as_timestamp('2024-01-01 12:00:00') }}

{# Format datetime #}
{{ now() | timestamp_custom('%Y-%m-%d %H:%M:%S') }}
{{ now() | timestamp_custom('%H:%M', true) }}  {# Local time #}

{# Time since/until #}
{{ states.sensor.temperature.last_changed | relative_time }}
{# e.g., "5 minutes ago" #}

{# Parse timestamp #}
{{ as_datetime('2024-01-01 12:00:00') }}
{{ strptime('01/01/2024', '%d/%m/%Y') }}
```

### Encoding Filters

```jinja
{# JSON #}
{{ {'key': 'value'} | to_json }}
{{ '{"key": "value"}' | from_json }}

{# Base64 #}
{{ 'hello' | base64_encode }}
{{ 'aGVsbG8=' | base64_decode }}

{# URL encoding #}
{{ 'hello world' | urlencode }}  {# hello%20world #}

{# MD5 hash #}
{{ 'password' | hash('md5') }}

{# SHA256 hash #}
{{ 'password' | hash('sha256') }}
```

### Unit Conversion

```jinja
{# Ordinal #}
{{ 1 | ordinal }}   {# 1st #}
{{ 2 | ordinal }}   {# 2nd #}
{{ 3 | ordinal }}   {# 3rd #}

{# Bitwise #}
{{ 5 | bitwise_and(3) }}  {# 1 #}
{{ 5 | bitwise_or(3) }}   {# 7 #}

{# Pack/unpack binary #}
{{ 'ABC' | pack('>3B') }}
{{ [65, 66, 67] | unpack('>3B') }}
```

---

## Built-in Tests

Tests are used with `is` keyword:

```jinja
{# Defined/undefined #}
{{ x is defined }}
{{ x is undefined }}

{# None check #}
{{ x is none }}
{{ x is not none }}

{# Type checks #}
{{ x is string }}
{{ x is number }}
{{ x is integer }}
{{ x is float }}
{{ x is iterable }}
{{ x is mapping }}    {# dict #}
{{ x is sequence }}   {# list #}

{# Comparison #}
{{ x is eq(5) }}
{{ x is ne(5) }}
{{ x is lt(5) }}
{{ x is le(5) }}
{{ x is gt(5) }}
{{ x is ge(5) }}

{# String tests #}
{{ x is lower }}
{{ x is upper }}

{# Truthiness #}
{{ x is truthy }}
{{ x is falsy }}

{# Container tests #}
{{ x is in([1, 2, 3]) }}
{{ x is containing(2) }}

{# Regex test #}
{{ x is match('[0-9]+') }}
{{ x is search('[0-9]+') }}
```

---

## Home Assistant Functions

### State Functions

```jinja
{# Get state #}
{{ states('sensor.temperature') }}

{# Get attribute #}
{{ state_attr('light.bedroom', 'brightness') }}

{# Check state #}
{{ is_state('light.bedroom', 'on') }}
{{ is_state('light.bedroom', ['on', 'off']) }}  {# Multiple values #}

{# Check attribute #}
{{ is_state_attr('light.bedroom', 'brightness', 255) }}

{# Has value (not unknown/unavailable) #}
{{ has_value('sensor.temperature') }}

{# Expand groups/areas #}
{{ expand('group.living_room_lights') | map(attribute='entity_id') | list }}
{{ expand(states.light) | selectattr('state', 'eq', 'on') | list }}
```

### Area/Device/Entity Functions

```jinja
{# Get entities in area #}
{{ area_entities('living_room') }}

{# Get devices in area #}
{{ area_devices('living_room') }}

{# Get area name #}
{{ area_name('light.living_room') }}
{{ area_id('Living Room') }}

{# Get device entities #}
{{ device_entities('abc123...') }}

{# Get device attributes #}
{{ device_attr('abc123...', 'name') }}
{{ device_attr('abc123...', 'model') }}
{{ device_attr('abc123...', 'manufacturer') }}

{# Get integration entities #}
{{ integration_entities('hue') }}

{# Get entity's device #}
{{ device_id('light.bedroom') }}
```

### Time Functions

```jinja
{# Current time #}
{{ now() }}              {# Current datetime #}
{{ utcnow() }}           {# Current UTC datetime #}
{{ today_at('08:00') }}  {# Today at specific time #}

{# Time components #}
{{ now().year }}
{{ now().month }}
{{ now().day }}
{{ now().hour }}
{{ now().minute }}
{{ now().second }}
{{ now().weekday() }}    {# 0=Monday, 6=Sunday #}
{{ now().isoweekday() }} {# 1=Monday, 7=Sunday #}

{# Time delta #}
{{ now() - timedelta(hours=1) }}
{{ now() + timedelta(days=7) }}
{{ now() - timedelta(minutes=30) }}

{# As timestamp #}
{{ as_timestamp(now()) }}
{{ as_timestamp(states.sensor.x.last_changed) }}

{# As datetime #}
{{ as_datetime(1704067200) }}
{{ as_datetime('2024-01-01 12:00:00') }}

{# As local time #}
{{ as_local(utcnow()) }}

{# Time comparisons #}
{{ now() > today_at('08:00') }}
{{ now().hour >= 8 and now().hour < 22 }}
```

### Math Functions

```jinja
{# Basic math #}
{{ sin(3.14159 / 2) }}
{{ cos(0) }}
{{ tan(0.785) }}
{{ sqrt(16) }}
{{ log(100, 10) }}
{{ e }}
{{ pi }}

{# Rounding #}
{{ floor(3.7) }}   {# 3 #}
{{ ceil(3.2) }}    {# 4 #}

{# Statistics #}
{{ max(1, 5, 3) }}
{{ min(1, 5, 3) }}
```

### Other Functions

```jinja
{# Random #}
{{ range(1, 100) | random }}
{{ random(10) }}    {# 0-9 #}

{# Distance (between zones/entities) #}
{{ distance('zone.home', 'zone.work') }}
{{ distance('device_tracker.phone') }}  {# From home #}

{# Closest zone #}
{{ closest(states.zone) }}
{{ closest('zone.home', 'zone.work', 'zone.store') }}

{# Input datetime value #}
{{ input_datetime('input_datetime.alarm_time') }}

{# Slugify #}
{{ 'Living Room Light' | slugify }}  {# living_room_light #}
```

---

## Control Structures

### If/Elif/Else

```jinja
{% if condition %}
  Result if true
{% elif other_condition %}
  Result if other true
{% else %}
  Result if all false
{% endif %}

{# Inline if #}
{{ 'on' if condition else 'off' }}

{# Complex conditions #}
{% if states('sensor.temp') | float > 25 and is_state('climate.ac', 'off') %}
  Turn on AC
{% endif %}
```

### For Loops

```jinja
{# Basic loop #}
{% for item in [1, 2, 3] %}
  {{ item }}
{% endfor %}

{# Loop over entities #}
{% for light in states.light %}
  {{ light.entity_id }}: {{ light.state }}
{% endfor %}

{# With index #}
{% for item in items %}
  {{ loop.index }}: {{ item }}   {# 1-based #}
  {{ loop.index0 }}: {{ item }}  {# 0-based #}
{% endfor %}

{# Loop variables #}
{{ loop.first }}     {# True on first iteration #}
{{ loop.last }}      {# True on last iteration #}
{{ loop.length }}    {# Total items #}
{{ loop.revindex }}  {# Reverse index #}

{# With else (if empty) #}
{% for light in states.light | selectattr('state', 'eq', 'on') %}
  {{ light.name }} is on
{% else %}
  No lights are on
{% endfor %}
```

### Set Variables

```jinja
{# Set variable #}
{% set temp = states('sensor.temperature') | float %}
{% set message = 'Temperature is ' ~ temp ~ ' degrees' %}

{# Set multiple #}
{% set x, y = 1, 2 %}

{# Set from expression #}
{% set lights_on = states.light | selectattr('state', 'eq', 'on') | list %}
```

### Whitespace Control

```jinja
{# Remove whitespace before/after #}
{%- if condition -%}
  content
{%- endif -%}

{# Only before #}
{%- if condition %}
  content
{% endif %}

{# Only after #}
{% if condition -%}
  content
{% endif %}
```

---

## Variables and Macros

### Variables

```jinja
{% set greeting = 'Hello' %}
{% set name = 'World' %}
{{ greeting }}, {{ name }}!

{# Set from state #}
{% set temp = states('sensor.temperature') | float(0) %}
{% set humidity = states('sensor.humidity') | float(0) %}

{# Computed #}
{% set comfort = temp > 20 and temp < 25 and humidity < 60 %}
{{ 'Comfortable' if comfort else 'Not comfortable' }}
```

### Namespace (for loop variables)

```jinja
{# Variables inside loops need namespace #}
{% set ns = namespace(total=0, count=0) %}
{% for sensor in states.sensor | selectattr('attributes.device_class', 'eq', 'temperature') %}
  {% set ns.total = ns.total + sensor.state | float(0) %}
  {% set ns.count = ns.count + 1 %}
{% endfor %}
Average: {{ (ns.total / ns.count) | round(1) if ns.count > 0 else 'N/A' }}
```

### Macros

```jinja
{# Define macro #}
{% macro format_temp(entity_id) %}
  {{ states(entity_id) | float | round(1) }}°C
{% endmacro %}

{# Use macro #}
Living room: {{ format_temp('sensor.living_room_temp') }}
Bedroom: {{ format_temp('sensor.bedroom_temp') }}

{# Macro with default parameters #}
{% macro light_status(entity_id, on_text='ON', off_text='OFF') %}
  {{ on_text if is_state(entity_id, 'on') else off_text }}
{% endmacro %}

{{ light_status('light.bedroom') }}
{{ light_status('light.bedroom', '💡', '⚫') }}
```

---

## Common Patterns

### Safe State Access

```jinja
{# With default value #}
{{ states('sensor.temperature') | float(0) }}

{# Check availability first #}
{% if has_value('sensor.temperature') %}
  {{ states('sensor.temperature') }}
{% else %}
  Unavailable
{% endif %}

{# Compact availability check #}
{{ states('sensor.temperature') if has_value('sensor.temperature') else 'N/A' }}
```

### Count Entities by State

```jinja
{# Lights on #}
{{ states.light | selectattr('state', 'eq', 'on') | list | count }}

{# Windows open #}
{{ states.binary_sensor
   | selectattr('attributes.device_class', 'eq', 'window')
   | selectattr('state', 'eq', 'on')
   | list | count }}

{# Low battery sensors #}
{{ states.sensor
   | selectattr('attributes.device_class', 'eq', 'battery')
   | selectattr('state', 'lt', '20')
   | list | count }}
```

### Time-Based Logic

```jinja
{# Time of day #}
{% set hour = now().hour %}
{% if hour < 6 %}
  Night
{% elif hour < 12 %}
  Morning
{% elif hour < 18 %}
  Afternoon
{% else %}
  Evening
{% endif %}

{# Is it daytime #}
{{ 'day' if 6 <= now().hour < 22 else 'night' }}

{# Minutes since event #}
{% set last = as_timestamp(states.sensor.motion.last_changed) %}
{% set now_ts = as_timestamp(now()) %}
{{ ((now_ts - last) / 60) | round(0) }} minutes ago

{# Is weekend #}
{{ now().weekday() >= 5 }}
```

### Temperature Comfort

```jinja
{% set temp = states('sensor.temperature') | float(20) %}
{% set humidity = states('sensor.humidity') | float(50) %}

{% if temp < 18 %}
  Cold 🥶
{% elif temp < 22 %}
  Comfortable 😊
{% elif temp < 26 %}
  Warm 😅
{% else %}
  Hot 🥵
{% endif %}

{# Heat index approximation #}
{% set hi = temp + 0.5 * (humidity - 50) * 0.1 %}
Feels like: {{ hi | round(1) }}°C
```

### Dynamic Brightness

```jinja
{# Based on time of day #}
{% set hour = now().hour %}
{% if hour < 7 %}
  10
{% elif hour < 9 %}
  {{ 10 + (hour - 6) * 30 }}
{% elif hour < 20 %}
  100
{% elif hour < 22 %}
  {{ 100 - (hour - 19) * 35 }}
{% else %}
  10
{% endif %}
```

### List Formatting

```jinja
{# List lights that are on #}
{% set lights_on = states.light | selectattr('state', 'eq', 'on') | map(attribute='name') | list %}
{% if lights_on %}
  Lights on: {{ lights_on | join(', ') }}
{% else %}
  No lights on
{% endif %}

{# Format as bullet list #}
{% for light in states.light | selectattr('state', 'eq', 'on') %}
- {{ light.name }}
{% endfor %}
```

### Aggregate Sensor Values

```jinja
{# Average temperature #}
{% set temps = states.sensor
   | selectattr('attributes.device_class', 'eq', 'temperature')
   | rejectattr('state', 'in', ['unknown', 'unavailable'])
   | map(attribute='state')
   | map('float')
   | list %}
{{ (temps | sum / temps | length) | round(1) if temps else 'N/A' }}

{# Total power consumption #}
{% set power = states.sensor
   | selectattr('attributes.device_class', 'eq', 'power')
   | rejectattr('state', 'in', ['unknown', 'unavailable'])
   | map(attribute='state')
   | map('float')
   | sum %}
{{ power | round(0) }} W
```

---

## Template Sensors

### Basic Template Sensor

```yaml
template:
  - sensor:
      - name: "Average Temperature"
        unit_of_measurement: "°C"
        state: >
          {% set temps = states.sensor
             | selectattr('attributes.device_class', 'eq', 'temperature')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | map(attribute='state')
             | map('float')
             | list %}
          {{ (temps | sum / temps | length) | round(1) if temps else none }}
        availability: >
          {{ states.sensor
             | selectattr('attributes.device_class', 'eq', 'temperature')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | list | count > 0 }}
```

### With Attributes

```yaml
template:
  - sensor:
      - name: "System Status"
        state: "{{ 'OK' if lights_ok and sensors_ok else 'Warning' }}"
        attributes:
          lights_on: >
            {{ states.light | selectattr('state', 'eq', 'on') | list | count }}
          windows_open: >
            {{ states.binary_sensor
               | selectattr('attributes.device_class', 'eq', 'window')
               | selectattr('state', 'eq', 'on')
               | list | count }}
          last_updated: "{{ now().isoformat() }}"
```

### Binary Template Sensor

```yaml
template:
  - binary_sensor:
      - name: "Someone Home"
        state: >
          {{ states.person | selectattr('state', 'eq', 'home') | list | count > 0 }}
        device_class: presence
```

### Trigger-Based Template

```yaml
template:
  - trigger:
      - platform: state
        entity_id: sensor.power
    sensor:
      - name: "Power Average (5min)"
        unit_of_measurement: "W"
        state: >
          {% set current = trigger.to_state.state | float(0) %}
          {% set values = this.attributes.get('samples', []) %}
          {% set values = (values + [current])[-30:] %}
          {{ (values | sum / values | length) | round(1) }}
        attributes:
          samples: >
            {% set current = trigger.to_state.state | float(0) %}
            {% set values = this.attributes.get('samples', []) %}
            {{ (values + [current])[-30:] }}
```

---

## Debugging Templates

### Developer Tools

1. Go to **Developer Tools → Template**
2. Enter your template
3. See real-time output

### Useful Debug Expressions

```jinja
{# Show entity state details #}
{{ states.sensor.temperature }}

{# Show all attributes #}
{{ states.sensor.temperature.attributes }}

{# Show type #}
{{ states('sensor.temperature') | type_debug }}

{# List all entities matching pattern #}
{% for e in states if 'temperature' in e.entity_id %}
  {{ e.entity_id }}: {{ e.state }}
{% endfor %}
```

### Common Debug Patterns

```jinja
{# Check what you're working with #}
Value: {{ value }}
Type: {{ value | type_debug }}
Is string: {{ value is string }}
Is number: {{ value is number }}

{# Debug filter chain #}
{% set items = states.light %}
Step 1 (all): {{ items | list | count }}
{% set items = items | selectattr('state', 'eq', 'on') %}
Step 2 (on): {{ items | list | count }}
{% set items = items | selectattr('attributes.brightness', 'defined') %}
Step 3 (has brightness): {{ items | list | count }}
```

---

## Best Practices

### Always Use Defaults

```jinja
{# Bad - may error #}
{{ states('sensor.temp') | float }}

{# Good - with default #}
{{ states('sensor.temp') | float(0) }}
{{ states('sensor.temp') | int(0) }}
```

### Check Availability

```jinja
{# Bad - includes unavailable values #}
{% for s in states.sensor %}
  {{ s.state }}
{% endfor %}

{# Good - filter unavailable #}
{% for s in states.sensor | rejectattr('state', 'in', ['unknown', 'unavailable']) %}
  {{ s.state }}
{% endfor %}

{# Or use has_value #}
{% if has_value('sensor.temp') %}
  {{ states('sensor.temp') }}
{% endif %}
```

### Use Meaningful Variable Names

```jinja
{# Bad #}
{% set x = states('sensor.temperature') | float %}
{% set y = x > 25 %}

{# Good #}
{% set temperature = states('sensor.temperature') | float(0) %}
{% set is_hot = temperature > 25 %}
```

### Keep Templates Readable

```jinja
{# Bad - one long line #}
{{ states.sensor | selectattr('attributes.device_class', 'eq', 'temperature') | rejectattr('state', 'in', ['unknown', 'unavailable']) | map(attribute='state') | map('float') | sum / states.sensor | selectattr('attributes.device_class', 'eq', 'temperature') | rejectattr('state', 'in', ['unknown', 'unavailable']) | list | count }}

{# Good - split into steps #}
{% set temp_sensors = states.sensor
   | selectattr('attributes.device_class', 'eq', 'temperature')
   | rejectattr('state', 'in', ['unknown', 'unavailable'])
   | list %}
{% set temps = temp_sensors | map(attribute='state') | map('float') | list %}
{{ (temps | sum / temps | length) | round(1) if temps else 'N/A' }}
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `UndefinedError` | Variable not defined | Use `| default()` |
| `TemplateRuntimeError` | Type mismatch | Check types, use conversion |
| `float() argument must be a string or a number` | Invalid value | Use `float(0)` with default |
| `'None' has no attribute 'x'` | Entity/attribute doesn't exist | Check entity exists, use `is not none` |

### Type Conversion Issues

```jinja
{# String that looks like number #}
{{ "42" + 1 }}  {# Error! #}
{{ "42" | int + 1 }}  {# 43 #}

{# Boolean confusion #}
{{ states('light.x') == 'on' }}  {# True/False #}
{{ states('light.x') | bool }}  {# True (from string 'on') #}

{# None handling #}
{{ state_attr('light.x', 'missing_attr') }}  {# None #}
{{ state_attr('light.x', 'missing_attr') | default(0) }}  {# 0 #}
```

### Entity Not Found

```jinja
{# Check if entity exists #}
{% if states('sensor.maybe_exists') not in ['unknown', 'unavailable'] %}
  {{ states('sensor.maybe_exists') }}
{% else %}
  Entity not available
{% endif %}

{# Using has_value #}
{{ states('sensor.x') if has_value('sensor.x') else 'N/A' }}
```

### Filter Chain Debugging

```jinja
{# When a filter chain fails, break it down #}

{# Full chain (might fail) #}
{{ states.sensor | selectattr('state', 'gt', '20') | list }}

{# Debug step by step #}
All sensors: {{ states.sensor | list | count }}

{# Check states are numeric #}
{% for s in states.sensor %}
  {{ s.entity_id }}: "{{ s.state }}" ({{ s.state | float(none) }})
{% endfor %}

{# Filter non-numeric first #}
{% set valid = states.sensor | rejectattr('state', 'in', ['unknown', 'unavailable']) | list %}
Valid: {{ valid | count }}
```
