# JSONata in Node-RED

JSONata is a powerful query and transformation language for JSON data.

## Where JSONata is Used

- Change node (JSONata option)
- Switch node (JSONata expression)
- Some HA node properties
- Debug node status

## Basic Syntax

### Access Properties

```jsonata
payload              // msg.payload
payload.temperature  // msg.payload.temperature
data.new_state.state // msg.data.new_state.state
```

### Array Access

```jsonata
payload[0]           // First element
payload[-1]          // Last element
payload[0..2]        // First 3 elements
```

### Filter Arrays

```jsonata
payload[state = "on"]                    // Where state is "on"
payload[temperature > 25]                // Where temp > 25
payload[entity_id ~> /light\..*/]        // Regex match
```

## Operators

### Comparison

| Operator | Description |
|----------|-------------|
| `=` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |
| `in` | In array |

### Logical

| Operator | Description |
|----------|-------------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not()` | Logical NOT |

### String

| Operator | Description |
|----------|-------------|
| `&` | Concatenation |
| `~>` | Chain/pipe |

## Common Functions

### String Functions

```jsonata
$string(123)                    // "123"
$length("hello")                // 5
$substring("hello", 0, 3)       // "hel"
$substringBefore("hello-world", "-")  // "hello"
$substringAfter("hello-world", "-")   // "world"
$uppercase("hello")             // "HELLO"
$lowercase("HELLO")             // "hello"
$trim("  hello  ")              // "hello"
$contains("hello", "ell")       // true
$split("a,b,c", ",")            // ["a", "b", "c"]
$join(["a", "b", "c"], ",")     // "a,b,c"
$replace("hello", "l", "x")     // "hexxo"
$match("test123", /[0-9]+/)     // ["123"]
```

### Numeric Functions

```jsonata
$number("123")                  // 123
$round(3.14159, 2)              // 3.14
$floor(3.9)                     // 3
$ceil(3.1)                      // 4
$abs(-5)                        // 5
$sqrt(16)                       // 4
$power(2, 8)                    // 256
$random()                       // Random 0-1
```

### Array Functions

```jsonata
$count(payload)                 // Array length
$sum(payload.value)             // Sum of values
$average(payload.value)         // Average
$max(payload.value)             // Maximum
$min(payload.value)             // Minimum
$append([1,2], [3,4])           // [1,2,3,4]
$reverse([1,2,3])               // [3,2,1]
$sort(payload)                  // Sort ascending
$distinct(payload)              // Unique values
$shuffle(payload)               // Random order
```

### Object Functions

```jsonata
$keys(payload)                  // Object keys
$lookup(payload, "key")         // Get value by key
$merge([{a:1}, {b:2}])          // {a:1, b:2}
$spread(payload)                // Array of {key: value}
$type(payload)                  // "object", "array", etc.
```

### Date/Time Functions

```jsonata
$now()                          // Current timestamp (ms)
$millis()                       // Current timestamp (ms)
$toMillis("2024-01-01")         // Date to milliseconds
$fromMillis(1704067200000)      // Milliseconds to ISO string
```

### Boolean Functions

```jsonata
$not(true)                      // false
$boolean(1)                     // true
$boolean(0)                     // false
$boolean("")                    // false
$boolean("text")                // true
$exists(payload.optional)       // true if defined
```

## Transformations

### Map/Transform

```jsonata
// Transform array of entities
payload.{
  "id": entity_id,
  "name": attributes.friendly_name,
  "value": $number(state)
}
```

### Filter and Transform

```jsonata
// Lights that are on
payload[state = "on"].{
  "id": entity_id,
  "brightness": attributes.brightness
}
```

### Conditional

```jsonata
// If/then/else
payload > 25 ? "Hot" : payload > 15 ? "Warm" : "Cold"
```

### Aggregate

```jsonata
// Sum all values
$sum(payload.value)

// Average temperature
$average(payload[device_class = "temperature"].$number(state))
```

## Node-RED Specific

### Access Message Properties

```jsonata
$flowContext("variableName")    // Flow context
$globalContext("variableName")  // Global context
```

### In Change Node

Set `msg.payload` to:
```jsonata
{
  "entity": data.entity_id,
  "state": payload,
  "brightness": data.new_state.attributes.brightness,
  "changed": $now()
}
```

### In Switch Node

Route messages:
```jsonata
payload = "on" and data.new_state.attributes.brightness > 200
```

### Debug Status

Format status with JSONata:
```jsonata
payload & " (" & $string(data.new_state.attributes.brightness) & "%)"
```

## Home Assistant Examples

### Format Entity State

```jsonata
data.new_state.state & " " & data.new_state.attributes.unit_of_measurement
// "23.5 °C"
```

### Check Multiple Entities

```jsonata
$exists(payload[entity_id = "person.john" and state = "home"]) or
$exists(payload[entity_id = "person.jane" and state = "home"])
```

### Calculate Duration

```jsonata
// Minutes since last changed
($now() - $toMillis(data.new_state.last_changed)) / 60000
```

### Filter by Device Class

```jsonata
payload[attributes.device_class = "temperature" and $number(state) > 25].{
  "room": $substringAfter(entity_id, "sensor."),
  "temp": $number(state)
}
```

### Group by State

```jsonata
{
  "on": payload[state = "on"].entity_id,
  "off": payload[state = "off"].entity_id
}
```

### Build Notification

```jsonata
{
  "title": "Motion Detected",
  "message": "Motion in " & $substringAfter(data.entity_id, "binary_sensor.motion_") & " at " & $fromMillis($now())
}
```

## Debugging JSONata

### Use Debug Node

Set output to "complete msg object" and JSONata expression:

```jsonata
{
  "original": $,
  "result": YOUR_EXPRESSION_HERE
}
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `undefined` | Property doesn't exist | Use `$exists()` check |
| Type error | Wrong data type | Use `$number()`, `$string()` |
| Empty result | Filter matched nothing | Check filter condition |

### Debugging Tips

1. Start simple, build complexity
2. Test each part separately
3. Use `$type()` to check data types
4. Use `$exists()` for optional properties

## Performance Tips

1. Filter early, transform late
2. Avoid repeated calculations
3. Use `$count()` instead of filtering then counting
4. Cache complex expressions in context

## Reference

Full JSONata documentation: https://docs.jsonata.org/
