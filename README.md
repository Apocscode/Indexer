# Index — 5C Indexing Spin Jig Stepper Controller

## HHIP 5C Indexing Spin Jig (3900-1604) — Automated Stepper Motor Control

A complete hardware and firmware solution to automate a HHIP 5C Indexing Spin Jig using a stepper motor, timing belt/pulley drive, and an ESP32 microcontroller. The system handles all division math automatically, provides common indexing presets, and offers a simple rotary-encoder + OLED interface for shop-floor use.

---

## Features

- **Automatic Division Math** — Enter the number of divisions and the system calculates exact step counts, accounting for microstepping and gear ratio.
- **Common Presets** — One-click access to frequently used patterns: hex (6), square (4), gear teeth (12–72+), bolt circles, and more.
- **Precise Microstepping** — TMC2209 driver with up to 256 microsteps for ultra-smooth, backlash-free positioning.
- **Belt-Drive Coupling** — Timing belt and notched pulleys eliminate backlash between motor and indexer spindle.
- **Jog Mode** — Manually jog in fine increments (0.1° / 1° / 10°) for alignment.
- **Position Tracking** — Absolute position display with return-to-zero.
- **OLED Display** — Crisp 128×64 OLED shows current position, target, divisions, and mode.
- **Rotary Encoder + Buttons** — Glove-friendly input for shop use.
- **Configurable Gear Ratio** — Software-adjustable to match your pulley combination.

---

## Hardware Overview

| Component | Recommended Part | Notes |
|---|---|---|
| Microcontroller | ESP32 DevKit V1 (38-pin) | WiFi-capable, fast, plenty of GPIO |
| Stepper Driver | BigTreeTech TMC2209 v1.3 | UART mode, silent, up to 256 microsteps |
| Stepper Motor | NEMA 23 — 2.8A, 1.8°/step | 200 steps/rev; torque to hold indexer |
| Display | SSD1306 128×64 OLED (I2C) | Bright, readable, low power |
| Input | KY-040 Rotary Encoder | With push-button built in |
| Buttons | 3× momentary pushbuttons | MODE, PRESET, GO / STOP |
| Power Supply | 24V 5A switching PSU | Powers motor; ESP32 via buck converter |
| Buck Converter | LM2596 24V→5V module | Powers ESP32 from motor PSU |
| Timing Belt | GT2 6mm belt | Match length to your pulley spacing |
| Pulleys | GT2 20T (motor) / GT2 60T (indexer)* | *Adjust to your setup — 3:1 shown |
| Enclosure | Project box or 3D-printed | Protect electronics |
| Connectors | 4-pin aviation (GX16) for motor | Quick-disconnect |

> **Gear Ratio Note:** The firmware defaults to a 3:1 ratio (20T motor → 60T indexer). Change `GEAR_RATIO_NUMERATOR` and `GEAR_RATIO_DENOMINATOR` in `config.h` to match your actual pulleys.

---

## Wiring Diagram

See [docs/WIRING.md](docs/WIRING.md) for the full wiring guide.

### Quick Reference

```
ESP32 Pin    →  Connection
─────────────────────────────
GPIO 16      →  TMC2209 STEP
GPIO 17      →  TMC2209 DIR
GPIO 18      →  TMC2209 EN (active LOW)
GPIO 19 (TX) →  TMC2209 PDN_UART (via 1kΩ)
GPIO 21      →  OLED SDA
GPIO 22      →  OLED SCL
GPIO 32      →  Encoder CLK
GPIO 33      →  Encoder DT
GPIO 25      →  Encoder SW (push)
GPIO 26      →  Button: MODE
GPIO 27      →  Button: PRESET
GPIO 14      →  Button: GO/STOP
GND          →  Common ground
5V (buck)    →  ESP32 VIN
24V PSU      →  TMC2209 VM + buck converter input
```

---

## Software Architecture

```
firmware/
├── platformio.ini          # PlatformIO build config
├── src/
│   ├── main.cpp            # Setup + main loop
│   ├── config.h            # Pin definitions, gear ratio, steps
│   ├── stepper.h / .cpp    # Stepper motor control (accel/decel)
│   ├── indexer.h / .cpp     # Division math engine
│   ├── display.h / .cpp    # OLED UI rendering
│   ├── input.h / .cpp      # Encoder + button handling
│   └── presets.h / .cpp    # Common indexing presets
└── docs/
    ├── WIRING.md           # Detailed wiring guide
    ├── BOM.md              # Full bill of materials
    └── SETUP.md            # First-time calibration
```

---

## Getting Started

1. **Assemble hardware** per [docs/WIRING.md](docs/WIRING.md)
2. **Install PlatformIO** (VS Code extension recommended)
3. **Clone/open** this project in VS Code
4. **Edit `config.h`** — set your gear ratio and verify pin assignments
5. **Build & Upload:** `pio run -t upload`
6. **Calibrate:** Follow [docs/SETUP.md](docs/SETUP.md)

---

## Indexing Math

The core formula:

$$\text{Steps per division} = \frac{\text{Motor steps/rev} \times \text{Microsteps} \times \text{Gear Ratio}}{\text{Number of divisions}}$$

Example: 24 divisions with 200-step motor, 16 microsteps, 3:1 gear ratio:

$$\frac{200 \times 16 \times 3}{24} = 400 \text{ steps per index}$$

The firmware handles non-integer results via Bresenham-style error accumulation — no division is ever skipped or rounded.

---

## License

MIT — Use freely for personal and commercial projects.
