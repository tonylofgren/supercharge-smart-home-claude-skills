# Security in Node-RED

Protect your Node-RED installation and automations.

## Authentication

### Admin Authentication

In `settings.js`:

```javascript
adminAuth: {
  type: "credentials",
  users: [{
    username: "admin",
    password: "$2b$08$...", // bcrypt hash
    permissions: "*"
  }]
}
```

Generate password hash:

```bash
node -e "console.log(require('bcryptjs').hashSync('your-password', 8))"
```

### Multiple Users

```javascript
adminAuth: {
  type: "credentials",
  users: [
    {
      username: "admin",
      password: "$2b$...",
      permissions: "*"
    },
    {
      username: "viewer",
      password: "$2b$...",
      permissions: "read"
    }
  ]
}
```

### Permission Types

| Permission | Access |
|------------|--------|
| `*` | Full access |
| `read` | View only |
| Custom | Fine-grained (advanced) |

---

## HTTPS

### Enable HTTPS

In `settings.js`:

```javascript
https: {
  key: require("fs").readFileSync('/path/to/privkey.pem'),
  cert: require("fs").readFileSync('/path/to/cert.pem')
}
```

### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d nodered.yourdomain.com

# Certificate location
# /etc/letsencrypt/live/nodered.yourdomain.com/
```

### Self-Signed Certificate

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

---

## Webhook Security

### Secret Tokens

In webhook node, enable authentication:

```
Authentication: None | Basic | Bearer Token
```

### Bearer Token Validation

```javascript
// In function node after webhook
const authHeader = msg.req.headers.authorization;
const expectedToken = env.get("WEBHOOK_TOKEN");

if (!authHeader || authHeader !== `Bearer ${expectedToken}`) {
  msg.res.sendStatus(401);
  return null;
}

return msg;
```

### IP Whitelisting

```javascript
const allowedIPs = ["192.168.1.100", "10.0.0.50"];
const clientIP = msg.req.ip || msg.req.connection.remoteAddress;

if (!allowedIPs.includes(clientIP)) {
  node.warn(`Blocked request from ${clientIP}`);
  msg.res.sendStatus(403);
  return null;
}

return msg;
```

### HMAC Signature Validation

For webhooks that sign payloads (like GitHub):

```javascript
const crypto = require('crypto');
const secret = env.get("WEBHOOK_SECRET");
const signature = msg.req.headers['x-hub-signature-256'];
const payload = JSON.stringify(msg.payload);

const hmac = crypto.createHmac('sha256', secret);
hmac.update(payload);
const expectedSignature = 'sha256=' + hmac.digest('hex');

if (signature !== expectedSignature) {
  node.error("Invalid webhook signature");
  msg.res.sendStatus(401);
  return null;
}

return msg;
```

---

## Credentials

### Node-RED Credential Storage

Credentials stored encrypted in `flows_cred.json`.

Set encryption key in `settings.js`:

```javascript
credentialSecret: "your-very-long-secret-key-here"
```

### Environment Variables

Never hardcode secrets:

```javascript
// BAD - hardcoded
const apiKey = "sk-abc123...";

// GOOD - from environment
const apiKey = env.get("API_KEY");
```

Set in environment:

```bash
# Docker
docker run -e API_KEY=sk-abc123 nodered/node-red

# systemd
Environment=API_KEY=sk-abc123
```

### Home Assistant Secrets

In HA configuration:

```yaml
# secrets.yaml
node_red_webhook_token: "your-secret-token"

# configuration.yaml
automation:
  - alias: "Webhook trigger"
    trigger:
      - platform: webhook
        webhook_id: !secret node_red_webhook_token
