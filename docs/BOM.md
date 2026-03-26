# Bill of Materials (BOM)

## HHIP 5C Indexing Spin Jig — Stepper Controller

### Electronics

| # | Component | Qty | Recommended Part | Est. Cost | Source |
|---|-----------|-----|------------------|-----------|--------|
| 1 | ESP32 DevKit V1 (38-pin) | 1 | ESP-WROOM-32 DevKit | $8–12 | Amazon, AliExpress |
| 2 | TMC2209 Stepper Driver | 1 | BigTreeTech TMC2209 v1.3 | $6–10 | Amazon, BTT Store |
| 3 | NEMA 23 Stepper Motor | 1 | 57HS56-2804A (2.8A, 1.8°, 1.26 N·m) | $18–30 | StepperOnline, Amazon |
| 4 | SSD1306 OLED Display 128×64 | 1 | 0.96" I2C White/Blue | $4–7 | Amazon, AliExpress |
| 5 | KY-040 Rotary Encoder | 1 | With push-button, detent type | $2–4 | Amazon |
| 6 | Momentary Push Buttons | 3 | 12mm panel-mount, NO | $3–5 (pack) | Amazon |
| 7 | 24V 5A Power Supply | 1 | Mean Well LRS-150-24 or equivalent | $15–25 | Amazon, Digi-Key |
| 8 | LM2596 Buck Converter | 1 | 24V → 5V, 3A module | $2–4 | Amazon |
| 9 | 100µF 50V Electrolytic Cap | 1 | Near TMC2209 VM pin | $0.50 | Digi-Key, Mouser |
| 10 | 10kΩ Resistors | 4 | Pull-up for buttons/encoder | $1 (pack) | Amazon |
| 11 | 1kΩ Resistor | 1 | TMC2209 UART line | $0.10 | Amazon |
| 12 | Prototype PCB / Perfboard | 1 | 70×90mm double-sided | $2 | Amazon |
| 13 | Screw Terminal Blocks (2P) | 4 | 5.08mm pitch | $2 (pack) | Amazon |
| 14 | DC Power Jack | 1 | 5.5×2.1mm barrel panel-mount | $1 | Amazon |
| 15 | Toggle Switch | 1 | SPST, panel-mount (main power) | $2 | Amazon |

### Mechanical — Drive System

| # | Component | Qty | Specification | Est. Cost | Source |
|---|-----------|-----|---------------|-----------|--------|
| 16 | GT2 Timing Pulley (Motor) | 1 | 20 Tooth, 6mm bore (or match motor shaft) | $3–5 | Amazon |
| 17 | GT2 Timing Pulley (Indexer) | 1 | 60 Tooth, bore to match indexer spindle | $6–10 | Amazon |
| 18 | GT2 Timing Belt (6mm) | 1 | Length per your center distance | $4–8 | Amazon |
| 19 | Motor Mounting Bracket | 1 | NEMA 23 L-bracket or custom | $5–15 | Amazon / fabricate |
| 20 | Shaft Coupler / Set Screws | AR | To secure pulleys | $3 | Amazon |
| 21 | Belt Tensioner (optional) | 1 | Idler pulley + spring | $5 | Amazon |

### Enclosure & Wiring

| # | Component | Qty | Notes | Est. Cost | Source |
|---|-----------|-----|-------|-----------|--------|
| 22 | Project Enclosure | 1 | ABS box ~150×100×60mm or 3D print | $5–15 | Amazon |
| 23 | GX16-4 Aviation Connector | 1 set | Motor quick-disconnect (panel + cable) | $4 | Amazon |
| 24 | 22 AWG Silicone Wire | 3m | Signal wiring | $3 | Amazon |
| 25 | 18 AWG Wire | 1m | Motor + power wiring | $2 | Amazon |
| 26 | Cable Glands (PG7/PG9) | 2–3 | Enclosure entry points | $2 | Amazon |
| 27 | Heat Shrink Tubing | 1 set | Assorted sizes | $3 | Amazon |
| 28 | Zip Ties | 1 pack | Cable management | $2 | Amazon |

---

### Estimated Total: **$100–$170 USD**

> Prices are approximate (2025–2026). Many items are cheaper in multi-packs or from AliExpress with longer shipping times.

---

## Tools Required

- Soldering iron + solder
- Wire strippers
- Multimeter
- Drill (for enclosure holes)
- Allen wrenches (pulley set screws)
- USB-C cable (ESP32 programming)
- Computer with VS Code + PlatformIO

## Optional Upgrades

| Upgrade | Part | Purpose |
|---------|------|---------|
| Closed-loop feedback | AS5600 magnetic encoder | Verify position, detect stalls |
| Larger display | SH1106 1.3" OLED | Easier to read |
| WiFi control | (built into ESP32) | Future: phone/tablet UI |
| Emergency stop | NC mushroom button | Safety for powered operation |
| Dust cover | 3D-printed shroud | Protect belt/pulleys from chips |
