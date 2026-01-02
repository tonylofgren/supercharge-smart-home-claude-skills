# Installation Guide

## Claude Code Plugin Installation

### Global Installation

```bash
# Add as Claude Code MCP server
claude mcp add aurora-node-red -- npx -y @anthropic-ai/claude-code-mcp@latest \
  /path/to/aurora-smart-home/node-red
```

### Project-Based Installation

Create or edit `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "node-red": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/claude-code-mcp@latest",
        "/path/to/aurora-smart-home/node-red"
      ]
    }
  }
}
```

---

## Node-RED Setup

### Option 1: Home Assistant Addon (Recommended)

1. **Navigate to Add-ons:**
   ```
   Settings → Add-ons → Add-on Store
   ```

2. **Install Node-RED:**
   - Search for "Node-RED"
   - Click Install
   - Wait for installation

3. **Start Addon:**
   - Enable "Start on boot"
   - Click "Start"

4. **Access:**
   - Click "Open Web UI"
   - Default: `http://homeassistant.local:1880`

5. **Install HA Nodes:**
   - Menu → Manage Palette → Install
   - Search: `node-red-contrib-home-assistant-websocket`
   - Install

### Option 2: Docker

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

```bash
# Start
docker-compose up -d

# Install HA nodes
docker exec -it node-red npm install node-red-contrib-home-assistant-websocket

# Restart to load nodes
docker restart node-red
```

### Option 3: Manual Installation

```bash
# Install Node.js (v18+)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install Node-RED
sudo npm install -g --unsafe-perm node-red

# Install HA nodes
cd ~/.node-red
npm install node-red-contrib-home-assistant-websocket

# Start Node-RED
node-red
```

---

## Home Assistant Configuration

### Create Access Token

1. Open Home Assistant
2. Click your profile (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Name it "Node-RED"
6. Copy token immediately (shown only once)

### Configure Node-RED Server

1. Open Node-RED editor
2. Drag any HA node to workspace
3. Double-click to configure
4. Click pencil icon next to "Server"
5. Configure:

**For Addon:**
```
Addon: ✓ (checked)
```

**For External:**
```
Addon: ☐ (unchecked)
Base URL: http://192.168.1.100:8123
Access Token: [paste your token]
```

6. Click "Add" then "Deploy"

### Verify Connection

- Server node should show green "connected" status
- Entity autocomplete should work

---

## Custom Integration (For Entity Nodes)

If you want to create entities in Home Assistant from Node-RED:

### HACS Installation

1. Open HACS
2. Click "Integrations"
3. Search "Node-RED"
4. Install "Node-RED Companion"
5. Restart Home Assistant

### Manual Installation

1. Download from [GitHub](https://github.com/zachowj/hass-node-red)
2. Copy `custom_components/nodered` to your config
3. Restart Home Assistant

### Add Integration

1. Settings → Integrations
2. Add Integration
3. Search "Node-RED"
4. Configure

---

## Platform-Specific Notes

### Windows

```powershell
# Install Node.js from nodejs.org
# Then in PowerShell:
npm install -g --unsafe-perm node-red
cd $env:USERPROFILE\.node-red
npm install node-red-contrib-home-assistant-websocket
node-red
```

### macOS

```bash
# Using Homebrew
brew install node
npm install -g node-red
cd ~/.node-red
npm install node-red-contrib-home-assistant-websocket
node-red
```

### Linux

```bash
# Use NodeSource repository for latest Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
sudo npm install -g --unsafe-perm node-red
cd ~/.node-red
npm install node-red-contrib-home-assistant-websocket
node-red
```

### Raspberry Pi

```bash
# Use official Node-RED script
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
cd ~/.node-red
npm install node-red-contrib-home-assistant-websocket
sudo systemctl restart nodered
```

---

## Troubleshooting Installation

### Node-RED Won't Start

```bash
# Check logs
journalctl -u nodered -f

# Check port in use
netstat -tlnp | grep 1880

# Try different port
node-red -p 1881
```

### HA Nodes Not Appearing

```bash
# Reinstall nodes
cd ~/.node-red
npm uninstall node-red-contrib-home-assistant-websocket
npm install node-red-contrib-home-assistant-websocket

# Restart Node-RED
```

### Connection Issues

1. Verify HA is accessible
2. Check firewall rules
3. Regenerate access token
4. Verify URL format (include http://)

---

## Updating

### Addon

- Updates automatically via Supervisor
- Or: Settings → Add-ons → Node-RED → Update

### Docker

```bash
docker pull nodered/node-red:latest
docker-compose up -d
```

### Manual

```bash
sudo npm update -g node-red
cd ~/.node-red
npm update
```

### HA Nodes

- Menu → Manage Palette → Update
- Or: `npm update node-red-contrib-home-assistant-websocket`

---

## Next Steps

1. Read [SKILL.md](SKILL.md) for usage
2. Check [CHEATSHEET.md](CHEATSHEET.md) for quick patterns
3. Import templates from [templates/](templates/)
4. Explore [references/](references/) for detailed docs
