# Home Assistant State Nodes

Nodes for reading entity states.

## api-current-state

Get the current state of a **single** entity.

### IMPORTANT LIMITATION

This node only accepts a **single entity_id**. It does NOT support:
- Patterns
- Regex
- Multiple entities

For multiple entities, use:
1. `ha-get-entities` node
2. Function node with global states

### Configuration

```json
{
  "type": "api-current-state",
  "entity_id": "sensor.temperature",
  "stateType": "str",
  "blockInputOverrides": false,
  "outputProperties": [
    {
      "property": "payload",
      "propertyType": "msg",
      "value": "",
      "valueType": "entityState"
    },
    {
      "property": "data",
      "propertyType": "msg",
      "value": "",
      "valueType": "entity"
    }
  ],
  "for": "0",
  "forType": "num",
  "forUnits": "minutes"
}
```

### stateType Options

| Value | Description | Example Output |
|-------|-------------|----------------|
| `str` | String (default) | `"23.5"` |
| `num` | Number | `23.5` |
| `bool` | Boolean | `true` |

### Output Properties

| valueType | Description |
|-----------|-------------|
| `entityState` | Just the state value |
| `entity` | Full entity object |
| `config` | Node configuration |

### Output Message

```javascript
{
  payload: "23.5",  // or 23.5 if stateType is num
  data: {
    entity_id: "sensor.temperature",
    state: "23.5",
    attributes: {
      unit_of_measurement: "°C",
      device_class: "temperature",
      friendly_name: "Living Room Temperature"
    },
    last_changed: "2024-01-01T12:00:00Z",
    last_updated: "2024-01-01T12:00:00Z"
  }
}
```

### "for" Duration Check

Check if state has been stable for duration:

```json
{
  "for": "5",
  "forType": "num",
  "forUnits": "minutes"
}
```

Adds `msg.timeSinceChangedMs` to output.

### Input Override

Pass entity_id dynamically:

```javascript
msg.payload = { entity_id: "sensor.bedroom_temperature" };
return msg;
```

---

## ha-get-entities

Query multiple entities based on rules.

### Configuration

```json
{
  "type": "ha-get-entities",
  "server": "",
  "rules": [
    {
      "property": "entity_id",
      "logic": "starts_with",
      "value": "light."
    },
    {
      "property": "state",
      "logic": "is",
      "value": "on"
    }
  ],
  "outputType": "array",
  "outputEmptyResults": false,
  "outputLocationType": "msg",
  "outputLocation": "payload"
}
```

### Rule Properties

| Property | Description |
|----------|-------------|
| `entity_id` | Entity ID string |
| `state` | State value |
| `attributes.X` | Specific attribute |
| `last_changed` | Last changed timestamp |
| `last_updated` | Last updated timestamp |

### Rule Logic Options

| Logic | Description |
|-------|-------------|
| `is` | Exact match |
| `is_not` | Not equal |
| `lt` | Less than |
| `lte` | Less than or equal |
| `gt` | Greater than |
| `gte` | Greater than or equal |
| `starts_with` | String starts with |
| `ends_with` | String ends with |
| `in` | Value in list |
| `not_in` | Value not in list |
| `includes` | Contains substring |
| `does_not_include` | Doesn't contain |
| `in_group` | Entity is in group |
| `regex` | Regular expression match |
| `jsonata` | JSONata expression |

### Output Types

| Type | Description |
|------|-------------|
| `array` | Array of entity objects |
| `count` | Number of matching entities |
| `random` | Single random match |
| `split` | Send separate message per entity |

### Example: All Lights That Are On

```json
{
  "rules": [
    { "property": "entity_id", "logic": "starts_with", "value": "light." },
    { "property": "state", "logic": "is", "value": "on" }
  ],
  "outputType": "array"
}
```

Output:
```javascript
{
  payload: [
    { entity_id: "light.living_room", state: "on", ... },
    { entity_id: "light.bedroom", state: "on", ... }
  ]
}
```

### Example: Temperature Sensors Above 25°C

```json
{
  "rules": [
    { "property": "entity_id", "logic": "starts_with", "value": "sensor." },
    { "property": "attributes.device_class", "logic": "is", "value": "temperature" },
    { "property": "state", "logic": "gt", "value": "25" }
  ]
}
```

### Example: Entities With Low Battery

```json
{
  "rules": [
    { "property": "attributes.battery", "logic": "lt", "value": "20" }
  ]
}
```

### Example: Using Regex

```json
{
  "rules": [
    { "property": "entity_id", "logic": "regex", "value": "^(light|switch)\\..+_living_room$" }
  ]
}
```

---

## api-get-history

Get historical state data.

### Configuration

```json
{
  "type": "api-get-history",
  "entityId": "sensor.temperature",
  "startDate": "",
  "endDate": "",
  "relativeDates": true,
  "outputType": "array",
  "outputLocationKey": "payload"
}
```

