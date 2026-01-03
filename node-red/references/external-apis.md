# External API Integration

Connect Node-RED to external services.

## HTTP Request Node

### Basic Configuration

```json
{
  "type": "http request",
  "method": "GET",
  "url": "https://api.example.com/data",
  "return": "obj"
}
```

### Return Types

| Type | `return` | Use Case |
|------|----------|----------|
| JSON object | `obj` | API responses |
| String | `txt` | Plain text |
| Binary | `bin` | Files, images |

---

## GET Requests

### Simple GET

```javascript
msg.url = "https://api.weather.com/current";
return msg;
```

### With Query Parameters

```javascript
msg.url = "https://api.example.com/search";
msg.payload = {
  q: "temperature",
  city: "Stockholm"
};
return msg;
// Result: https://api.example.com/search?q=temperature&city=Stockholm
```

### Dynamic URL

```javascript
const city = flow.get('city') || 'Stockholm';
msg.url = `https://api.weather.com/forecast/${city}`;
return msg;
```

---

## POST Requests

### JSON Body

```javascript
msg.url = "https://api.example.com/data";
msg.method = "POST";
msg.headers = {
  "Content-Type": "application/json"
};
msg.payload = {
  sensor: "temperature",
  value: 22.5,
  timestamp: Date.now()
};
return msg;
```

### Form Data

```javascript
msg.url = "https://api.example.com/login";
msg.method = "POST";
msg.headers = {
  "Content-Type": "application/x-www-form-urlencoded"
};
msg.payload = "username=admin&password=secret";
return msg;
```

---

## Authentication

### API Key in Header

```javascript
msg.url = "https://api.example.com/data";
msg.headers = {
  "X-API-Key": env.get("API_KEY")
};
return msg;
```

### Bearer Token

```javascript
msg.url = "https://api.example.com/data";
msg.headers = {
  "Authorization": `Bearer ${env.get("ACCESS_TOKEN")}`
};
return msg;
```

### Basic Auth

In http request node:
- Enable "Use basic authentication"
- Set username/password

Or in code:

```javascript
const username = env.get("API_USER");
const password = env.get("API_PASS");
const auth = Buffer.from(`${username}:${password}`).toString('base64');

msg.headers = {
  "Authorization": `Basic ${auth}`
};
return msg;
```

### OAuth 2.0 Flow

```javascript
// Token refresh function
async function refreshToken() {
  const response = await fetch("https://oauth.example.com/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: flow.get("refresh_token"),
      client_id: env.get("CLIENT_ID"),
      client_secret: env.get("CLIENT_SECRET")
    })
  });

  const data = await response.json();
  flow.set("access_token", data.access_token);
  flow.set("refresh_token", data.refresh_token);
  flow.set("token_expires", Date.now() + (data.expires_in * 1000));

  return data.access_token;
}

// Check token before request
let token = flow.get("access_token");
const expires = flow.get("token_expires") || 0;

if (Date.now() > expires - 60000) { // Refresh 1 min early
  token = await refreshToken();
}

msg.headers = {
  "Authorization": `Bearer ${token}`
};

node.send(msg);
node.done();
return null;
```

---

## Response Handling

### Parse Response

```javascript
// After http request node
const data = msg.payload;

// Check status
if (msg.statusCode !== 200) {
  node.error(`API error: ${msg.statusCode}`, msg);
  return null;
}

// Extract data
msg.temperature = data.main.temp;
msg.humidity = data.main.humidity;
return msg;
```

### Error Handling

```javascript
// Check for errors
if (msg.statusCode >= 400) {
  msg.error = {
    status: msg.statusCode,
    message: msg.payload.error || "Unknown error"
  };
  return [null, msg]; // Output 2 for errors
}

return [msg, null]; // Output 1 for success
```

### Rate Limit Handling

```javascript
if (msg.statusCode === 429) {
  // Rate limited - wait and retry
  const retryAfter = parseInt(msg.headers['retry-after']) || 60;
  msg._retryDelay = retryAfter * 1000;
  return [null, msg]; // To retry logic
}

