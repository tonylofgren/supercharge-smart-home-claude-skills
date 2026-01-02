# ESPHome Troubleshooting Flowcharts

Visual decision trees for debugging common ESPHome issues.

## WiFi Connection Issues

```dot
digraph wifi_debug {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="Device won't\nconnect to WiFi", shape=doublecircle];
    check_led [label="Status LED\nblinking?", shape=diamond];
    check_logs [label="Can view\nserial logs?", shape=diamond];
    check_ssid [label="SSID correct?\n(case sensitive)", shape=diamond];
    check_pass [label="Password\ncorrect?", shape=diamond];
    check_2ghz [label="Router on\n2.4GHz?", shape=diamond];
    check_distance [label="Device within\nrange?", shape=diamond];
    check_ap [label="Fallback AP\nvisible?", shape=diamond];

    fix_power [label="Check power\nsupply (5V 1A+)", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_ssid [label="Fix SSID in\nconfig", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_pass [label="Fix password\nin secrets.yaml", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_2ghz [label="Enable 2.4GHz\non router", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_distance [label="Move device\ncloser", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_flash [label="Re-flash via\nUSB", shape=box, style="rounded,filled", fillcolor=lightgreen];
    connect_ap [label="Connect to AP\nand check logs", shape=box, style="rounded,filled", fillcolor=lightgreen];

    start -> check_led;
    check_led -> fix_power [label="no"];
    check_led -> check_logs [label="yes"];
    check_logs -> check_ap [label="no"];
    check_logs -> check_ssid [label="yes"];
    check_ssid -> fix_ssid [label="no"];
    check_ssid -> check_pass [label="yes"];
    check_pass -> fix_pass [label="no"];
    check_pass -> check_2ghz [label="yes"];
    check_2ghz -> fix_2ghz [label="no"];
    check_2ghz -> check_distance [label="yes"];
    check_distance -> fix_distance [label="no"];
    check_distance -> fix_flash [label="yes - still fails"];
    check_ap -> connect_ap [label="yes"];
    check_ap -> fix_flash [label="no"];
}
```

