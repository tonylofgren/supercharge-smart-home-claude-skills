# Node-RED Installation Guide

Complete setup for Node-RED with Home Assistant integration.

## Installation Methods

### Method 1: Home Assistant Add-on (Recommended)

Best for most users. Runs inside Home Assistant.

1. Go to **Settings → Add-ons → Add-on Store**
2. Search for "Node-RED"
3. Click **Install**
4. Enable **Start on boot** and **Watchdog**
5. Click **Start**
6. Access via sidebar or http://homeassistant.local:1880

Configuration options in add-on settings:
```yaml
credential_secret: your-secret-key
dark_mode: true
http_node:
  username: admin
  password: secure-password
ssl: false
```

### Method 2: Docker

For advanced users or external servers.

```yaml
# docker-compose.yml
version: '3'
services:
  nodered:
    image: nodered/node-red:latest
    container_name: nodered
    restart: unless-stopped
    ports:
      - "1880:1880"
    volumes:
      - ./data:/data
    environment:
      - TZ=Europe/Stockholm
```

Run:
```bash
docker-compose up -d
```

### Method 3: Native Installation

For Linux servers without Docker.

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Node-RED
sudo npm install -g --unsafe-perm node-red

# Run
node-red
```

---

## Home Assistant Integration

### Install node-red-contrib-home-assistant-websocket

In Node-RED:

1. Menu → **Manage palette**
2. **Install** tab
3. Search: `node-red-contrib-home-assistant-websocket`
4. Click **Install**

Or via command line:
```bash
cd ~/.node-red
npm install node-red-contrib-home-assistant-websocket
```

### Create Access Token

1. In Home Assistant, click your profile (bottom left)
2. Scroll to **Long-Lived Access Tokens**
3. Click **Create Token**
4. Name: `Node-RED`
5. Copy the token (shown only once!)

### Configure Server

In Node-RED:

1. Drag any HA node to canvas
2. Double-click to edit
3. Click pencil icon next to **Server**
4. Fill in:
   - **Base URL**: `http://homeassistant.local:8123`
   - **Access Token**: paste your token
5. Click **Add** then **Done**
6. **Deploy**

### Verify Connection

1. Check server node shows green "connected" status
2. Drag a `trigger-state` node
3. Entity dropdown should populate with your entities

---

## Docker with Home Assistant

### Same Network

```yaml
version: '3'
services:
  nodered:
    image: nodered/node-red:latest
    container_name: nodered
    restart: unless-stopped
    ports:
      - "1880:1880"
    volumes:
      - ./data:/data
    environment:
      - TZ=Europe/Stockholm
    networks:
      - homeassistant

networks:
  homeassistant:
    external: true
```

Base URL: `http://homeassistant:8123`

### Docker Compose with HA

```yaml
version: '3'
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: homeassistant
    restart: unless-stopped
    volumes:
      - ./ha-config:/config
    network_mode: host

  nodered:
    image: nodered/node-red:latest
    container_name: nodered
    restart: unless-stopped
    ports:
      - "1880:1880"
    volumes:
      - ./nodered-data:/data
    environment:
      - TZ=Europe/Stockholm
```

---

## Configuration

### settings.js

Key settings for `~/.node-red/settings.js`:

```javascript
module.exports = {
  // Flow file
  flowFile: 'flows.json',

  // User directory
  userDir: '/data',

  // Credential encryption key
  credentialSecret: "your-very-long-secret-key",

  // Admin authentication
  adminAuth: {
    type: "credentials",
    users: [{
      username: "admin",
      password: "$2b$08$...", // bcrypt hash
      permissions: "*"
    }]
  },

  // Logging
  logging: {
    console: {
      level: "info",
      metrics: false,
      audit: false
    }
  },

  // Editor settings
  editorTheme: {
    projects: {
      enabled: false
    }
  }
};
```

### Generate Password Hash

```bash
node -e "console.log(require('bcryptjs').hashSync('your-password', 8))"
```

### Enable Projects

In settings.js:
```javascript
editorTheme: {
  projects: {
    enabled: true
  }
}
```

---

## TLS/SSL

### With Let's Encrypt

```javascript
// settings.js
https: {
  key: require("fs").readFileSync('/etc/letsencrypt/live/domain.com/privkey.pem'),
  cert: require("fs").readFileSync('/etc/letsencrypt/live/domain.com/fullchain.pem')
},
requireHttps: true
```

### Self-Signed

```bash
# Generate certificate
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=nodered"

# Move to Node-RED directory
mv *.pem ~/.node-red/
```

```javascript
// settings.js
https: {
  key: require("fs").readFileSync('/data/key.pem'),
  cert: require("fs").readFileSync('/data/cert.pem')
}
```

---

## Troubleshooting Installation

### Can't Find Add-on

- Enable **Advanced Mode** in HA profile
- Check if Supervisor is running
- Try refreshing add-on store

### Node-RED Won't Start

Check logs:
```bash
# Docker
docker logs nodered

# Native
journalctl -u nodered
```

Common issues:
- Port 1880 already in use
- Permission issues on data directory
- Node.js version incompatible

### Connection to HA Failed

1. Verify HA is accessible from Node-RED host
2. Check token hasn't expired
3. Confirm URL includes port (`:8123`)
4. For Docker: verify network connectivity

### Palette Install Fails

```bash
# Clear npm cache
cd ~/.node-red
npm cache clean --force

# Retry install
npm install node-red-contrib-home-assistant-websocket
```

---

## Backup and Restore

### What to Back Up

| Item | Location | Purpose |
|------|----------|---------|
| `flows.json` | Data dir | Your flows |
| `flows_cred.json` | Data dir | Encrypted credentials |
| `settings.js` | Data dir | Configuration |
| `package.json` | Data dir | Installed nodes |

### Backup Script

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=/backups/nodered
DATA_DIR=/data

mkdir -p $BACKUP_DIR
tar czf $BACKUP_DIR/nodered-$DATE.tar.gz \
  -C $DATA_DIR \
  flows.json flows_cred.json settings.js package.json
```

### Restore

```bash
# Stop Node-RED
# Extract backup
tar xzf nodered-backup.tar.gz -C /data

# Install packages
cd /data
npm install

# Start Node-RED
```

---

## Upgrading

### Home Assistant Add-on

1. Settings → Add-ons
2. Node-RED add-on
3. Check for updates
4. Click Update

### Docker

```bash
docker pull nodered/node-red:latest
docker-compose down
docker-compose up -d
```

### Native

```bash
sudo npm install -g --unsafe-perm node-red
sudo systemctl restart nodered
```

### After Upgrade

1. Check installed nodes for compatibility
2. Review Node-RED changelog
3. Test critical flows
4. Update node-red-contrib-home-assistant-websocket if needed

---

## Next Steps

1. ✅ Installation complete
2. ✅ HA integration configured
3. Create your first flow:
   - Drag `trigger-state` node
   - Configure entity
   - Add `debug` node
   - Wire and deploy
4. Read the [Cookbook](references/cookbook.md) for examples
5. Check [Common Mistakes](references/troubleshooting.md) to avoid issues