```

---

## Network Security

### Binding to Localhost

In `settings.js`:

```javascript
uiHost: "127.0.0.1"  // Only local access
```

### Reverse Proxy

Use nginx for external access:

```nginx
server {
    listen 443 ssl;
    server_name nodered.example.com;

    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    location / {
        proxy_pass http://127.0.0.1:1880;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules

```bash
# Allow only local network
sudo ufw allow from 192.168.1.0/24 to any port 1880

# Deny all external
sudo ufw deny 1880
```

---

## Home Assistant Integration Security

### Long-Lived Access Token

1. Go to HA Profile → Long-Lived Access Tokens
2. Create token with descriptive name
3. Store securely (not in flows)

### Token Best Practices

| Practice | Why |
|----------|-----|
| One token per integration | Easier to revoke |
| Descriptive names | Know what uses it |
| Regular rotation | Limit exposure time |
| Monitor usage | Detect abuse |

### Minimal Permissions

If using HA user accounts:

- Create dedicated Node-RED user
- Limit to needed entities only
- Use entity filters in HA

---

## Input Validation

### Validate Webhook Payloads

```javascript
function validatePayload(payload) {
  // Required fields
  if (!payload.entity_id) {
    return { valid: false, error: "Missing entity_id" };
  }

  // Type validation
  if (typeof payload.brightness !== 'number') {
    return { valid: false, error: "brightness must be number" };
  }

  // Range validation
  if (payload.brightness < 0 || payload.brightness > 100) {
    return { valid: false, error: "brightness must be 0-100" };
  }

  // Entity ID format
  if (!/^[a-z_]+\.[a-z0-9_]+$/.test(payload.entity_id)) {
    return { valid: false, error: "Invalid entity_id format" };
  }

  return { valid: true };
}

const result = validatePayload(msg.payload);
if (!result.valid) {
  node.error(result.error, msg);
  return null;
}

return msg;
```

### Sanitize Entity IDs

```javascript
// Prevent injection
function sanitizeEntityId(id) {
  return id.replace(/[^a-z0-9_.]/gi, '');
}

const safeId = sanitizeEntityId(msg.payload.entity_id);
```

### Rate Limiting

```javascript
const maxRequests = 10;
const windowMs = 60000; // 1 minute

const clientIP = msg.req.ip;
let requests = flow.get(`rateLimit_${clientIP}`) || [];
const now = Date.now();

// Remove old requests
requests = requests.filter(t => now - t < windowMs);

if (requests.length >= maxRequests) {
  msg.res.status(429).send("Too many requests");
  return null;
}

requests.push(now);
flow.set(`rateLimit_${clientIP}`, requests);

return msg;
```

---

## Logging and Monitoring

### Security Event Logging

```javascript
function logSecurityEvent(event, details) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    event: event,
    details: details
  };

  // Store in context
  let securityLog = flow.get('securityLog') || [];
  securityLog.push(logEntry);

  // Keep last 1000 entries
  if (securityLog.length > 1000) {
    securityLog = securityLog.slice(-1000);
  }

  flow.set('securityLog', securityLog);

  // Also log to debug
  node.warn(`SECURITY: ${event} - ${JSON.stringify(details)}`);
}

// Usage
logSecurityEvent("AUTH_FAILURE", {
  ip: msg.req.ip,
  path: msg.req.path
});
```

### Failed Authentication Alerts

```javascript
const failures = flow.get('authFailures') || [];
const clientIP = msg.req.ip;
const now = Date.now();

failures.push({ ip: clientIP, time: now });

// Keep last hour
const oneHourAgo = now - (60 * 60 * 1000);
const recentFailures = failures.filter(f => f.time > oneHourAgo);
flow.set('authFailures', recentFailures);

// Count failures from this IP
const ipFailures = recentFailures.filter(f => f.ip === clientIP).length;

if (ipFailures >= 5) {
  // Alert on multiple failures
  msg.alert = {
    title: "Security Alert",
    message: `${ipFailures} failed auth attempts from ${clientIP}`
  };
  return [null, msg]; // Output 2 for alerts
}

return null;
```

---

## Node Security

### Dangerous Nodes

Use with caution:

| Node | Risk | Mitigation |
|------|------|------------|
| Command runner nodes | Shell command execution | Validate all inputs |
| `file` | File system access | Restrict paths |
| `http request` | Network access | Whitelist URLs |
| `function` | Code execution | Review carefully |

### Command Runner Safety

```javascript
// NEVER pass user input directly to shell commands
// Command injection risk!

// Instead, validate input first
const allowedCommands = ['status', 'restart', 'stop'];
if (!allowedCommands.includes(msg.payload)) {
  return null;
}
```

### File Path Validation

```javascript
const path = require('path');
const baseDir = '/data/nodered';

// Prevent directory traversal
const requestedPath = msg.filename;
const resolvedPath = path.resolve(baseDir, requestedPath);

if (!resolvedPath.startsWith(baseDir)) {
  node.error("Path traversal attempt blocked");
  return null;
}

msg.filename = resolvedPath;
return msg;
```

---

## Docker Security

### Non-Root User

```dockerfile
# Node-RED Docker already runs as non-root
USER node-red
```

### Read-Only Filesystem

```yaml
# docker-compose.yml
services:
  nodered:
    image: nodered/node-red
    read_only: true
    tmpfs:
      - /tmp
    volumes:
      - ./data:/data
```

### Resource Limits

```yaml
services:
  nodered:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

### Network Isolation

```yaml
networks:
  internal:
    internal: true  # No external access

services:
  nodered:
    networks:
      - internal
```

---

## Backup Security

### Encrypted Backups

```bash
# Backup with encryption
tar czf - /data/nodered | openssl enc -aes-256-cbc -salt -out backup.tar.gz.enc

# Restore
openssl enc -d -aes-256-cbc -in backup.tar.gz.enc | tar xzf -
```

### Exclude Credentials

```bash
# Backup flows without credentials
cp flows.json flows-backup.json
# Credentials in separate file: flows_cred.json
```

---

## Security Checklist

### Initial Setup

- [ ] Enable adminAuth
- [ ] Set strong credentialSecret
- [ ] Enable HTTPS
- [ ] Bind to localhost or use reverse proxy
- [ ] Configure firewall

### Webhooks

- [ ] Use authentication (Bearer/Basic)
- [ ] Validate all input
- [ ] Implement rate limiting
- [ ] Log access attempts

### Ongoing

- [ ] Keep Node-RED updated
- [ ] Review installed nodes
- [ ] Rotate tokens regularly
- [ ] Monitor security logs
- [ ] Backup encrypted

### Code Review

- [ ] No hardcoded secrets
- [ ] Input validation on all external data
- [ ] Proper error handling (no info leaks)
- [ ] Principle of least privilege