**Common WiFi Fixes:**
- Ensure 2.4GHz is enabled (ESP doesn't support 5GHz)
- Check for special characters in SSID/password
- Try `fast_connect: true` in wifi config
- Add `output_power: 20dB` for better range

---

## Sensor Not Reading

```dot
digraph sensor_debug {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="Sensor shows\nNaN or no data", shape=doublecircle];
    check_wiring [label="Wiring\ncorrect?", shape=diamond];
    check_power [label="Sensor getting\npower? (3.3V/5V)", shape=diamond];
    check_gpio [label="Correct GPIO\npin?", shape=diamond];
    check_platform [label="Correct sensor\nplatform?", shape=diamond];
    check_pullup [label="Pull-up/down\nneeded?", shape=diamond];
    check_address [label="I2C address\ncorrect?", shape=diamond];

    fix_wiring [label="Check:\nVCC, GND, Data", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_power [label="Verify voltage\nwith multimeter", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_gpio [label="Check board\npinout diagram", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_platform [label="Verify sensor\nmodel/type", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_pullup [label="Add pullup_resistor\nor mode: INPUT_PULLUP", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_address [label="Run I2C scan\nCheck datasheet", shape=box, style="rounded,filled", fillcolor=lightgreen];
    sensor_dead [label="Sensor may\nbe defective", shape=box, style="rounded,filled", fillcolor=lightyellow];

    start -> check_wiring;
    check_wiring -> fix_wiring [label="unsure"];
    check_wiring -> check_power [label="yes"];
    check_power -> fix_power [label="no/unsure"];
    check_power -> check_gpio [label="yes"];
    check_gpio -> fix_gpio [label="unsure"];
    check_gpio -> check_platform [label="yes"];
    check_platform -> fix_platform [label="wrong"];
    check_platform -> check_pullup [label="correct"];
    check_pullup -> fix_pullup [label="no"];
    check_pullup -> check_address [label="N/A or yes"];
    check_address -> fix_address [label="I2C sensor"];
    check_address -> sensor_dead [label="all correct"];
}
```

**I2C Scan Command:**
```yaml
i2c:
  scan: true  # Shows detected addresses in logs
```

---

## OTA Update Failing

```dot
digraph ota_debug {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="OTA update\nfails", shape=doublecircle];
    check_wifi [label="Device on\nsame network?", shape=diamond];
    check_ip [label="Can ping\ndevice IP?", shape=diamond];
    check_space [label="Enough flash\nspace?", shape=diamond];
    check_pass [label="OTA password\ncorrect?", shape=diamond];
    check_timeout [label="Upload\ntimeout?", shape=diamond];

    fix_network [label="Connect to\nsame subnet", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_ip [label="Check IP in\nlogs/router", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_space [label="Reduce config\nor use USB", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_pass [label="Update OTA\npassword", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_timeout [label="Move closer\nor use USB", shape=box, style="rounded,filled", fillcolor=lightgreen];

    start -> check_wifi;
    check_wifi -> fix_network [label="no"];
    check_wifi -> check_ip [label="yes"];
    check_ip -> fix_ip [label="no"];
    check_ip -> check_space [label="yes"];
    check_space -> fix_space [label="no"];
    check_space -> check_pass [label="yes"];
    check_pass -> fix_pass [label="wrong"];
    check_pass -> check_timeout [label="correct"];
    check_timeout -> fix_timeout [label="yes"];
}
```

**Tips:**
- Check flash size: ESP8266 needs 1MB+, ESP32 needs 4MB+
- Use `esphome upload device.yaml --device 192.168.x.x`
- Disable antivirus/firewall temporarily

---

## Boot Loop / Crash

```dot
digraph bootloop_debug {
    rankdir=TB;
    node [shape=box, style=rounded];

    start [label="Device keeps\nrebooting", shape=doublecircle];
    check_power [label="Power supply\nadequate?", shape=diamond];
    check_gpio0 [label="GPIO0 floating\nor pulled up?", shape=diamond];
    check_logs [label="Can see\ncrash logs?", shape=diamond];
    check_lambda [label="Complex lambda\nor automation?", shape=diamond];
    check_memory [label="Memory issue\n(heap low)?", shape=diamond];

    fix_power [label="Use 5V 2A\npower supply", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_gpio0 [label="Add 10k pull-up\nto GPIO0", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_safe [label="Flash with\nsafe_mode enabled", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_lambda [label="Simplify lambda\ncode", shape=box, style="rounded,filled", fillcolor=lightgreen];
    fix_memory [label="Reduce sensors\nor update intervals", shape=box, style="rounded,filled", fillcolor=lightgreen];

    start -> check_power;
    check_power -> fix_power [label="no/weak"];
    check_power -> check_gpio0 [label="yes"];
    check_gpio0 -> fix_gpio0 [label="no"];
    check_gpio0 -> check_logs [label="yes"];
    check_logs -> fix_safe [label="no"];
    check_logs -> check_lambda [label="yes"];
    check_lambda -> fix_lambda [label="yes"];
    check_lambda -> check_memory [label="no"];
    check_memory -> fix_memory [label="yes"];
}
```

**Safe Mode Config:**
```yaml
safe_mode:
  boot_is_good_after: 1min
  num_attempts: 5
```

---

## Quick Debug Commands

```yaml
# Enable debug logging
logger:
  level: DEBUG

# Show free memory
sensor:
  - platform: debug
    free:
      name: "Free Heap"
    loop_time:
      name: "Loop Time"

# I2C device scan
i2c:
  scan: true

# WiFi diagnostics
text_sensor:
  - platform: wifi_info
    ip_address:
      name: "IP Address"
    ssid:
      name: "Connected SSID"
    bssid:
      name: "Connected BSSID"
    mac_address:
      name: "MAC Address"
```

## See Also

- [troubleshooting.md](troubleshooting.md) - Common errors and solutions
- [boards.md](boards.md) - Board pinouts and capabilities
- [power-management.md](power-management.md) - Power supply requirements
