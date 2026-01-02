# Troubleshooting Flowcharts

Visual guides for diagnosing common Node-RED issues.

---

## Connection Issues

```
┌─────────────────────────────────────────────────────────┐
│              HA Server Not Connecting?                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Server node shows red │
              │     "disconnected"    │
              └───────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │ Can you access HA web interface │
         │     from same machine?          │
         └────────────────────────────────┘
                    │           │
                   YES          NO
                    │           │
                    ▼           ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Check token      │  │ HA is down or    │
    │ configuration    │  │ network issue    │
    └──────────────────┘  └──────────────────┘
              │                    │
              ▼                    ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Is token valid?  │  │ Check HA logs    │
    │ (not expired)    │  │ Start HA service │
    └──────────────────┘  └──────────────────┘
         │        │
        YES       NO
         │        │
         ▼        ▼
    ┌─────────┐ ┌──────────────────┐
    │ Check   │ │ Generate new     │
    │ URL     │ │ token in HA      │
    └─────────┘ └──────────────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │ URL format correct?          │
    │ - Include http:// or https://│
    │ - Correct port (8123)        │
    │ - No trailing slash          │
    └──────────────────────────────┘
         │        │
        YES       NO
         │        │
         ▼        ▼
    ┌─────────┐ ┌──────────────────┐
    │ Check   │ │ Fix URL format   │
    │ firewall│ │ Example:         │
    └─────────┘ │http://192.168.1.10:8123│
                └──────────────────┘
```

---

## Entity Not Found

```
┌─────────────────────────────────────────────────────────┐
│              Entity Not Found Error?                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Does entity exist in  │
              │ HA Developer Tools?   │
              └───────────────────────┘
                    │           │
                   YES          NO
                    │           │
                    ▼           ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Check spelling   │  │ Entity doesn't   │
    │ in Node-RED      │  │ exist - check    │
    │ node config      │  │ integration      │
    └──────────────────┘  └──────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │ Spelling matches exactly?    │
    │ (case-sensitive)             │
    └──────────────────────────────┘
         │        │
        YES       NO
         │        │
         ▼        ▼
    ┌─────────┐ ┌──────────────────┐
    │ Clear   │ │ Copy entity_id   │
    │ cache   │ │ from HA directly │
    └─────────┘ └──────────────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │ In server node config:       │
    │ Click "Update" or redeploy   │
    │ to refresh entity list       │
    └──────────────────────────────┘
```

---

## Flow Not Triggering

```
┌─────────────────────────────────────────────────────────┐
│              Flow Not Triggering?                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Is flow deployed?     │
              │ (no red deploy button)│
              └───────────────────────┘
                    │           │
                   YES          NO
                    │           │
                    ▼           ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Is flow/tab      │  │ Click Deploy     │
    │ enabled?         │  │ button           │
    └──────────────────┘  └──────────────────┘
         │        │
        YES       NO
         │        │
         ▼        ▼
    ┌─────────┐ ┌──────────────────┐
    │ Check   │ │ Enable flow tab  │
    │ trigger │ │ (right-click tab)│
    │ node    │ └──────────────────┘
    └─────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │ Does trigger node show       │
    │ green "connected" status?    │
    └──────────────────────────────┘
         │        │
        YES       NO
         │        │
         ▼        ▼
    ┌─────────┐ ┌──────────────────┐
    │ Check   │ │ Fix server       │
    │ trigger │ │ connection first │
    │ config  │ └──────────────────┘
    └─────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │ Add debug node after trigger │
    │ to see if messages arrive    │
    └──────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │ Messages arriving at debug?  │
    └──────────────────────────────┘
         │        │
        YES       NO
         │        │
         ▼        ▼
    ┌─────────────┐ ┌──────────────────┐
    │ Problem is  │ │ Check constraints│
    │ downstream  │ │ in trigger node  │
    │ in flow     │ │                  │
    └─────────────┘ │ - Entity ID      │
                    │ - State condition│
                    │ - Time filters   │
                    └──────────────────┘
```

---

## Service Call Failing

