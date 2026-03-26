# Bill of Materials — Watchmaker's Lathe Controller

## Raspberry Pi Platform

---

### Core Electronics

| # | Component | Qty | Recommended Part | Est. Cost | Source |
|---|-----------|-----|------------------|-----------|--------|
| 1 | Raspberry Pi 4B (2GB+) or Pi 5 | 1 | Pi 4B 4GB recommended | $45–80 | PiShop, Amazon |
| 2 | Official Pi 7" Touchscreen | 1 | DSI, 800×480, capacitive | $60–75 | PiShop, Amazon |
| 3 | Pi Touchscreen Case | 1 | SmartiPi Touch 2 or Pibow | $15–30 | Amazon |
| 4 | MicroSD Card (32GB+) | 1 | SanDisk Extreme / Samsung EVO | $8–12 | Amazon |
| 5 | USB-C Power Supply (Pi) | 1 | Official Pi 5V 3A PSU | $8–12 | PiShop |

### Motor & Driver

| # | Component | Qty | Recommended Part | Est. Cost | Source |
|---|-----------|-----|------------------|-----------|--------|
| 6 | NEMA 17 Stepper (0.9°, 2A) | 1 | 42HS48-2004S (0.44 N·m) | $15–25 | StepperOnline |
| 7 | TMC2209 Stepper Driver | 1 | BigTreeTech TMC2209 v1.3 | $6–10 | Amazon, BTT |
| 8 | 24V 3A Power Supply (Motor) | 1 | Mean Well LRS-75-24 | $12–18 | Amazon, Digi-Key |
| 9 | 100µF 50V Electrolytic Cap | 1 | Near TMC2209 VM pin | $0.50 | Mouser |

> **Alternative motor:** For higher RPM lathe use (>3000 RPM at spindle), consider a NEMA 23 with more torque, especially with higher gear ratios.

### RPM Sensor

| # | Component | Qty | Recommended Part | Est. Cost | Source |
|---|-----------|-----|------------------|-----------|--------|
| 10a | Hall Effect Sensor | 1 | KY-003 (A3144 based) | $2–4 | Amazon |
| 10b | Small Neodymium Magnet | 1 | 3×1mm disc (epoxied to spindle/pulley) | $1 | Amazon |
| — | *OR Alternative:* | — | — | — | — |
| 10c | Optical Slot Sensor | 1 | KY-010 / TCPT1300 | $2–4 | Amazon |
| 10d | Slotted Disc | 1 | 3D print, 1 slot per rev | $0 | DIY |

> **Recommendation:** Hall effect + magnet is simpler, more robust in a shop environment, and doesn't care about dust/oil. Glue a tiny magnet to the motor pulley.

### Input Controls

| # | Component | Qty | Recommended Part | Est. Cost | Source |
|---|-----------|-----|------------------|-----------|--------|
| 11 | Rotary Encoder (speed knob) | 1 | KY-040 or Bourns PEC11R (100 PPR) | $3–8 | Amazon |
| 12 | Heavy Machined Knob | 1 | Aluminum 25mm+ dia, D-shaft | $5–10 | Amazon |
| 13 | Momentary Push Buttons | 2 | 16mm panel-mount, LED ring | $4–8 | Amazon |
| 14 | Emergency Stop Button | 1 | NC mushroom, 22mm panel-mount | $5–8 | Amazon |
| 15 | Toggle Switch (Power) | 1 | DPST illuminated, 16A | $3–5 | Amazon |

### Mechanical — Drive System

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| 16 | GT2 Timing Pulley (Motor) | 1 | 16T or 20T, 5mm bore | $3–5 | Amazon |
| 17 | GT2 Timing Pulley (Lathe) | 1 | 60T–80T, bore to match spindle | $6–12 | Amazon |
| 18 | GT2 Timing Belt (6mm) | 1 | Length per center distance | $4–8 | Amazon |
| 19 | Motor Mounting Bracket | 1 | Custom per lathe model | $5–15 | Fabricate/3D print |
| 20 | Belt Tensioner Idler | 1 | GT2 idler bearing | $3–5 | Amazon |

