# Home Assistant Setup for Node-RED

## Table of Contents
- [Installation Options](#installation-options)
- [Home Assistant Addon](#home-assistant-addon)
- [External Node-RED](#external-node-red)
- [Access Token Setup](#access-token-setup)
- [Server Configuration](#server-configuration)
- [Connection Troubleshooting](#connection-troubleshooting)

---

## Installation Options

### Comparison

| Feature | HA Addon | External/Docker |
|---------|----------|-----------------|
| **Setup** | One-click | Manual config |
| **Updates** | Automatic | Manual |
| **URL Config** | Automatic | Manual |
| **Authentication** | Automatic | Token required |
| **Resources** | Shared with HA | Separate |
| **Persistence** | Managed by HA | Self-managed |

### Which to Choose?

**Use HA Addon if:**
- Running Home Assistant OS or Supervised
- Want simplest setup
- Don't need advanced Node.js configuration

**Use External if:**
- Running HA Container/Core
- Need more resources for complex flows
- Want isolation from HA
- Need specific Node.js version

---

## Home Assistant Addon

### Installation

1. **Navigate to Add-ons:**
   ```
   Settings → Add-ons → Add-on Store
   ```

2. **Find Node-RED:**
   - Search for "Node-RED"
   - Click on "Node-RED"

3. **Install:**
   - Click "Install"
   - Wait for installation

4. **Configure (optional):**
   ```yaml
   # Addon Configuration
   credential_secret: your-secret-phrase
   theme: monaco-dark
   http_node:
     username: ""
     password: ""
   http_static:
     username: ""
     password: ""
   ssl: false
   ```

5. **Start:**
   - Toggle "Start on boot"
   - Click "Start"

6. **Access:**
   - Click "Open Web UI"
   - Or navigate to: `http://homeassistant.local:1880`

### Addon Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `credential_secret` | Encryption key for credentials | Random |
| `theme` | Editor theme | monaco |
| `ssl` | Enable HTTPS | false |
| `certfile` | SSL certificate file | fullchain.pem |
| `keyfile` | SSL key file | privkey.pem |

### Network Settings

```yaml
# For external access, enable host network
# In addon configuration
network:
  1880/tcp: 1880
```

---

## External Node-RED

### Docker Installation

```yaml
# docker-compose.yml
version: '3'
services:
  node-red:
    image: nodered/node-red:latest
    container_name: node-red
    restart: unless-stopped
    ports:
      - "1880:1880"
    volumes:
      - ./node-red-data:/data
    environment:
      - TZ=Europe/Stockholm
```

### Manual Installation

```bash
# Install Node.js (v18+)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install Node-RED globally
sudo npm install -g --unsafe-perm node-red

# Run Node-RED
node-red
```

### Install HA Nodes

```bash
# Via npm (in Node-RED user directory)
cd ~/.node-red
npm install node-red-contrib-home-assistant-websocket

# Or via Palette Manager in editor
# Menu → Manage Palette → Install
# Search: node-red-contrib-home-assistant-websocket
```

---

## Access Token Setup

### Creating a Long-Lived Token

1. **Open Profile:**
   - Click your username (bottom left)
   - Or navigate to: `/profile`

2. **Scroll to "Long-Lived Access Tokens"**

3. **Create Token:**
   - Click "Create Token"
   - Enter a name: "Node-RED"
   - Click "OK"

4. **Copy Token:**
   - **IMPORTANT:** Copy immediately - shown only once
   - Store securely

### Token Requirements

| Requirement | Reason |
|-------------|--------|
| **Administrator account** | Full API access |
| **Don't share** | Security |
| **Store securely** | Credential protection |
| **Regenerate if exposed** | Security breach |

### Token Best Practices

```
DO:
✓ Create dedicated token for Node-RED
✓ Name it descriptively ("Node-RED Production")
✓ Regenerate periodically
✓ Delete unused tokens

DON'T:
✗ Share token in flows
✗ Commit to version control
✗ Use same token for multiple services
✗ Use personal account for automation
```

---

## Server Configuration

### Adding Server Node

1. **Drag any HA node to workspace**
2. **Double-click to edit**
3. **Click pencil icon next to "Server"**
4. **Configure connection**

### Addon Configuration

```javascript
{
  "name": "Home Assistant",
  "addon": true,  // CRITICAL: Enable this
  // Other settings will auto-configure
}
```

### External Configuration

```javascript
{
  "name": "Home Assistant",
  "addon": false,
  "host": "http://192.168.1.100",  // Or homeassistant.local
  "port": "8123",
  "accessToken": "eyJ0...",  // Your long-lived token

  // Advanced options
  "rejectUnauthorizedCerts": true,
  "connectionDelay": true,
  "cacheJson": true,
  "heartbeat": false,
  "heartbeatInterval": 30
}
```

### Connection Options

| Option | Description | Default |
|--------|-------------|---------|
| `name` | Display name | Home Assistant |
| `addon` | Running as addon | false |
| `host` | HA URL | http://supervisor/core |
| `port` | HA port | 8123 |
| `accessToken` | Long-lived token | - |
| `rejectUnauthorizedCerts` | Validate SSL | true |
| `connectionDelay` | Wait before connecting | true |
| `cacheJson` | Cache autocomplete | true |
| `heartbeat` | Enable heartbeat | false |
| `heartbeatInterval` | Heartbeat seconds | 30 |

### Registry Options

```javascript
{
  // Enable entity registries for autocomplete
  "areaRegistry": true,
  "deviceRegistry": true,
  "entityRegistry": true,

  // Status display format
  "statusSeparator": ":",
  "statusYear": "hidden",
  "statusMonth": "short",
  "statusDay": "numeric",
  "statusHourCycle": "h23",

  // Global context
  "enableGlobalContextStore": true
}
```

---

## Connection Troubleshooting

### Common Issues

#### "Connection Failed"

**Addon Setup:**
```javascript
// Ensure addon: true is set
{
  "addon": true
}
// URL will be: http://supervisor/core
```

**External Setup:**
```javascript
// Check URL format
{
  "host": "http://192.168.1.100",  // Include http://
  "port": "8123"
}
```

#### "Authentication Failed"

```
1. Verify token is from administrator account
2. Check token hasn't expired
3. Regenerate token if in doubt
4. Ensure no whitespace in token field
```

#### "Connection Lost After Restart"

```javascript
// Enable connection delay
{
  "connectionDelay": true
}

// In addon config, wait for HA to fully start
```

#### "Entities Not Found"

```
1. Wait for HA to fully load entities
2. Check entity ID spelling
3. Clear autocomplete cache:
   - Uncheck "Cache Autocomplete Results"
   - Deploy
   - Recheck and deploy again
```

### Checking Connection Status

**Via Node Status:**
```
┌─────────────┐
│ HA Server   │
│ ● connected │  ← Green dot = connected
└─────────────┘

┌─────────────┐
│ HA Server   │
│ ○ disconnected │  ← Red ring = disconnected
└─────────────┘
```

**Via Debug:**
```javascript
// Add function node to check
const server = global.get("homeassistant").homeAssistant;
msg.payload = {
  connected: server.websocket.readyState === 1,
  entities: Object.keys(server.states).length
};
return msg;
```

### Network Configuration

#### Firewall Rules

```bash
# Allow Node-RED port
sudo ufw allow 1880/tcp

# Allow WebSocket connections (if external)
sudo ufw allow 8123/tcp
```

#### Proxy Configuration

```javascript
// Behind reverse proxy
{
  "host": "https://ha.yourdomain.com",
  "port": "443",
  "rejectUnauthorizedCerts": true
}
```

#### Docker Network

```yaml
# If HA and Node-RED in Docker
networks:
  home-automation:
    driver: bridge

# In HA container
networks:
  - home-automation

# In Node-RED container
networks:
  - home-automation

# Use container name as host
# host: "http://homeassistant:8123"
```

---

## Verifying Setup

### Test Flow

```json
[
  {
    "id": "inject",
    "type": "inject",
    "name": "Test",
    "payload": "",
    "wires": [["get_state"]]
  },
  {
    "id": "get_state",
    "type": "api-current-state",
    "name": "Get Sun State",
    "entityId": "sun.sun",
    "wires": [["debug"]]
  },
  {
    "id": "debug",
    "type": "debug",
    "name": "Output",
    "active": true,
    "complete": "true"
  }
]
```

### Expected Output

```javascript
{
  _msgid: "abc123",
  payload: "above_horizon",  // or "below_horizon"
  data: {
    entity_id: "sun.sun",
    state: "above_horizon",
    attributes: {
      next_dawn: "2024-01-15T06:30:00+00:00",
      // ... more attributes
    }
  }
}
```

---

## Related References

- [HA Trigger Nodes](ha-trigger-nodes.md) - State change triggers
- [HA Action Nodes](ha-action-nodes.md) - Service calls
- [Troubleshooting](troubleshooting.md) - Common issues
