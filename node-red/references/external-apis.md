# External APIs

Integrating external web services and APIs in Node-RED.

---

## HTTP Request Node

### Basic Configuration

| Setting | Description |
|---------|-------------|
| Method | GET, POST, PUT, DELETE, etc. |
| URL | API endpoint |
| Payload | Request body (for POST/PUT) |
| Return | UTF-8 string, JSON, binary buffer |

### Output Properties

```javascript
msg.payload      // Response body
msg.statusCode   // HTTP status (200, 404, etc.)
msg.headers      // Response headers
msg.responseUrl  // Final URL (after redirects)
```

---

## Common HTTP Methods

### GET Request

```
[Inject] --> [http request: GET] --> [Process Response]

URL: https://api.example.com/data
Method: GET
Return: a parsed JSON object
```

### POST Request

```javascript
// Set payload before http request node
msg.payload = {
    name: "New Item",
    value: 42
};
msg.headers = {
    "Content-Type": "application/json"
};
return msg;
```

### With Query Parameters

```javascript
// Build URL with params
const baseUrl = "https://api.weather.com/forecast";
const params = new URLSearchParams({
    location: "Stockholm",
    units: "metric",
    lang: "en"
});
msg.url = `${baseUrl}?${params}`;
return msg;
```

---

## Authentication

### API Key in Header

```javascript
msg.headers = {
    "Authorization": "Bearer " + env.get("API_KEY"),
    "Content-Type": "application/json"
};
return msg;
```

### API Key in URL

```javascript
const apiKey = env.get("API_KEY");
msg.url = `https://api.example.com/data?api_key=${apiKey}`;
return msg;
```

### Basic Auth

Configure in http request node:
- Enable authentication
- Select "basic authentication"
- Enter username/password

Or manually:

```javascript
const auth = Buffer.from("username:password").toString("base64");
msg.headers = {
    "Authorization": "Basic " + auth
};
return msg;
```

### OAuth 2.0

```javascript
// Token refresh flow
let token = flow.get("accessToken");
const expiry = flow.get("tokenExpiry") || 0;

if (Date.now() > expiry - 60000) {  // Refresh 1 min before expiry
    // Need to refresh token
    msg.refreshToken = true;
    return [null, msg];  // Output 2: Refresh flow
}

msg.headers = {
    "Authorization": "Bearer " + token
};
return [msg, null];  // Output 1: Continue
```

---

## Error Handling

### Check Status Code

```javascript
// After http request node
if (msg.statusCode !== 200) {
    node.warn(`API error: ${msg.statusCode}`);

    if (msg.statusCode === 401) {
        // Unauthorized - refresh token
        return [null, msg];
    } else if (msg.statusCode === 429) {
        // Rate limited - retry later
        return [null, null, msg];
    } else {
        // Other error
        node.error(`API failed: ${msg.statusCode}`, msg);
        return null;
    }
}

return [msg, null, null];
```

### Timeout Handling

Set timeout in http request node properties.

```javascript
// Handle timeout
if (msg.statusCode === undefined) {
    node.warn("Request timed out");
    // Implement retry logic
}
```

### Retry with Backoff

```javascript
const MAX_RETRIES = 3;
const retries = msg._retries || 0;

if (msg.statusCode >= 500 && retries < MAX_RETRIES) {
    msg._retries = retries + 1;
    const delay = Math.pow(2, retries) * 1000;  // Exponential backoff

    setTimeout(() => {
        node.send(msg);
    }, delay);

    return null;
}

if (retries >= MAX_RETRIES) {
    node.error("Max retries exceeded", msg);
}

return msg;
```

---

## Rate Limiting

### Respect API Limits

```javascript
const RATE_LIMIT = 60;  // Requests per minute
const timestamps = flow.get("apiCalls") || [];

// Clean old timestamps
const oneMinuteAgo = Date.now() - 60000;
const recent = timestamps.filter(t => t > oneMinuteAgo);

if (recent.length >= RATE_LIMIT) {
    node.warn("Rate limit reached, queuing request");
    // Queue or delay request
    return null;
}

recent.push(Date.now());
flow.set("apiCalls", recent);
return msg;
```

### Queue Requests

```javascript
// Add to queue
let queue = flow.get("requestQueue") || [];
queue.push(msg);
flow.set("requestQueue", queue);