### Wiring & Enclosure

| # | Component | Qty | Notes | Est. Cost | Source |
|---|-----------|-----|-------|-----------|--------|
| 21 | Project Enclosure | 1 | Aluminum 200×120×60mm or 3D print | $10–20 | Amazon |
| 22 | GPIO Breakout / HAT Proto | 1 | Pi GPIO prototyping board | $5–10 | Amazon |
| 23 | Level Shifter (3.3V↔5V) | 1 | Bidirectional 4-ch (TXS0108E) | $2–4 | Amazon |
| 24 | 10kΩ Resistors | 5 | Pull-ups for buttons/sensor | $1 | Amazon |
| 25 | 22 AWG Silicone Wire | 3m | Signal wiring | $3 | Amazon |
| 26 | 18 AWG Wire | 1m | Motor + power | $2 | Amazon |
| 27 | JST-XH Connectors | 1 set | Motor & sensor connections | $4 | Amazon |
| 28 | GX12-4 Aviation Connector | 1 set | Motor quick-disconnect | $3 | Amazon |
| 29 | Cable Glands (PG7) | 3 | Enclosure wire entry | $2 | Amazon |

---

### Estimated Total: **$240–$400 USD**

(Higher than the ESP32 version due to the Pi + touchscreen, but you gain a full GUI, RPM control, and room for future features like WiFi remote, data logging, etc.)

---

## Watchmaking-Specific Considerations

### Lathe Compatibility Notes

| Lathe | Spindle Connection | Notes |
|-------|--------------------|-------|
| Sherline | Fits ER16 or standard nose, use pulley on motor side | Common hobby lathe |
| Levin | Headstock pulley replacement | Classic watchmaker's lathe |
| Boley F1 | Round belt pulley → timing belt adapter needed | Precision instrument lathe |
| Lorch KD50 | Belt-drive compatible | German precision lathe |
| Taig Micro | Direct pulley swap | Popular micro lathe |
| Cowells ME90 | Belt drive, easy pulley swap | Small model engineering lathe |

### Recommended Gear Ratios for Watchmaking

| Application | Motor Pulley | Lathe Pulley | Ratio | RPM Range (at motor max) | Indexing Resolution |
|-------------|-------------|-------------|-------|--------------------------|---------------------|
| General turning | 20T | 60T | 3:1 | 50–2,700 RPM | 0.0033° |
| Fine turning + indexing | 16T | 80T | 5:1 | 50–1,600 RPM | 0.0018° |
| High-speed drilling | 30T | 30T | 1:1 | 50–8,000 RPM | 0.0088° |
| Gear cutting (slow) | 16T | 80T | 5:1 | 50–1,600 RPM | 0.0018° |

> Use a 0.9° stepper (400 steps/rev) at 256 microsteps for maximum resolution. With a 5:1 ratio that's **512,000 steps/rev**.

---

## Optional Upgrades

| Upgrade | Part | Purpose |
|---------|------|---------|
| Closed-loop stepper | NEMA 17 + AS5600 encoder | Detect stalls, verify position |
| Foot pedal | USB sustain pedal | Hands-free speed control |
| Coolant pump | Small 12V peristaltic pump | Controlled from GPIO |
| Chip guard | 3D-printed shield | Protect encoder/sensor from swarf |
| WiFi dashboard | (built into Pi) | Monitor RPM from phone |
| Camera | Pi Camera Module | Magnification for fine work |
| Tachometer display | Separate LED 7-seg | Always-visible RPM readout |

## Tools Required

- Soldering iron + solder
- Wire strippers, crimpers
- Multimeter
- USB keyboard + mouse (initial Pi setup)
- Allen wrenches (pulley set screws)
- Drill (enclosure holes)
