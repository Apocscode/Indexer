# Materials List — Complete Parts Reference

## Both Projects: ESP32 5C Indexer + Watchmaker's Lathe Controller

---

## Section A: ESP32 Indexing Controller (HHIP 5C Spin Jig)

### A1 — Core Electronics

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| A1 | ESP32 DevKit V1 (38-pin) | 1 | ESP-WROOM-32 DevKit, USB-C | $8–12 | Amazon, AliExpress |
| A2 | TMC2209 Stepper Driver | 1 | BigTreeTech TMC2209 v1.3, UART mode | $6–10 | Amazon, BTT Store |
| A3 | NEMA 23 Stepper Motor | 1 | 57HS56-2804A — 2.8A, 1.8°/step, 1.26 N·m | $18–30 | StepperOnline, Amazon |
| A4 | SSD1306 OLED Display | 1 | 0.96", 128×64, I2C, white or blue | $4–7 | Amazon, AliExpress |
| A5 | KY-040 Rotary Encoder | 1 | With push-button, detent type | $2–4 | Amazon |
| A6 | Momentary Push Buttons | 3 | 12mm panel-mount, normally open | $3–5 | Amazon (pack) |
| A7 | 24V 5A Power Supply | 1 | Mean Well LRS-150-24 or equivalent | $15–25 | Amazon, Digi-Key |
| A8 | LM2596 Buck Converter | 1 | 24V → 5V, 3A module with trimpot | $2–4 | Amazon |

### A2 — Passive Components

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| A9 | 100µF 50V Electrolytic Cap | 1 | Near TMC2209 VM pin, radial lead | $0.50 | Digi-Key, Mouser |
| A10 | 10kΩ Resistors (¼W) | 4 | Pull-up: encoder CLK, DT, SW + buttons | $1 | Amazon (pack) |
| A11 | 1kΩ Resistor (¼W) | 1 | TMC2209 PDN_UART signal line | $0.10 | Amazon |

