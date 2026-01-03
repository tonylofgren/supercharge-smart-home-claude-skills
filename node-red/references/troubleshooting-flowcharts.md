# Troubleshooting Flowcharts

Visual guides for diagnosing common issues.

## Connection Problems

```
START: Can't connect to Home Assistant
                │
                ▼
    ┌─────────────────────┐
    │ Is HA running?       │
    │ Check HA status      │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check URL      Start HA
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Is URL correct?      │
    │ http://ha.local:8123 │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check Token    Fix URL
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Is token valid?      │
    │ Try creating new one │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check Network  Create Token
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Can ping HA host?    │
    │ Check firewall      │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check SSL      Fix Network
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Using HTTPS?         │
    │ Check cert config   │
    └─────────────────────┘
```

---

## Flow Not Triggering

```
START: Automation not firing
                │
                ▼
    ┌─────────────────────┐
    │ Is flow deployed?    │
    │ Check for red dot   │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check Node     Deploy Now
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Is trigger enabled?  │
    │ Not disabled/bypassed│
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check Entity   Enable It
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Entity ID correct?   │
    │ Check spelling      │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check Constraints Fix ID
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Constraints met?     │
    │ Check conditions    │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Add Debug      Adjust Rules
       │
       ▼
    ┌─────────────────────┐
    │ Add debug node       │
    │ Check if msg arrives │
    └─────────────────────┘
```

---

## Service Call Failing

```
START: Service call not working
                │
                ▼
    ┌─────────────────────┐
    │ Check debug output   │
    │ Any error messages?  │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
    ERROR          NO ERROR
       │             │
       ▼             ▼
  ┌─────────┐   ┌─────────┐
  │ Parse   │   │ Message │
  │ Error   │   │ Arrives?│
  └────┬────┘   └────┬────┘
       │             │
       ▼        ┌────┴────┐
    ┌─────────────────────┐
    │ Is domain correct?   │
    │ light, switch, etc.  │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check Service  Fix Domain
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Is service correct?  │
    │ turn_on, turn_off   │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Check Data     Fix Service
       │             │
       ▼             │
    ┌─────────────────────┐
    │ Data format correct? │
    │ JSON valid?         │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
      YES           NO
       │             │
       ▼             ▼
  Test in HA    Fix JSON
       │
       ▼
    ┌─────────────────────┐
    │ Try in Developer     │
    │ Tools → Services     │
    └─────────────────────┘
```

---

## Function Node Error

```
START: Function node error
                │
                ▼
    ┌─────────────────────┐
    │ Check error message  │
    │ Look at debug panel │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────────────────────────┐
    │ What type of error?                      │
    ├──────────┬──────────┬──────────┬────────┤
    │TypeError │Reference │Syntax   │Other   │
    │          │Error     │Error    │        │
    └────┬─────┴────┬─────┴────┬────┴───┬────┘
         │          │          │         │
         ▼          ▼          ▼         ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │Check    │ │Variable │ │Fix      │ │Check    │
    │property │ │not      │ │syntax:  │ │full     │
    │access   │ │defined  │ │brackets │ │message  │
    │null/    │ │         │ │commas   │ │         │
    │undefined│ │         │ │quotes   │ │         │
    └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
         │          │          │         │
         ▼          ▼          ▼         ▼
    ┌─────────────────────────────────────────┐
    │ Use optional chaining:                   │
    │ msg.data?.new_state?.attributes?.value  │
    │                                          │
    │ Check variable spelling                  │
    │ Validate JSON syntax                     │
    └─────────────────────────────────────────┘
```

---

## Message Not Arriving

```
START: No message at destination
                │
                ▼
    ┌─────────────────────┐
    │ Where does it stop?  │
    │ Add debug nodes     │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────────────────────────┐
    │ Message visible in debug at...          │
    ├──────────────┬──────────────────────────┤
    │ Nowhere      │ Somewhere in middle      │
    └──────┬───────┴──────────┬───────────────┘
           │                  │
           ▼                  ▼
    ┌─────────────┐   ┌─────────────────────┐
    │ Source not  │   │ Which node stops it?│
    │ triggering  │   │ Check that node     │
    │             │   └──────────┬──────────┘
    │ See "Flow   │              │
    │ Not         │   ┌──────────┴──────────┐
    │ Triggering" │   │                     │
    └─────────────┘   ▼                     ▼
               ┌─────────────┐    ┌─────────────┐
               │ Switch node │    │ Function    │
               │ No match?   │    │ returns     │
               │             │    │ null?       │
               │ Check rules │    │             │
               │ Add "else"  │    │ Check logic │
               └─────────────┘    └─────────────┘
```

---

## Entity Not Found

