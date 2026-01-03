# Home Assistant + Node-RED Setup

Installation and configuration guide.

## Installation Options

### Option 1: Home Assistant Add-on (Recommended)

If running Home Assistant OS or Supervised:

1. Go to **Settings → Add-ons → Add-on Store**
2. Search for "Node-RED"
3. Install the official Node-RED add-on
4. Configure credentials in add-on configuration
5. Start the add-on

**Advantages:**
- Automatic HA connection
- SSL handled automatically
- Integrated with HA backups
- Access to Supervisor API

### Option 2: External Node-RED

For Docker or standalone installations:

1. Install Node-RED:
   ```bash
   npm install -g node-red
   ```

2. Install the HA nodes:
   ```bash
   cd ~/.node-red
   npm install node-red-contrib-home-assistant-websocket
   ```

3. Create a Long-Lived Access Token in HA:
   - Profile → Long-Lived Access Tokens → Create Token
   - Copy the token (shown only once!)

4. Configure the Server node in Node-RED with:
   - Base URL: `http://homeassistant.local:8123`
   - Access Token: Your long-lived token

## First-Time Configuration

### Server Node Setup

1. Drag any HA node to the canvas
2. Double-click to open configuration
3. Click the pencil icon next to "Server"
4. Configure:

| Field | Add-on Value | External Value |
|-------|-------------|----------------|
| Name | Home Assistant | Home Assistant |
| Base URL | `http://supervisor/core` | `http://your-ha-ip:8123` |
| Access Token | (auto-filled) | Your long-lived token |

### Connection Verification

After configuration:
1. Deploy the flow
2. Check the node status (should show "connected")
3. If disconnected, check:
   - Base URL is correct
   - Access token is valid
   - Network connectivity

## Entity Nodes Setup (Optional)

Entity nodes (sensor, binary_sensor, switch, etc.) require additional integration:

### Install node-red Integration

1. Add HACS if not already installed
2. In HACS, search for "Node-RED"
3. Install "Node-RED Companion"
4. Restart Home Assistant
5. Go to Settings → Devices & Services
6. Click "Add Integration"
7. Search for "Node-RED"
8. Complete setup

**Without this integration, entity nodes will not work!**

## Docker Compose Example

```yaml
version: '3'
services:
  node-red:
    image: nodered/node-red:latest
    container_name: node-red
    environment:
      - TZ=Europe/Stockholm
    ports:
      - "1880:1880"
    volumes:
      - ./node-red-data:/data
    restart: unless-stopped
```

## Security Considerations

### Access Token Security

- Store tokens in environment variables, not flow JSON
- Use credential nodes when possible
- Rotate tokens periodically
- Never commit tokens to version control

### Network Security

- Use HTTPS when possible
- Consider VPN for external access
- Limit network exposure
- Use authentication on Node-RED

### Securing Node-RED

In `settings.js`:

```javascript
module.exports = {
  adminAuth: {
    type: "credentials",
    users: [{
      username: "admin",
      password: "$2b$08$...", // bcrypt hash
      permissions: "*"
    }]
  }
}
```

Generate password hash:
```bash
node-red admin hash-pw
```

## Common Connection Issues

### "Error: connect ECONNREFUSED"

- Check Base URL is correct
- Verify HA is running
- Check network connectivity
- Firewall blocking connection

### "401 Unauthorized"

- Access token is invalid or expired
- Token was revoked
- Generate a new token

### "WebSocket connection failed"

- Check if HA is accessible via WebSocket
- Verify SSL/TLS settings match
- Check for proxy configuration issues

### Entity Nodes Show "Error"

- node-red integration not installed
- Entity config not properly set
- HA restart required after integration install

## Environment Variables

For Docker/external installations, set via environment:

```bash
export NODE_RED_HA_BASE_URL="http://homeassistant.local:8123"
export NODE_RED_HA_TOKEN="your-long-lived-access-token"
```

Access in function nodes:
```javascript
const baseUrl = env.get("NODE_RED_HA_BASE_URL");
```

## Backup and Restore

### Add-on Backups

Included in Home Assistant backups automatically.

### External Node-RED

Backup the following:
- `~/.node-red/flows.json` - Your flows
- `~/.node-red/flows_cred.json` - Encrypted credentials
- `~/.node-red/settings.js` - Configuration
- `~/.node-red/package.json` - Installed nodes

### Migrating Flows

1. Export flows: Menu → Export → Download
2. Import in new instance: Menu → Import
3. Reconfigure server nodes (tokens don't transfer)
4. Update entity IDs if different HA instance

## Version Compatibility

| node-red-contrib-home-assistant-websocket | Node-RED | Home Assistant |
|-------------------------------------------|----------|----------------|
| 0.65.x | 3.0+ | 2024.1+ |
| 0.60.x | 2.2+ | 2023.1+ |
| 0.50.x | 2.0+ | 2022.1+ |

Always check the [GitHub releases](https://github.com/zachowj/node-red-contrib-home-assistant-websocket/releases) for compatibility notes.