// Process queue at intervals
if (!flow.get("processingQueue")) {
    flow.set("processingQueue", true);
    processQueue();
}

function processQueue() {
    const queue = flow.get("requestQueue") || [];
    if (queue.length === 0) {
        flow.set("processingQueue", false);
        return;
    }

    const next = queue.shift();
    flow.set("requestQueue", queue);
    node.send(next);

    setTimeout(processQueue, 1000);  // 1 request per second
}
```

---

## Common API Integrations

### Weather API

```javascript
// OpenWeatherMap
const apiKey = env.get("OPENWEATHER_KEY");
const city = "Stockholm";
msg.url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;
return msg;

// Process response
const temp = msg.payload.main.temp;
const description = msg.payload.weather[0].description;
```

### REST API with Pagination

```javascript
// Fetch all pages
let allData = flow.get("allData") || [];
const page = msg._page || 1;

// After response
allData = allData.concat(msg.payload.results);

if (msg.payload.next) {
    msg.url = msg.payload.next;
    msg._page = page + 1;
    flow.set("allData", allData);
    return msg;  // Fetch next page
}

// All pages fetched
msg.payload = allData;
flow.set("allData", []);
return msg;
```

### Webhook Sender

```javascript
// Send data to external webhook
msg.method = "POST";
msg.url = env.get("WEBHOOK_URL");
msg.headers = {
    "Content-Type": "application/json",
    "X-Webhook-Secret": env.get("WEBHOOK_SECRET")
};
msg.payload = {
    event: "state_change",
    entity: msg.data.entity_id,
    state: msg.payload,
    timestamp: new Date().toISOString()
};
return msg;
```

---

## Caching API Responses

### Time-Based Cache

```javascript
const CACHE_TTL = 300000;  // 5 minutes
const cacheKey = msg.url;
const cache = flow.get("apiCache") || {};

if (cache[cacheKey] && Date.now() - cache[cacheKey].time < CACHE_TTL) {
    msg.payload = cache[cacheKey].data;
    msg.cached = true;
    return msg;
}

// After http request, store in cache
cache[cacheKey] = {
    data: msg.payload,
    time: Date.now()
};
flow.set("apiCache", cache);
return msg;
```

### Conditional Requests

```javascript
// Use ETag/Last-Modified for caching
const cache = flow.get("cache") || {};
const cached = cache[msg.url];

if (cached) {
    msg.headers = msg.headers || {};
    if (cached.etag) {
        msg.headers["If-None-Match"] = cached.etag;
    }
    if (cached.lastModified) {
        msg.headers["If-Modified-Since"] = cached.lastModified;
    }
}
return msg;

// After response
if (msg.statusCode === 304) {
    // Not modified, use cached data
    msg.payload = cached.data;
} else {
    // Update cache
    cache[msg.url] = {
        data: msg.payload,
        etag: msg.headers.etag,
        lastModified: msg.headers["last-modified"]
    };
    flow.set("cache", cache);
}
```

---

## Security Best Practices

### Store Credentials Securely

```javascript
// Use environment variables
const apiKey = env.get("API_KEY");

// Or flow context (set via admin)
const apiKey = flow.get("apiCredentials")?.key;
```

### Validate Responses

```javascript
// Verify response structure
if (!msg.payload || !msg.payload.data) {
    node.error("Invalid API response structure", msg);
    return null;
}

// Sanitize data before use
const cleanData = sanitize(msg.payload.data);
```

### HTTPS Only

- Always use HTTPS for external APIs
- Verify SSL certificates (default behavior)
- Only disable SSL verification for testing

---

## Debugging

### Log Requests

```javascript
// Before http request
node.warn(`API Request: ${msg.method || 'GET'} ${msg.url}`);
if (msg.payload) {
    node.warn(`Body: ${JSON.stringify(msg.payload)}`);
}
return msg;
```

### Inspect Response

```javascript
// After http request
node.warn(`Response ${msg.statusCode}: ${JSON.stringify(msg.payload).substring(0, 200)}`);
return msg;
```

### Use Debug Node

Connect debug node after http request to inspect:
- `msg.payload` - Response body
- `msg.statusCode` - HTTP status
- `msg.headers` - Response headers