```
START: Entity not found error
                │
                ▼
    ┌─────────────────────┐
    │ Check entity in HA   │
    │ Settings → Entities │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
    EXISTS      NOT EXISTS
       │             │
       ▼             ▼
  ┌─────────┐   ┌─────────┐
  │ Check   │   │ Create  │
  │ spelling│   │ entity  │
  │         │   │ or fix  │
  │ Case    │   │ device  │
  │ matters!│   │         │
  └────┬────┘   └─────────┘
       │
       ▼
    ┌─────────────────────┐
    │ Copy exact entity_id │
    │ from HA to Node-RED  │
    └─────────┬───────────┘
              │
       ┌──────┴──────┐
       │             │
    WORKS       STILL FAILS
       │             │
       ▼             ▼
     DONE      ┌─────────────┐
               │ Check HA    │
               │ connection  │
               │             │
               │ Reconnect   │
               │ server node │
               └─────────────┘
```

---

## Timer Issues

```
START: Timer not working
                │
                ▼
    ┌─────────────────────┐
    │ Which timer issue?   │
    └─────────┬───────────┘
              │
    ┌─────────┴─────────┬─────────────────┐
    │                   │                 │
    ▼                   ▼                 ▼
┌─────────┐      ┌─────────────┐   ┌─────────────┐
│Won't    │      │Won't        │   │Fires        │
│start    │      │reset        │   │multiple     │
│         │      │             │   │times        │
└────┬────┘      └──────┬──────┘   └──────┬──────┘
     │                  │                 │
     ▼                  ▼                 ▼
┌─────────────┐  ┌─────────────┐   ┌─────────────┐
│Check input  │  │Using extend │   │Check for    │
│message      │  │property?    │   │duplicate    │
│arrives      │  │             │   │flows        │
│             │  │extend: true │   │             │
│Add debug    │  │to reset     │   │Check link   │
│before timer │  │on new msg   │   │nodes        │
└─────────────┘  └─────────────┘   └─────────────┘
```

---

## State Access Issues

```
START: Can't read entity state
                │
                ▼
    ┌─────────────────────┐
    │ Using correct method?│
    └─────────┬───────────┘
              │
    ┌─────────┴─────────────────────┐
    │                               │
    ▼                               ▼
┌─────────────────────┐    ┌─────────────────────┐
│ global.get(...)     │    │ api-current-state   │
│                     │    │ node                │
│ Check path:         │    │                     │
│ global.get(         │    │ Single entity only  │
│   "homeassistant"   │    │ entityIdType: exact │
│ ).homeAssistant     │    │                     │
│   .states           │    │ For multiple, use   │
│                     │    │ get-entities node   │
└──────────┬──────────┘    └─────────────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ States populated?    │
    │                      │
    │ Wait for HA connect  │
    │ before accessing     │
    │                      │
    │ Check for undefined  │
    └─────────────────────┘
```

---

## Debug Strategy

```
START: Something's wrong
                │
                ▼
    ┌─────────────────────────────────────────┐
    │ STEP 1: Add debug nodes                  │
    │                                          │
    │ [trigger] → [debug A]                    │
    │      ↓                                   │
    │ [function] → [debug B]                   │
    │      ↓                                   │
    │ [action] → [debug C]                     │
    └─────────────────────┬───────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────┐
    │ STEP 2: Identify where it stops          │
    │                                          │
    │ A shows, B doesn't → Problem in function│
    │ B shows, C doesn't → Problem in action  │
    │ Nothing shows → Problem in trigger      │
    └─────────────────────┬───────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────┐
    │ STEP 3: Check the failing node           │
    │                                          │
    │ • Node status (bottom text)              │
    │ • Debug sidebar messages                 │
    │ • Node configuration                     │
    └─────────────────────┬───────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────┐
    │ STEP 4: Fix and verify                   │
    │                                          │
    │ • Make one change at a time              │
    │ • Deploy and test                        │
    │ • Repeat until working                   │
    └─────────────────────────────────────────┘
```

---

## Quick Decision Trees

### Which Trigger Node?

```
Need to trigger on...
       │
       ├── State change → trigger-state
       │
       ├── Time schedule → inject (crontab)
       │
       ├── Device event → device trigger
       │
       ├── Location → zone
       │
       ├── External → webhook
       │
       └── Multiple states → get-entities + switch
```

### How to Get State?

```
Need entity state...
       │
       ├── Single entity, inline → api-current-state
       │
       ├── Single entity, in function → global.get(...)
       │
       ├── Multiple entities → get-entities
       │
       ├── Historical data → get-history
       │
       └── Periodic check → poll-state
```

### Service Call Method?

```
Need to call service...
       │
       ├── Simple, configured → api-call-service (UI)
       │
       ├── Dynamic target → api-call-service (msg.payload)
       │
       ├── Complex data → function + api-call-service
       │
       └── Multiple calls → split + api-call-service
```