### Date Range Options

**Relative (recommended):**
```json
{
  "relativeDates": true,
  "startDate": "24",  // hours ago
  "endDate": "0"      // now
}
```

**Absolute:**
```json
{
  "relativeDates": false,
  "startDate": "2024-01-01T00:00:00Z",
  "endDate": "2024-01-02T00:00:00Z"
}
```

### Output Types

| Type | Description |
|------|-------------|
| `array` | Array of state changes |
| `split` | Separate message per state change |

### Output Message

```javascript
{
  payload: [
    {
      entity_id: "sensor.temperature",
      state: "22.5",
      attributes: { ... },
      last_changed: "2024-01-01T10:00:00Z"
    },
    {
      entity_id: "sensor.temperature",
      state: "23.0",
      attributes: { ... },
      last_changed: "2024-01-01T11:00:00Z"
    }
  ]
}
```

### Processing History

```javascript
// Calculate average
const history = msg.payload;
const values = history
  .map(s => parseFloat(s.state))
  .filter(v => !isNaN(v));

const average = values.reduce((a, b) => a + b, 0) / values.length;
msg.average = Math.round(average * 100) / 100;
return msg;
```

---

## poll-state

Periodically get entity state.

### Configuration

```json
{
  "type": "poll-state",
  "entity_id": "sensor.power",
  "updateInterval": 60,
  "updateIntervalUnits": "seconds",
  "outputInitially": true,
  "stateType": "num",
  "ifState": "",
  "ifStateType": "str",
  "ifStateOperator": "is"
}
```

### Interval Units

- `milliseconds`
- `seconds`
- `minutes`
- `hours`

### Conditional Output

Only output when condition is met:

```json
{
  "ifState": "100",
  "ifStateType": "num",
  "ifStateOperator": "gt"
}
```

---

## ha-wait-until

Pause flow until condition is met.

### Configuration

```json
{
  "type": "ha-wait-until",
  "entityId": "binary_sensor.door",
  "entityIdType": "exact",
  "property": "state",
  "comparator": "is",
  "value": "off",
  "valueType": "str",
  "timeout": 30,
  "timeoutUnits": "seconds",
  "checkCurrentState": true,
  "blockInputOverrides": false
}
```

### Outputs

- **Output 1**: Condition was met
- **Output 2**: Timeout occurred

### Use Cases

#### Wait for Door to Close

```json
{
  "entityId": "binary_sensor.front_door",
  "property": "state",
  "comparator": "is",
  "value": "off",
  "timeout": 60,
  "timeoutUnits": "seconds"
}
```

#### Wait for Person to Arrive

```json
{
  "entityId": "person.john",
  "property": "state",
  "comparator": "is",
  "value": "home",
  "timeout": 0
}
```

Note: `timeout: 0` means wait indefinitely.

---

## Accessing States in Function Nodes

For complex state queries, use function nodes:

### Get All States

```javascript
const states = global.get("homeassistant").homeAssistant.states;
```

### Query by Pattern

```javascript
const lights = Object.keys(states)
  .filter(id => id.startsWith("light."))
  .map(id => states[id]);
```

### Check Multiple Entities

```javascript
const entitiesToCheck = [
  "binary_sensor.door_front",
  "binary_sensor.door_back",
  "binary_sensor.door_garage"
];

const openDoors = entitiesToCheck
  .filter(id => states[id]?.state === "on")
  .map(id => states[id].attributes.friendly_name);

if (openDoors.length > 0) {
  msg.openDoors = openDoors;
  return msg;
}
return null;
```

### Get Entities by Attribute

```javascript
const batteryLow = Object.entries(states)
  .filter(([id, entity]) => {
    const battery = entity.attributes?.battery;
    return battery !== undefined && battery < 20;
  })
  .map(([id, entity]) => ({
    id,
    name: entity.attributes.friendly_name,
    battery: entity.attributes.battery
  }));

msg.payload = batteryLow;
return msg;
```

### Aggregate Values

```javascript
const tempSensors = Object.entries(states)
  .filter(([id, entity]) =>
    id.startsWith("sensor.") &&
    entity.attributes?.device_class === "temperature"
  )
  .map(([id, entity]) => ({
    id,
    temp: parseFloat(entity.state),
    name: entity.attributes.friendly_name
  }))
  .filter(s => !isNaN(s.temp));

const avgTemp = tempSensors.reduce((sum, s) => sum + s.temp, 0) / tempSensors.length;
const maxTemp = Math.max(...tempSensors.map(s => s.temp));
const minTemp = Math.min(...tempSensors.map(s => s.temp));

msg.payload = {
  average: Math.round(avgTemp * 10) / 10,
  max: maxTemp,
  min: minTemp,
  sensors: tempSensors
};
return msg;
```
