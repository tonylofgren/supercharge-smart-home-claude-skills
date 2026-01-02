# Error Handling

Implementing robust error handling in Node-RED flows.

---

## Catch Node

The Catch node catches errors thrown by nodes in the same flow.

### Basic Setup

```
[Any Node] ---> [Processing] ---> [Output]
      |
      +--> [Catch All] ---> [Error Handler]
```

### Catch Node Configuration

| Option | Description |
|--------|-------------|
| Catch errors from: all nodes | Catches any error in the flow |
| Catch errors from: selected nodes | Only catches from specific nodes |
| Ignore handled errors | Skip errors already caught |

### Error Message Properties

```javascript
// In function node after catch
msg.error.message    // Error message text
msg.error.source.id  // Node ID that threw error
msg.error.source.type // Node type
msg.error.source.name // Node name
```

---

## Throwing Errors

### From Function Node

```javascript
// Throw an error (caught by Catch node)
node.error("Something went wrong", msg);

// Just log without throwing
node.warn("Warning message");
node.log("Info message");
```

### Conditional Errors

```javascript
if (!msg.payload) {
    node.error("Missing payload", msg);
    return null;  // Stop flow
}

if (msg.payload < 0) {
    node.error("Value cannot be negative", msg);
    return null;
}

return msg;
```

---

## Error Handler Patterns

### Log and Continue

```javascript
// In error handler function node
node.warn(`Error: ${msg.error.message} from ${msg.error.source.name}`);

// Optionally send notification
msg.payload = {
    action: "notify.mobile_app",
    data: {
        title: "Node-RED Error",
        message: msg.error.message
    }
};
return msg;
```

### Retry Logic

```javascript
// Track retry attempts
const MAX_RETRIES = 3;
const attempts = (msg._retryCount || 0) + 1;

if (attempts <= MAX_RETRIES) {
    msg._retryCount = attempts;
    node.warn(`Retry ${attempts}/${MAX_RETRIES}`);

    // Delay before retry
    setTimeout(() => {
        node.send(msg);
    }, 1000 * attempts);  // Exponential backoff

    return null;
}

// Max retries reached
node.error("Max retries exceeded", msg);
return null;
```

### Error Recovery

```javascript
// Set default value on error
msg.payload = msg._originalPayload || "default";
msg.recovered = true;
return msg;
```

---

## Status Node

Monitor node status changes for error detection.

### Configuration

| Option | Description |
|--------|-------------|
| Report status from: all nodes | All status changes |
| Report status from: selected | Specific nodes only |

### Status Message

```javascript
// msg structure from Status node
msg.status.text     // Status text
msg.status.fill     // "red", "green", "yellow", "blue", "grey"
msg.status.shape    // "dot", "ring"
msg.status.source.id   // Node ID
msg.status.source.type // Node type
msg.status.source.name // Node name
```

### Monitor for Disconnection

```javascript
// In function after Status node
if (msg.status.fill === "red" ||
    msg.status.text?.includes("disconnect")) {

    msg.payload = {
        action: "notify.mobile_app",
        data: {
            title: "Connection Lost",
            message: `${msg.status.source.name}: ${msg.status.text}`
        }
    };
    return msg;
}
return null;
```

---

## Complete Node

The Complete node triggers when a node has finished processing.

### Use Cases

- Confirm operation completed
- Chain dependent operations
- Audit logging

### Configuration

1. Add Complete node
2. Select target nodes to monitor
3. Wire to downstream processing

---

## Validation Patterns

### Input Validation

```javascript
// Validate before processing
function validate(msg) {
    const errors = [];

    if (!msg.payload) {
        errors.push("Missing payload");
    }

    if (typeof msg.payload !== "object") {
        errors.push("Payload must be an object");
    }

    if (msg.payload && !msg.payload.entity_id) {
        errors.push("Missing entity_id");
    }

    return errors;
}

const errors = validate(msg);
if (errors.length > 0) {
    node.error(errors.join(", "), msg);
    return null;
}

return msg;
```

### Safe Property Access

