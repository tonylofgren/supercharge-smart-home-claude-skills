# Custom Card Development for Home Assistant

> Guide to creating custom Lovelace cards with JavaScript/TypeScript

## Overview

Custom cards extend Home Assistant's dashboard capabilities beyond built-in cards. They're JavaScript-based web components that can render any UI you need.

## Development Options

### 1. Lit-based Card (Recommended)
Best for: Production cards with reactivity, state management, and built-in XSS protection.

### 2. Simple JavaScript Card
Best for: Quick prototypes (use Lit for production).

### 3. React/Preact Card
Best for: Developers familiar with React ecosystem.

---

## Security Best Practices

> **Important**: Always use safe DOM methods to prevent XSS vulnerabilities.

| Avoid | Use Instead |
|-------|-------------|
| `element.innerHTML = userInput` | Lit's `html` template literals |
| String concatenation for HTML | Template literals with auto-escaping |
| Direct DOM manipulation with user data | Lit's reactive properties |

Lit automatically escapes values in templates, making it the safest choice.

---

## Quick Start with Lit (Recommended)

### Project Setup

```bash
# Create project
mkdir my-card && cd my-card
npm init -y

# Install dependencies
npm install lit
npm install -D typescript rollup @rollup/plugin-node-resolve @rollup/plugin-typescript

# Create TypeScript config
```

Create `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2021",
    "module": "ESNext",
    "moduleResolution": "node",
    "lib": ["ES2021", "DOM", "DOM.Iterable"],
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "experimentalDecorators": true,
    "useDefineForClassFields": false
  },
  "include": ["src/**/*.ts"]
}
```

### Rollup Configuration

Create `rollup.config.js`:
```javascript
import resolve from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";

export default {
  input: "src/my-card.ts",
  output: {
    file: "dist/my-card.js",
    format: "es",
  },
  plugins: [
    resolve(),
    typescript(),
  ],
};
```

### Card Implementation

Create `src/my-card.ts`:

```typescript
import { LitElement, html, css, PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";

// Type definitions for Home Assistant
interface HomeAssistant {
  states: { [entity_id: string]: HassEntity };
  callService(domain: string, service: string, data?: object): Promise<void>;
  formatEntityState(entity: HassEntity): string;
  locale: HassLocale;
  themes: HassThemes;
}

interface HassEntity {
  entity_id: string;
  state: string;
  attributes: { [key: string]: any };
  last_changed: string;
  last_updated: string;
}

interface CardConfig {
  type: string;
  entity?: string;
  name?: string;
  icon?: string;
  show_state?: boolean;
}

@customElement("my-lit-card")
export class MyLitCard extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @state() private config!: CardConfig;

  // Card configuration
  static getConfigElement() {
    return document.createElement("my-lit-card-editor");
  }

  static getStubConfig() {
    return {
      entity: "sun.sun",
      name: "My Card",
      show_state: true,
    };
  }

  setConfig(config: CardConfig) {
    if (!config.entity) {
      throw new Error("Please define an entity");
    }
    this.config = config;
  }

  // Styling
  static styles = css`
    ha-card {
      padding: 16px;
    }
    .card-content {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .state {
      font-size: 24px;
      font-weight: bold;
    }
    .name {
      color: var(--secondary-text-color);
    }
    .icon {
      --mdc-icon-size: 40px;
      color: var(--state-icon-color);
    }
    .row {
      display: flex;
      align-items: center;
      gap: 16px;
    }
  `;

  // Render method - Lit auto-escapes values for XSS protection
  protected render() {
    if (!this.config || !this.hass) {
      return html``;
    }

    const entity = this.hass.states[this.config.entity!];
    if (!entity) {
      return html`
        <ha-card>
          <div class="card-content">
            Entity not found: ${this.config.entity}
          </div>
        </ha-card>
      `;
    }

    const name = this.config.name || entity.attributes.friendly_name || entity.entity_id;
    const icon = this.config.icon || entity.attributes.icon || "mdi:help-circle";
    const state = this.hass.formatEntityState(entity);

    // Lit's html tagged template auto-escapes all interpolated values
    return html`
      <ha-card>
        <div class="card-content">
          <div class="row">
            <ha-icon class="icon" .icon=${icon}></ha-icon>
            <div>
              <div class="name">${name}</div>
              ${this.config.show_state !== false
                ? html`<div class="state">${state}</div>`
                : ""}
            </div>
          </div>
        </div>
      </ha-card>
    `;
  }

  // Lifecycle
  protected updated(changedProps: PropertyValues) {
    super.updated(changedProps);
  }

  // Card size for grid
  getCardSize(): number {
    return 2;
  }
}

// Register card info
window.customCards = window.customCards || [];
window.customCards.push({
  type: "my-lit-card",
  name: "My Lit Card",
  description: "A custom card built with Lit",
  preview: true,
});

// TypeScript declarations
declare global {
  interface HTMLElementTagNameMap {
    "my-lit-card": MyLitCard;
  }
  interface Window {
    customCards: Array<{
      type: string;
      name: string;
      description: string;
      preview?: boolean;
    }>;
  }
}
```

### Add as Resource

In `configuration.yaml`:
```yaml
lovelace:
  mode: yaml  # or use UI
  resources:
    - url: /local/my-card.js
      type: module
```

Or via UI: Settings → Dashboards → Resources → Add Resource

### Use in Dashboard

```yaml
type: custom:my-lit-card
entity: sensor.temperature
name: Temperature
```

---

## Card Editor (Visual Configuration)

Allow users to configure the card through UI:

```typescript
import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("my-lit-card-editor")
export class MyLitCardEditor extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @state() private config!: CardConfig;

  setConfig(config: CardConfig) {
    this.config = config;
  }

  private _valueChanged(ev: CustomEvent) {
    const target = ev.target as any;
    const value = ev.detail?.value ?? target.value;
    const key = target.configValue;

    if (!key) return;

    const newConfig = { ...this.config, [key]: value };

    // Dispatch config-changed event
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: newConfig },
        bubbles: true,
        composed: true,
      })
    );
  }

  static styles = css`
    .form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
  `;

  protected render() {
    if (!this.hass || !this.config) {
      return html``;
    }

    return html`
      <div class="form">
        <ha-entity-picker
          .hass=${this.hass}
          .value=${this.config.entity}
          .configValue=${"entity"}
          @value-changed=${this._valueChanged}
          allow-custom-entity
        ></ha-entity-picker>

        <ha-textfield
          label="Name (optional)"
          .value=${this.config.name || ""}
          .configValue=${"name"}
          @input=${this._valueChanged}
        ></ha-textfield>

        <ha-icon-picker
          .hass=${this.hass}
          .value=${this.config.icon || ""}
          .configValue=${"icon"}
          @value-changed=${this._valueChanged}
        ></ha-icon-picker>

        <ha-formfield label="Show State">
          <ha-switch
            .checked=${this.config.show_state !== false}
            .configValue=${"show_state"}
            @change=${this._valueChanged}
          ></ha-switch>
        </ha-formfield>
      </div>
    `;
  }
}
```

---

## Interacting with Home Assistant

### Call Services

```typescript
// Toggle a light
this.hass.callService("light", "toggle", {
  entity_id: this.config.entity,
});

// Turn on with brightness
this.hass.callService("light", "turn_on", {
  entity_id: this.config.entity,
  brightness_pct: 50,
});

// Run a script
this.hass.callService("script", "turn_on", {
  entity_id: "script.my_script",
});
```

### Handle Events

```typescript
// In render method - use Lit event binding
protected render() {
  return html`
    <ha-card @click=${this._handleClick}>
      ...
    </ha-card>
  `;
}

private _handleClick(ev: Event) {
  ev.stopPropagation();
  this.hass.callService("light", "toggle", {
    entity_id: this.config.entity,
  });
}
```

### Subscribe to State Changes

```typescript
protected firstUpdated() {
  // Subscribe to specific entity
  this.hass.connection.subscribeMessage(
    (msg) => this._handleStateChange(msg),
    { type: "subscribe_events", event_type: "state_changed" }
  );
}

private _handleStateChange(msg: any) {
  if (msg.data.entity_id === this.config.entity) {
    this.requestUpdate();
  }
}
```

---

## Using Home Assistant Components

HA provides many reusable components:

```typescript
// Entity picker
html`<ha-entity-picker .hass=${this.hass}></ha-entity-picker>`

// Icon picker
html`<ha-icon-picker .hass=${this.hass}></ha-icon-picker>`

// Icon
html`<ha-icon .icon=${"mdi:home"}></ha-icon>`

// State icon (auto-colored)
html`<ha-state-icon .state=${entity}></ha-state-icon>`

// Switch
html`<ha-switch .checked=${true}></ha-switch>`

// Slider
html`<ha-slider .value=${50} .min=${0} .max=${100}></ha-slider>`

// Button
html`<ha-button @click=${this._click}>Click Me</ha-button>`

// Alert
html`<ha-alert alert-type="warning">Warning message</ha-alert>`

// Card
html`<ha-card header="Title">Content</ha-card>`
```

---

## Advanced Features

### Conditional Rendering

```typescript
protected render() {
  const entity = this.hass.states[this.config.entity!];

  return html`
    <ha-card>
      ${entity.state === "on"
        ? html`<div class="on">Device is ON</div>`
        : html`<div class="off">Device is OFF</div>`
      }

      ${this.config.show_graph
        ? html`<my-graph .data=${entity}></my-graph>`
        : ""}
    </ha-card>
  `;
}
```

### Dynamic Styling

```typescript
static styles = css`
  :host {
    --card-primary-color: var(--primary-color);
  }

  .state-on {
    color: var(--state-light-active-color, var(--state-active-color));
  }

  .state-off {
    color: var(--state-light-inactive-color, var(--state-inactive-color));
  }
`;

protected render() {
  const isOn = entity.state === "on";

  return html`
    <div class="state ${isOn ? "state-on" : "state-off"}">
      ${entity.state}
    </div>
  `;
}
```

### Card Actions (Tap, Hold, Double-Tap)

```typescript
import { handleAction, hasAction } from "custom-card-helpers";

protected render() {
  return html`
    <ha-card
      @action=${this._handleAction}
      .actionHandler=${actionHandler({
        hasHold: hasAction(this.config.hold_action),
        hasDoubleClick: hasAction(this.config.double_tap_action),
      })}
    >
      ...
    </ha-card>
  `;
}

private _handleAction(ev: ActionHandlerEvent) {
  handleAction(this, this.hass!, this.config, ev.detail.action);
}
```

### Localization

```typescript
// Use Home Assistant's localization
const localizedState = this.hass.localize(
  `component.${domain}.state.${entity.state}`
);

// Or format entities
const formattedState = this.hass.formatEntityState(entity);
const formattedAttribute = this.hass.formatEntityAttributeValue(
  entity,
  "brightness"
);
```

---

## Publishing to HACS

### 1. Repository Structure

```
my-card/
├── dist/
│   └── my-card.js
├── hacs.json
├── README.md
├── LICENSE
└── info.md
```

### 2. hacs.json

```json
{
  "name": "My Custom Card",
  "render_readme": true,
  "filename": "my-card.js"
}
```

### 3. Release Process

1. Build production bundle
2. Create GitHub release with version tag (e.g., `v1.0.0`)
3. Attach `my-card.js` to release
4. Submit to HACS default repository (or users can add custom)

### 4. README Requirements

- Card name and description
- Screenshot/GIF of card in action
- Installation instructions
- Configuration options table
- Example configurations

---

## Debugging Tips

### Browser DevTools

1. Open dashboard in browser
2. F12 → Elements → Find your card
3. Console for JavaScript errors
4. Network tab for resource loading

### Debug Logging

```typescript
protected updated(changedProps: PropertyValues) {
  console.log("Card updated:", changedProps);
  console.log("Current config:", this.config);
  console.log("Entity state:", this.hass?.states[this.config.entity!]);
}
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Card not showing | Check resource URL, clear cache |
| "Custom element doesn't exist" | customElements.define not called |
| State not updating | Check `set hass()` implementation |
| Styles not applying | Use Shadow DOM or ha-card styles |

---

## Resources

- [Home Assistant Frontend Docs](https://developers.home-assistant.io/docs/frontend/)
- [Lit Documentation](https://lit.dev/)
- [Custom Cards Tutorial (HA Community)](https://community.home-assistant.io/)
- [card-tools (Helper Library)](https://github.com/thomasloven/lovelace-card-tools)
- [HACS Documentation](https://hacs.xyz/)

---

## Example Cards to Study

| Card | Description | GitHub |
|------|-------------|--------|
| Button Card | Highly customizable button | button-card |
| Mini Graph Card | Sensor history graphs | mini-graph-card |
| Mushroom Cards | Modern card collection | mushroom |
| Stack In Card | Card grouping | stack-in-card |
| Card Mod | CSS customization | lovelace-card-mod |
