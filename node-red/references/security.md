# Security Best Practices

Securing your Node-RED installation and flows.

---

## Access Control

### Enable Authentication

Edit `settings.js`:

```javascript
adminAuth: {
    type: "credentials",
    users: [{
        username: "admin",
        password: "$2b$08$...",  // bcrypt hash
        permissions: "*"
    }]
}
```

Generate password hash:

```bash
node -e "console.log(require('bcryptjs').hashSync('your-password', 8))"
```

### Role-Based Access

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

---

## Home Assistant Token Security

### Store Tokens Securely

**Never:**
- Hardcode tokens in function nodes
- Commit tokens to version control
- Share flows with tokens included

**Do:**
- Use environment variables
- Configure in server node (encrypted)
- Regenerate tokens periodically

### Environment Variables

```bash
# Set before starting Node-RED
export HA_TOKEN="your-long-lived-token"
```

Access in flows:

```javascript
const token = env.get("HA_TOKEN");
```

### Token Rotation

1. Create new token in Home Assistant
2. Update Node-RED server config
3. Deploy
4. Delete old token in Home Assistant

---

## Webhook Security

### Require Authentication

```javascript
// In webhook handler
const expectedToken = env.get("WEBHOOK_SECRET");
const providedToken = msg.req.headers["x-webhook-token"];

if (providedToken !== expectedToken) {
    msg.res.sendStatus(401);
    return null;
}

return msg;
```

### Validate Origin

```javascript
const allowedOrigins = ["192.168.1.0/24", "10.0.0.0/8"];
const clientIP = msg.req.ip;

if (!isAllowedIP(clientIP, allowedOrigins)) {
    node.warn(`Blocked request from ${clientIP}`);
    msg.res.sendStatus(403);
    return null;
}
```

### Use HTTPS

Configure in `settings.js`:

```javascript
https: {
    key: fs.readFileSync('/path/to/privkey.pem'),
    cert: fs.readFileSync('/path/to/cert.pem')
}
```

---

## Input Validation

### Sanitize User Input

```javascript
// Validate expected format
const entityId = msg.payload.entity_id;

// Check format
if (!/^[a-z_]+\.[a-z0-9_]+$/.test(entityId)) {
    node.error("Invalid entity ID format", msg);
    return null;
}

// Whitelist allowed entities
const allowed = ["light.living_room", "switch.fan"];
if (!allowed.includes(entityId)) {
    node.error("Entity not in allowed list", msg);
    return null;
}
```

### Prevent Injection

```javascript
// Bad: Direct string interpolation
const query = `SELECT * FROM logs WHERE user = '${msg.payload.user}'`;

// Good: Parameterized or validated
const user = msg.payload.user.replace(/[^a-zA-Z0-9]/g, '');
```

### Validate JSON

```javascript
try {
    const data = JSON.parse(msg.payload);

    // Validate structure
    if (!data.entity_id || !data.action) {
        throw new Error("Missing required fields");
    }

    msg.validated = data;
    return msg;
} catch (e) {
    node.error("Invalid JSON: " + e.message, msg);
    return null;
}
```

---

## Credential Management

### Node-RED Credentials

Stored encrypted in `flows_cred.json`.

- Never commit `flows_cred.json` to git
- Add to `.gitignore`:
  ```
  flows_cred.json
  .config.*.json
  ```

### Credential Secret

Set in `settings.js`:

```javascript
credentialSecret: "your-secret-key"
```

Or via environment:

```bash
export NODE_RED_CREDENTIAL_SECRET="your-secret-key"
```

---

## Network Security

### Firewall Rules

```bash
# Allow only local network
iptables -A INPUT -p tcp --dport 1880 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 1880 -j DROP
```

### Reverse Proxy

Use nginx for SSL termination:

```nginx
server {
    listen 443 ssl;
    server_name nodered.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:1880;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Bind to Localhost

For local-only access:

```javascript
// settings.js
uiHost: "127.0.0.1"
```

---

## Secrets in Flows

### Use Context for Secrets

```javascript
// Store secret in global context (not in flow JSON)
// Set via admin API or startup script
global.set("apiKey", process.env.API_KEY);

// Use in function
const apiKey = global.get("apiKey");
```

### Mask Sensitive Data

```javascript
// Don't log sensitive data
const maskedToken = token.substring(0, 8) + "...";
node.log(`Using token: ${maskedToken}`);
```

---

## Audit Logging

### Log Security Events

```javascript
function logSecurityEvent(event, details) {
    const entry = {
        timestamp: new Date().toISOString(),
        event: event,
        details: details,
        ip: msg.req?.ip
    };

    // Store in context
    let log = flow.get("securityLog") || [];
    log.push(entry);
    if (log.length > 1000) log.shift();
    flow.set("securityLog", log, "file");

    // Alert on suspicious activity
    if (event.includes("failed") || event.includes("blocked")) {
        // Send notification
    }
}

// Usage
logSecurityEvent("auth_failed", { user: msg.payload.user });
logSecurityEvent("webhook_blocked", { ip: msg.req.ip });
```

---

## Backup Security

### Encrypt Backups

```bash
# Backup with encryption
tar czf - flows.json flows_cred.json | \
  openssl enc -aes-256-cbc -salt -out backup.tar.gz.enc

# Restore
openssl enc -d -aes-256-cbc -in backup.tar.gz.enc | tar xzf -
```

### Secure Storage

- Store backups in separate location
- Use encrypted storage
- Limit access permissions
- Regular backup rotation

---

## Security Checklist

### Initial Setup

- [ ] Enable authentication
- [ ] Set credential secret
- [ ] Configure HTTPS
- [ ] Restrict network access
- [ ] Set secure file permissions

### Ongoing

- [ ] Regular token rotation
- [ ] Monitor access logs
- [ ] Update Node-RED regularly
- [ ] Review installed nodes
- [ ] Audit flow permissions

### Development

- [ ] Validate all inputs
- [ ] Don't hardcode secrets
- [ ] Use environment variables
- [ ] Sanitize debug output
- [ ] Review before sharing flows

---

## Common Vulnerabilities

| Vulnerability | Risk | Mitigation |
|---------------|------|------------|
| No authentication | Full access | Enable adminAuth |
| HTTP only | Traffic interception | Use HTTPS |
| Exposed port | Internet access | Firewall, VPN |
| Hardcoded tokens | Credential theft | Environment vars |
| Unvalidated input | Injection attacks | Input validation |
| Debug nodes | Data leakage | Disable in production |

---

## Security Updates

### Stay Updated

```bash
# Update Node-RED
npm update -g node-red

# Update nodes
cd ~/.node-red
npm update
```

### Monitor Advisories

- [Node-RED Security](https://nodered.org/docs/security)
- [npm Security Advisories](https://www.npmjs.com/advisories)
- [Home Assistant Security](https://www.home-assistant.io/docs/security/)