return [msg, null];
```

---

## Common APIs

### Weather API

```javascript
// OpenWeatherMap
const apiKey = env.get("OPENWEATHER_API_KEY");
const city = "Stockholm";

msg.url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;
return msg;
```

Response:

```javascript
const weather = msg.payload;
msg.result = {
  temp: weather.main.temp,
  humidity: weather.main.humidity,
  description: weather.weather[0].description
};
return msg;
```

### Pushover Notifications

```javascript
msg.url = "https://api.pushover.net/1/messages.json";
msg.method = "POST";
msg.headers = { "Content-Type": "application/json" };
msg.payload = {
  token: env.get("PUSHOVER_TOKEN"),
  user: env.get("PUSHOVER_USER"),
  title: msg.title || "Notification",
  message: msg.message,
  priority: msg.priority || 0
};
return msg;
```

### Telegram

```javascript
const botToken = env.get("TELEGRAM_BOT_TOKEN");
const chatId = env.get("TELEGRAM_CHAT_ID");

msg.url = `https://api.telegram.org/bot${botToken}/sendMessage`;
msg.method = "POST";
msg.headers = { "Content-Type": "application/json" };
msg.payload = {
  chat_id: chatId,
  text: msg.message,
  parse_mode: "HTML"
};
return msg;
```

### Slack

```javascript
msg.url = env.get("SLACK_WEBHOOK_URL");
msg.method = "POST";
msg.headers = { "Content-Type": "application/json" };
msg.payload = {
  text: msg.message,
  channel: "#home-automation",
  username: "Node-RED",
  icon_emoji: ":house:"
};
return msg;
```

### Discord

```javascript
msg.url = env.get("DISCORD_WEBHOOK_URL");
msg.method = "POST";
msg.headers = { "Content-Type": "application/json" };
msg.payload = {
  content: msg.message,
  username: "Home Automation",
  embeds: [{
    title: msg.title,
    description: msg.description,
    color: 5814783 // Blue
  }]
};
return msg;
```

---

## Webhooks (Incoming)

### HTTP In Node

```json
{
  "type": "http in",
  "method": "post",
  "url": "/api/webhook"
}
```

### Complete Flow

```
[http in: POST /webhook] → [function: process] → [http response]
```

### Response Handler

```javascript
// Must send response
msg.res.status(200).send({ status: "ok" });
return null;

// Or use http response node with:
msg.payload = { status: "ok" };
msg.statusCode = 200;
return msg;
```

### Webhook with Validation

```javascript
const expectedSecret = env.get("WEBHOOK_SECRET");
const receivedSecret = msg.req.headers['x-webhook-secret'];

if (receivedSecret !== expectedSecret) {
  msg.res.status(401).send({ error: "Unauthorized" });
  return null;
}

// Process webhook
const event = msg.payload.event;
const data = msg.payload.data;

node.log(`Received webhook: ${event}`);

msg.res.status(200).send({ received: true });
return null;
```

---

## Retry Logic

### Simple Retry

```javascript
const maxRetries = 3;
msg._retryCount = (msg._retryCount || 0) + 1;

if (msg.statusCode >= 500 && msg._retryCount <= maxRetries) {
  // Server error - retry with delay
  setTimeout(() => {
    node.send(msg);
  }, 1000 * msg._retryCount);
  node.done();
  return null;
}

return msg;
```

### Exponential Backoff

```javascript
const maxRetries = 5;
const baseDelay = 1000;

msg._retryCount = (msg._retryCount || 0) + 1;

if (msg._retryCount > maxRetries) {
  node.error("Max retries exceeded", msg);
  return null;
}

// Exponential: 1s, 2s, 4s, 8s, 16s
const delay = baseDelay * Math.pow(2, msg._retryCount - 1);

node.status({ fill: "yellow", shape: "ring", text: `Retry ${msg._retryCount}/${maxRetries}` });