```
┌─────────────────────────────────────────────────────────┐
│              Service Call Not Working?                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Does service work     │
              │ in HA Developer Tools?│
              └───────────────────────┘
                    │           │
                   YES          NO
                    │           │
                    ▼           ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Check Node-RED   │  │ Service/entity   │
    │ service config   │  │ problem in HA    │
    └──────────────────┘  └──────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │ Using correct service name?  │
    │ Format: domain.service       │
    │ Example: light.turn_on       │
    └──────────────────────────────┘
         │        │
        YES       NO
         │        │
         ▼        ▼
    ┌─────────┐ ┌──────────────────┐
    │ Check   │ │ Fix service name │
    │ data    │ │ Check HA docs    │
    │ format  │ └──────────────────┘
    └─────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │ Is data/payload correct?     │
    │ - Valid JSON                 │
    │ - Required fields present    │
    │ - Correct data types         │
    └──────────────────────────────┘
         │        │
        YES       NO
         │        │
         ▼        ▼
    ┌─────────────┐ ┌──────────────────┐
    │ Check debug │ │ Fix data format  │
    │ node output │ │ Use JSONata or   │
    │ of service  │ │ function node    │
    │ node        │ │ to correct       │
    └─────────────┘ └──────────────────┘
```

---

## Message Not Passing Through

```
┌─────────────────────────────────────────────────────────┐
│           Message Stops Mid-Flow?                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Add debug nodes       │
              │ between each node     │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Find where message    │
              │ stops appearing       │
              └───────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │ What type of node stops it?    │
         └────────────────────────────────┘
              │         │         │
          Function   Switch    Other
              │         │         │
              ▼         ▼         ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Check    │ │ Verify   │ │ Check    │
    │ return   │ │ switch   │ │ node     │
    │ statement│ │ rules    │ │ config   │
    └──────────┘ └──────────┘ └──────────┘
         │            │            │
         ▼            ▼            ▼
    ┌──────────────────────────────────────┐
    │ Common causes:                        │
    │ - return null (drops message)         │
    │ - No matching switch condition        │
    │ - Wrong output wire                   │
    │ - Node has error (check status)       │
    │ - Async code without node.send()      │
    └──────────────────────────────────────┘
```

---

## Slow Performance

```
┌─────────────────────────────────────────────────────────┐
│              Node-RED Running Slow?                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Check Node-RED        │
              │ CPU/Memory usage      │
              └───────────────────────┘
                    │           │
                  HIGH         LOW
                    │           │
                    ▼           ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Too many messages│  │ Problem likely   │
    │ or heavy flows   │  │ external (HA,    │
    └──────────────────┘  │ network, etc.)   │
              │           └──────────────────┘
              ▼
    ┌──────────────────────────────┐
    │ Check for:                   │
    │ - Loops in flow              │
    │ - High-frequency triggers    │
    │ - Missing debounce           │
    │ - Too many debug nodes       │
    └──────────────────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │ Solutions:                   │
    │ - Add debounce/throttle      │
    │ - Reduce polling frequency   │
    │ - Disable unused debug nodes │
    │ - Split large flows          │
    │ - Use event triggers not poll│
    └──────────────────────────────┘
```

---

## Debug Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│              Quick Debug Checklist                       │
└─────────────────────────────────────────────────────────┘

□ Is the flow deployed? (no red deploy button)
□ Is the flow tab enabled? (not disabled)
□ Is server connection green?
□ Are entity IDs spelled correctly?
□ Is debug node connected and active?
□ Are switch conditions matching?
□ Does function return msg (not null)?
□ Are wires connected to correct outputs?
□ Check browser console for errors
□ Check Node-RED log for errors
```

---

## Error Message Quick Fixes

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| "Entity not found" | Typo in entity_id | Copy from HA |
| "Invalid token" | Expired/wrong token | Generate new token |
| "Connection refused" | HA not running | Start HA |
| "undefined is not iterable" | Missing data | Add null checks |
| "Cannot read property of undefined" | Missing nested prop | Use optional chaining |
| "Service not found" | Wrong service name | Check HA services |
| "Invalid JSON" | Malformed JSON | Validate JSON syntax |