### A3 — Mechanical (Drive System)

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| A12 | GT2 Timing Pulley (Motor) | 1 | 20 Tooth, 6.35mm bore (¼" NEMA 23 shaft) | $3–5 | Amazon |
| A13 | GT2 Timing Pulley (Indexer) | 1 | 60 Tooth, bore to match indexer spindle | $6–10 | Amazon |
| A14 | GT2 Timing Belt (6mm wide) | 1 | 2mm pitch, length per center distance | $4–8 | Amazon (sold by meter) |
| A15 | NEMA 23 Mounting Bracket | 1 | Steel L-bracket or custom fabricated | $5–15 | Amazon, fabricate |
| A16 | Shaft Set Screws | AR | M3/M4, to secure pulleys to shafts | $3 | Amazon |
| A17 | GT2 Idler Tensioner (optional) | 1 | 20T smooth idler bearing, 3mm bore | $3–5 | Amazon |

### A4 — Enclosure & Wiring

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| A18 | Project Enclosure | 1 | ABS box ~150×100×60mm or 3D printed | $5–15 | Amazon |
| A19 | GX16-4 Aviation Connector | 1 set | 4-pin, panel + cable (motor disconnect) | $4 | Amazon |
| A20 | Prototype PCB / Perfboard | 1 | 70×90mm, double-sided, 2.54mm pitch | $2 | Amazon |
| A21 | Screw Terminal Blocks | 4 | 2-position, 5.08mm pitch | $2 | Amazon |
| A22 | DC Power Jack | 1 | 5.5×2.1mm barrel, panel-mount | $1 | Amazon |
| A23 | Toggle Switch (Power) | 1 | SPST, panel-mount, 10A | $2 | Amazon |
| A24 | 22 AWG Silicone Wire | 3m | Signal wiring, assorted colors | $3 | Amazon |
| A25 | 18 AWG Wire | 1m | Motor + power wiring | $2 | Amazon |
| A26 | Cable Glands (PG7/PG9) | 2–3 | Enclosure wire entry | $2 | Amazon |
| A27 | Heat Shrink Tubing | 1 set | Assorted sizes (2mm–10mm) | $3 | Amazon |
| A28 | Zip Ties | 1 pack | Small, for cable management | $2 | Amazon |

### ESP32 System Total: **$100–$170 USD**

---

## Section B: Watchmaker's Lathe Controller (Raspberry Pi)

### B1 — Computing & Display

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| B1 | Raspberry Pi 4B (4GB) | 1 | Pi 5 also works; 2GB minimum | $45–80 | PiShop, Amazon |
| B2 | Official Pi 7" Touchscreen | 1 | DSI ribbon, 800×480, capacitive touch | $60–75 | PiShop, Amazon |
| B3 | Touchscreen Case | 1 | SmartiPi Touch 2 or Pibow frame | $15–30 | Amazon |
| B4 | MicroSD Card (32GB+) | 1 | SanDisk Extreme or Samsung EVO Select | $8–12 | Amazon |
| B5 | USB-C Power Supply (Pi) | 1 | Official Pi PSU, 5V 3A | $8–12 | PiShop |

### B2 — Motor & Driver

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| B6 | NEMA 17 Stepper Motor (0.9°) | 1 | 42HS48-2004S — 2A, 0.44 N·m, 400 steps/rev | $15–25 | StepperOnline |
| B7 | TMC2209 Stepper Driver | 1 | BigTreeTech TMC2209 v1.3, UART mode | $6–10 | Amazon, BTT |
| B8 | 24V 3A Power Supply (Motor) | 1 | Mean Well LRS-75-24 or equivalent | $12–18 | Amazon, Digi-Key |
| B9 | 100µF 50V Electrolytic Cap | 1 | Near TMC2209 VM pin | $0.50 | Mouser |

> **Motor note:** Use a 0.9° motor (400 steps/rev) for maximum indexing resolution. At 256 microsteps with 3:1 ratio, this yields 307,200 steps per revolution (0.00117° resolution). For higher-torque applications or spindle RPM >3,000, consider a NEMA 23.

### B3 — RPM Sensor

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| B10a | Hall Effect Sensor (recommended) | 1 | KY-003 module (A3144 based), 3.3V safe | $2–4 | Amazon |
| B10b | Neodymium Magnet | 1 | 3×1mm disc, epoxied to spindle or pulley | $1 | Amazon |
| — | *OR Alternative:* | — | — | — | — |
| B10c | Optical Slot Sensor | 1 | KY-010 or TCPT1300X01 | $2–4 | Amazon |
| B10d | Slotted Disc | 1 | 3D printed, 1 slot per revolution | $0 | DIY |

> **Recommendation:** Hall effect + magnet is simpler, more robust in a dusty/oily shop environment, and requires no alignment. Glue a tiny magnet to the motor pulley or spindle.

### B4 — Input Controls

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| B11 | Rotary Encoder (Speed Knob) | 1 | KY-040 or Bourns PEC11R, 24 PPR | $3–8 | Amazon |
| B12 | Heavy Machined Knob | 1 | Aluminum, 25–38mm dia, D-shaft or set screw | $5–10 | Amazon |
| B13 | Momentary Push Buttons | 2 | 16mm panel-mount, NO, LED ring optional | $4–8 | Amazon |
| B14 | Emergency Stop Button | 1 | 22mm mushroom, **normally closed (NC)** | $5–8 | Amazon |
| B15 | Power Toggle Switch | 1 | DPST illuminated, 16A rated | $3–5 | Amazon |

> **E-STOP must be NC (normally closed).** A broken wire triggers E-STOP — this is a safety requirement.

### B5 — Mechanical (Drive System)

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| B16 | GT2 Timing Pulley (Motor) | 1 | 16T or 20T, 5mm bore (NEMA 17 shaft) | $3–5 | Amazon |
| B17 | GT2 Timing Pulley (Spindle) | 1 | 60T–80T, bore to match lathe spindle | $6–12 | Amazon |
| B18 | GT2 Timing Belt (6mm wide) | 1 | 2mm pitch, length per center distance | $4–8 | Amazon |
| B19 | Motor Mounting Bracket | 1 | Custom per lathe model (fab or 3D print) | $5–15 | Fabricate |
| B20 | GT2 Belt Tensioner Idler | 1 | Smooth idler bearing on adjustable arm | $3–5 | Amazon |

### B6 — Wiring & Enclosure

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| B21 | Aluminum Enclosure | 1 | 200×120×60mm or 3D printed | $10–20 | Amazon |
| B22 | GPIO Breakout / HAT Proto | 1 | Pi GPIO prototyping board | $5–10 | Amazon |
| B23 | Level Shifter (3.3V↔5V) | 1 | Bidirectional 4-channel, TXS0108E | $2–4 | Amazon |
| B24 | 10kΩ Resistors (¼W) | 5 | Pull-ups: sensor, encoder, buttons | $1 | Amazon |
| B25 | 1kΩ Resistors (¼W) | 2 | UART TX and RX lines to TMC2209 | $0.20 | Amazon |
| B26 | 22 AWG Silicone Wire | 3m | Signal wiring, assorted colors | $3 | Amazon |
| B27 | 18 AWG Wire | 1m | Motor + power wiring | $2 | Amazon |
| B28 | JST-XH Connectors | 1 set | Motor and sensor quick-connect | $4 | Amazon |
| B29 | GX12-4 Aviation Connector | 1 set | Motor quick-disconnect, 4-pin | $3 | Amazon |
| B30 | Cable Glands (PG7) | 3 | Enclosure wire entry | $2 | Amazon |

### Watchmaker System Total: **$240–$400 USD**

---

## Section C: Shared / Common Items

These items are identical between both projects. If building both, buy once:

| Component | Used In | Notes |
|-----------|---------|-------|
| GT2 Timing Belt (6mm) | Both | Same belt type; cut to length |
| TMC2209 Stepper Driver | Both | Identical driver board |
| 100µF 50V Cap | Both | Same spec |
| 10kΩ Resistors | Both | Same spec |
| 22 AWG Silicone Wire | Both | Same spec |
| 18 AWG Wire | Both | Same spec |
| Heat Shrink / Zip Ties | Both | Same spec |

---

## Section D: Tools Required

| Tool | Purpose | Needed For |
|------|---------|------------|
| Soldering iron + solder | All electrical connections | Both |
| Wire strippers | Preparing wire ends | Both |
| Wire crimpers | JST / aviation connectors | Watchmaker |
| Multimeter | Voltage verification, coil testing | Both |
| Drill + bits | Enclosure panel holes, mounting | Both |
| Allen wrenches (metric) | Pulley set screws (M3, M4) | Both |
| USB-C cable | Programming ESP32 | ESP32 |
| USB keyboard + mouse | Initial Pi setup | Watchmaker |
| Computer with VS Code | Firmware development | ESP32 |
| Adjustable wrench | Motor bracket mounting | Both |
| File / deburring tool | Clean drilled holes | Both |

---

## Section E: Optional Upgrades

| Upgrade | Part | Purpose | System |
|---------|------|---------|--------|
| Closed-loop encoder | AS5600 magnetic encoder | Position verification, stall detection | Both |
| Larger OLED | SH1106 1.3" OLED (I2C) | Easier to read in shop | ESP32 |
| Foot pedal | USB sustain pedal | Hands-free speed control | Watchmaker |
| Coolant pump | 12V peristaltic pump | Controlled from GPIO | Watchmaker |
| Chip guard | 3D-printed shield | Protect encoder/sensor from swarf | Both |
| WiFi dashboard | Built into Pi / ESP32 | Remote RPM monitoring | Both |
| Camera | Pi Camera Module v3 | Magnification for fine work | Watchmaker |
| Tachometer display | 7-segment LED, 4-digit | Always-visible RPM readout | Both |
| Emergency stop (ESP32) | NC mushroom button | Safety for powered operation | ESP32 |
| Dust cover | 3D-printed shroud | Protect belt/pulleys from chips | Both |

---

## Section F: Spindle Pulley Selection by Lathe

The motor-side pulley is standard (20T GT2, 5mm bore). The spindle-side pulley depends on your lathe:

| Lathe | Spindle Shaft | Recommended Pulley | Notes |
|-------|--------------|--------------------|----|
| **Sherline** | 3/4"-16 thread / ER16 nose | GT2 60T, 3/4" bore or adapter | Mounts to spindle nose |
| **Levin** | 8mm or 10mm smooth | GT2 60T, match bore | Replaces headstock pulley |
| **Boley F1** | Smooth, round-belt pulley | GT2 60T + adapter sleeve | 3D print or machine adapter |
| **Lorch KD50** | Belt-drive compatible | GT2 60T, match bore | Direct mounting |
| **Taig Micro** | 1/2" (12.7mm) | GT2 60T, 12.7mm bore | Direct swap |
| **Cowells ME90** | Belt-drive | GT2 60T, match bore | Direct swap |
| **HHIP 5C Jig** | Varies | GT2 60T + bracket | Custom bracket recommended |

**If the bore doesn't match:** Use a shaft bushing/sleeve (e.g., 5mm→8mm, 8mm→10mm), or bore out an aluminum pulley on the lathe before converting it. GT2 pulleys can also be 3D-printed — adequate for the low torques in watchmaking.

### Belt Length Calculation

$$L = 2C + \pi \cdot \frac{D_1 + D_2}{2} + \frac{(D_2 - D_1)^2}{4C}$$

Where:
- $C$ = center distance between motor and spindle shafts (mm)
- $D_1$ = pitch diameter of small pulley = $\frac{\text{teeth} \times 2}{\pi}$ (mm)
- $D_2$ = pitch diameter of large pulley = $\frac{\text{teeth} \times 2}{\pi}$ (mm)

**Example:** 20T + 60T pulleys, 100mm center distance:
- $D_1 = \frac{20 \times 2}{\pi} = 12.73$ mm
- $D_2 = \frac{60 \times 2}{\pi} = 38.20$ mm
- $L = 200 + \pi \cdot 25.46 + \frac{649.2}{400} = 200 + 79.96 + 1.62 \approx 282$ mm

Use a **280mm or 300mm closed-loop GT2 belt**, or cut from open belt stock.

### Recommended Gear Ratios

| Application | Motor Pulley | Spindle Pulley | Ratio | RPM Range | Resolution |
|-------------|-------------|----------------|-------|-----------|------------|
| General turning | 20T | 60T | 3:1 | 50–2,700 | 0.0033° |
| Fine work + indexing | 16T | 80T | 5:1 | 50–1,600 | 0.0018° |
| High-speed drilling | 30T | 30T | 1:1 | 50–8,000 | 0.0088° |
| Gear cutting (slow) | 16T | 80T | 5:1 | 50–1,600 | 0.0018° |

---

## Section G: Sourcing Notes

- **Amazon** — Fastest shipping, moderate prices. Good for one-offs.
- **AliExpress** — Cheapest, 2–4 week shipping. Best for bulk or non-urgent.
- **StepperOnline** — Best selection of stepper motors with detailed specs.
- **Digi-Key / Mouser** — Best for precision components (caps, resistors). Free shipping over $50.
- **BigTreeTech (BTT)** — Direct source for TMC2209 driver boards.
- **PiShop.us / PiHut.com** — Authorized Pi distributors, best stock availability.
- **McMaster-Carr** — Pulleys, belts, brackets, fasteners (higher cost, fast shipping, exact specs).

> **Tip:** A single Amazon order can cover 80% of the BOM for either project. The motor and Pi are the only items that benefit from sourcing from specialists.

---

*Consolidated materials list — March 2026*
