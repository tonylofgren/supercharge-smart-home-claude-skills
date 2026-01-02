# JSONata Expressions

JSONata is a query and transformation language for JSON data, built into Node-RED.

---

## Where to Use JSONata

- **Change node**: Set property with JSONata expression
- **Switch node**: Property comparisons
- **Service call nodes**: Data field with JSONata type
- **Template node**: JSONata mode

---

## Basic Syntax

### Accessing Properties

```jsonata
payload              // msg.payload
payload.value        // msg.payload.value
data.entity_id       // msg.data.entity_id
$flowContext("var")  // flow.get("var")
$globalContext("var") // global.get("var")
```

### Safe Navigation

```jsonata
payload.data.value   // Errors if data is undefined
payload.data?.value  // Returns undefined if data is undefined
```

---

## Operators

### Arithmetic

```jsonata
payload + 10         // Addition
payload - 5          // Subtraction
payload * 2          // Multiplication
payload / 4          // Division
payload % 3          // Modulo
```

### Comparison

```jsonata
payload = "on"       // Equals
payload != "off"     // Not equals
payload > 20         // Greater than
payload >= 20        // Greater or equal
payload < 50         // Less than
payload <= 50        // Less or equal
```

### Logical

```jsonata
payload > 10 and payload < 50    // AND
payload = "on" or payload = "off" // OR
not(payload = "unavailable")      // NOT
```

### String Concatenation

```jsonata
"Temperature: " & payload & "°C"
```

---

## Conditional Expressions

### Ternary

```jsonata
payload > 20 ? "warm" : "cold"
```

### Nested Conditions

```jsonata
payload > 30 ? "hot" : payload > 20 ? "warm" : "cold"
```

---

## Array Operations

### Access Elements

```jsonata
payload[0]           // First element
payload[-1]          // Last element
payload[0..2]        // First three elements
```

### Filtering

```jsonata
payload[state = "on"]           // Items where state is "on"
payload[brightness > 50]         // Items with brightness > 50
payload[$.entity_id ~> /light/]  // Items matching regex
```

### Mapping

```jsonata
payload.entity_id                // Extract entity_id from each
payload.({"id": entity_id, "state": state})  // Transform each
```

### Aggregation

```jsonata
$sum(payload.value)              // Sum of values
$average(payload.temperature)    // Average
$min(payload)                    // Minimum
$max(payload)                    // Maximum
$count(payload)                  // Count items
```

---

## Built-in Functions

### String Functions

```jsonata
$string(payload)                 // Convert to string
$length(payload)                 // String length
$substring(payload, 0, 5)        // Substring
$uppercase(payload)              // UPPERCASE
$lowercase(payload)              // lowercase
$trim(payload)                   // Remove whitespace
$split(payload, ",")             // Split into array
$join(payload, ", ")             // Join array to string
$replace(payload, "old", "new")  // Replace text
$contains(payload, "text")       // Contains check
$match(payload, /pattern/)       // Regex match
```

### Numeric Functions

```jsonata
$number(payload)                 // Convert to number
$abs(payload)                    // Absolute value
$floor(payload)                  // Round down
$ceil(payload)                   // Round up
$round(payload, 2)               // Round to decimals
$power(payload, 2)               // Exponent
$sqrt(payload)                   // Square root
```

### Array Functions

```jsonata
$count(payload)                  // Array length
$sum(payload)                    // Sum values
$average(payload)                // Average
$append(arr1, arr2)              // Concatenate arrays
$reverse(payload)                // Reverse order
$sort(payload)                   // Sort ascending
$distinct(payload)               // Unique values
$shuffle(payload)                // Random order
```

### Object Functions

```jsonata
$keys(payload)                   // Get keys
$lookup(payload, "key")          // Get value by key
$merge([obj1, obj2])             // Merge objects
$spread(payload)                 // Object to key-value pairs
$type(payload)                   // Get type
```

### Date/Time Functions

```jsonata
$now()                           // Current timestamp (ms)
$millis()                        // Current time in ms
$toMillis("2024-01-15")          // Parse date to ms
$fromMillis(1234567890)          // Ms to ISO string
```

---

## Home Assistant Examples

### Get Entity State

```jsonata
$globalContext("homeassistant").homeAssistant.states["light.room"].state
```

### Build Service Data

```jsonata
{
    "brightness_pct": payload > 50 ? 100 : 50,
    "transition": 2
}
```

### Filter Entities by Domain

```jsonata
$keys($globalContext("homeassistant").homeAssistant.states)[$ ~> /^light\./]
```

### Dynamic Entity Selection

```jsonata
{
    "entity_id": payload.lights[state = "on"].entity_id
}
```

### Temperature Conversion

```jsonata
{
    "celsius": payload,
    "fahrenheit": (payload * 9/5) + 32
}
```

---

## Common Patterns

### Default Values

```jsonata
payload ? payload : "default"
// Or using nullish coalescing
payload ?? "default"
```

### Conditional Object Properties

```jsonata
{
    "brightness": brightness,
    "transition": transition ? transition : 1
}
```

### Build Array from Values

```jsonata
[
    entity_id,
    second_entity
][$ != null]  // Filter out nulls
```

### Transform State Data

```jsonata
{
    "entity": data.entity_id,
    "from": data.old_state.state,
    "to": data.new_state.state,
    "changed": data.old_state.state != data.new_state.state
}
```

### Extract Numbers from Strings

```jsonata
$number($match(payload, /\d+/).match)
```

---

## Switch Node Examples

### State Comparison

```jsonata
// Property: payload
// Condition: JSONata expression
payload = "on"
```

### Numeric Range

```jsonata
payload >= 20 and payload < 25
```

### Entity Domain Check

```jsonata
$contains(data.entity_id, "light.")
```

### Time-Based

```jsonata
$number($substring($fromMillis($now()), 11, 2)) >= 22
// Check if hour >= 22
```

---

## Service Call Data Examples

### Dynamic Brightness

```jsonata
{
    "brightness_pct": $round(payload * 100),
    "transition": 2
}
```

### Conditional Color Temperature

```jsonata
{
    "color_temp": $number($substring($fromMillis($now()), 11, 2)) < 18 ? 300 : 400
}
```

### Multiple Entities

```jsonata
{
    "entity_id": [
        "light.living_room",
        "light.kitchen"
    ][payload.rooms ~> /$]
}
```

---

## Debugging JSONata

### Use Change Node

1. Add a Change node
2. Set `msg.debug` to JSONata expression
3. Wire to Debug node
4. Check output

### Online Tester

Use [try.jsonata.org](https://try.jsonata.org/) to test expressions with sample data.

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `undefined` | Property doesn't exist | Use `?.` safe navigation |
| `T1005` | Cannot navigate into non-object | Check data structure |
| `T2001` | Wrong argument type | Use type conversion `$string()`, `$number()` |

---

## Performance Notes

1. JSONata expressions are compiled and cached
2. Complex expressions may be slower than function nodes
3. Avoid repeated global context lookups in loops
4. Use function nodes for very complex transformations