```javascript
// Using optional chaining
const value = msg.payload?.data?.value;

// With default
const brightness = msg.data?.new_state?.attributes?.brightness ?? 255;

// Check before use
if (!msg.data?.entity_id) {
    node.warn("No entity_id in message");
    return null;
}
```

---

## Service Call Error Handling

### Check Response

```javascript
// After api-call-service node
if (msg.payload === false) {
    node.error("Service call failed", msg);
    return null;
}
return msg;
```

### Timeout Handling

```javascript
// Set a timeout for service response
const timeout = setTimeout(() => {
    node.error("Service call timed out", msg);
    context.set("pending", null);
}, 10000);

context.set("timeout", timeout);

// In completion handler
const timeout = context.get("timeout");
if (timeout) {
    clearTimeout(timeout);
    context.set("timeout", null);
}
```

---

## Flow-Level Error Handling

### Global Error Handler Subflow

Create a subflow that handles errors consistently:

```
[Catch All] --> [Format Error] --> [Log to File]
                     |
                     +--> [Send Notification]
                     |
                     +--> [Update Dashboard]
```

### Error Categories

```javascript
// Categorize errors for different handling
const errorType = categorizeError(msg.error.message);

switch (errorType) {
    case "connection":
        // Attempt reconnect
        return [msg, null, null];

    case "validation":
        // Log and skip
        return [null, msg, null];

    case "critical":
        // Alert immediately
        return [null, null, msg];

    default:
        // Default handling
        return [msg, null, null];
}

function categorizeError(message) {
    if (message.includes("ECONNREFUSED") ||
        message.includes("timeout")) {
        return "connection";
    }
    if (message.includes("validation") ||
        message.includes("invalid")) {
        return "validation";
    }
    if (message.includes("critical") ||
        message.includes("security")) {
        return "critical";
    }
    return "unknown";
}
```

---

## Debugging Errors

### Add Context to Errors

```javascript
try {
    // Operation that might fail
    const result = processData(msg.payload);
    msg.payload = result;
    return msg;
} catch (error) {
    // Add context before throwing
    const context = {
        payload: msg.payload,
        topic: msg.topic,
        timestamp: Date.now()
    };

    node.error(`${error.message} | Context: ${JSON.stringify(context)}`, msg);
    return null;
}
```

### Error Logging Flow

```
[Catch] --> [Add Timestamp] --> [Store in Context] --> [Debug Node]
                                       |
                                       v
                              [Periodic Summary]
```

```javascript
// Store errors for review
let errors = flow.get("errorLog") || [];
errors.push({
    time: new Date().toISOString(),
    message: msg.error.message,
    source: msg.error.source.name
});

// Keep last 100 errors
while (errors.length > 100) {
    errors.shift();
}

flow.set("errorLog", errors);
```

---

## Best Practices

### 1. Fail Early

```javascript
// Validate at the start of processing
if (!isValid(msg)) {
    node.error("Invalid input", msg);
    return null;
}
// Continue with valid data...
```

### 2. Provide Meaningful Messages

```javascript
// Bad
node.error("Error", msg);

// Good
node.error(`Failed to turn on ${msg.entity_id}: ${reason}`, msg);
```

### 3. Use Status Indicators

```javascript
// Show error state on node
node.status({fill: "red", shape: "ring", text: "Error: " + error.message});
```

### 4. Don't Swallow Errors

```javascript
// Bad - error is hidden
try {
    doSomething();
} catch (e) {
    // Nothing
}

// Good - error is handled
try {
    doSomething();
} catch (e) {
    node.warn("Operation failed: " + e.message);
    // Take appropriate action
}
```

### 5. Clean Up on Errors

```javascript
// In On Stop tab or error handler
const timeout = context.get("timeout");
if (timeout) clearTimeout(timeout);

const interval = context.get("interval");
if (interval) clearInterval(interval);
```

---

## Recovery Strategies

| Strategy | When to Use |
|----------|-------------|
| Retry with backoff | Transient failures (network) |
| Use cached value | Data unavailable temporarily |
| Skip and continue | Non-critical operations |
| Alert and stop | Critical failures |
| Fallback action | Alternative when primary fails |