setTimeout(() => {
  node.send(msg);
  node.done();
}, delay);

return null;
```

---

## Caching

### Simple Cache

```javascript
const cacheKey = msg.url;
const cacheDuration = 5 * 60 * 1000; // 5 minutes

const cached = flow.get(`cache_${cacheKey}`);
if (cached && Date.now() - cached.time < cacheDuration) {
  msg.payload = cached.data;
  msg.fromCache = true;
  return msg;
}

// Continue to http request node
return msg;
```

### Store in Cache

```javascript
// After http request
const cacheKey = msg.url;
flow.set(`cache_${cacheKey}`, {
  data: msg.payload,
  time: Date.now()
});
return msg;
```

### Cache Invalidation

```javascript
function clearCache(pattern) {
  const keys = flow.keys();
  keys.forEach(key => {
    if (key.startsWith(`cache_${pattern}`)) {
      flow.set(key, undefined);
    }
  });
}

clearCache("https://api.example.com");
```

---

## File Downloads

### Download File

```json
{
  "type": "http request",
  "method": "GET",
  "url": "https://example.com/file.pdf",
  "return": "bin"
}
```

### Save to Disk

```javascript
msg.filename = "/data/downloads/file.pdf";
return msg;
// Connect to file node with "Write" action
```

### Upload File

```javascript
const fs = require('fs');
const FormData = require('form-data');

const form = new FormData();
form.append('file', fs.createReadStream('/data/upload/image.jpg'));
form.append('description', 'Uploaded from Node-RED');

msg.headers = form.getHeaders();
msg.payload = form;
msg.method = "POST";
msg.url = "https://api.example.com/upload";

return msg;
```

---

## Rate Limiting

### Client-Side Rate Limit

```javascript
const minInterval = 1000; // 1 second between requests
const lastRequest = flow.get('lastRequest') || 0;
const now = Date.now();

if (now - lastRequest < minInterval) {
  const waitTime = minInterval - (now - lastRequest);
  setTimeout(() => {
    flow.set('lastRequest', Date.now());
    node.send(msg);
    node.done();
  }, waitTime);
  return null;
}

flow.set('lastRequest', now);
return msg;
```

### Request Queue

```javascript
// Add to queue
let queue = flow.get('requestQueue') || [];
queue.push(msg);
flow.set('requestQueue', queue);

// Process queue at fixed rate
if (!flow.get('queueProcessing')) {
  flow.set('queueProcessing', true);
  processQueue();
}

function processQueue() {
  const queue = flow.get('requestQueue') || [];
  if (queue.length === 0) {
    flow.set('queueProcessing', false);
    return;
  }

  const nextMsg = queue.shift();
  flow.set('requestQueue', queue);
  node.send(nextMsg);

  setTimeout(processQueue, 1000); // 1 request per second
}

node.done();
return null;
```

---

## Debugging

### Log Request/Response

```javascript
// Before request
node.log(`Request: ${msg.method} ${msg.url}`);
if (msg.payload) {
  node.log(`Body: ${JSON.stringify(msg.payload)}`);
}
return msg;

// After response
node.log(`Response: ${msg.statusCode}`);
node.log(`Headers: ${JSON.stringify(msg.headers)}`);
node.log(`Body: ${JSON.stringify(msg.payload)}`);
return msg;
```

### HTTP Request Debug Options

In http request node:
- Enable "Use proxy"
- Point to debugging proxy (Charles, Fiddler)

---

## Quick Reference

### HTTP Methods

| Method | Use Case |
|--------|----------|
| GET | Retrieve data |
| POST | Create/send data |
| PUT | Update (full replace) |
| PATCH | Update (partial) |
| DELETE | Remove |

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Server Error |

### Common Headers

| Header | Purpose |
|--------|---------|
| Content-Type | Request body format |
| Authorization | Auth credentials |
| X-API-Key | API key |
| Accept | Expected response format |

