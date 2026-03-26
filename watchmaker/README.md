# Watchmaker's Lathe Controller

## Raspberry Pi–Based Variable Speed & Indexing Controller for Watchmaker's Lathes

A dual-purpose controller that provides **variable-speed lathe operation** (with closed-loop RPM control) and **precision indexing/dividing** — purpose-built for watchmaking, micro-gear cutting, and horological repair work.

---

## Why This Exists

Watchmaker's lathes (Sherline, Taig, Levin, Boley, Lorch, Schaublin 70/102) need two things that don't normally coexist:

1. **Smooth variable speed** — from 50 RPM (hand polishing, burnishing pivots) up to 8,000+ RPM (drilling, turning steel)
2. **Precision indexing** — for cutting escape wheels (15T), third wheels (75T), minute wheels (various), barrel teeth, and other horological gears with exact tooth counts

This project replaces both a variable-speed motor controller AND a dividing head/indexing attachment with a single Raspberry Pi–based system using a closed-loop stepper motor.

---

## Features

### Lathe / Variable Speed Mode
- **Continuous rotation** at a set RPM with real-time PID speed control
- **RPM range:** 50–8,000 RPM (configurable per setup)
- **Physical speed knob** — rotary encoder for intuitive analog-feel speed control
- **RPM sensor feedback** — optical or Hall-effect sensor for closed-loop regulation
- **Live RPM display** on touchscreen
- **Soft start / soft stop** — configurable ramp rates to protect delicate workpieces
- **Direction toggle** — forward / reverse

### Indexing / Dividing Mode
- **Automatic division math** — enter tooth count, system calculates exact steps
- **Bresenham error distribution** — no cumulative error over 360°
- **Watchmaking presets** — 80+ presets for common watch wheels, gears, and operations
- **Jog mode** — fine positioning in 0.01° / 0.1° / 1° increments
- **Absolute position tracking** — always know where you are

### Interface
- **7" Touchscreen** — large, readable GUI with dedicated screens per mode
- **Rotary encoder knob** — physical speed control, also used for menu navigation
- **Hardware buttons** — MODE, GO/STOP, E-STOP for glove-safe operation
- **Live graphs** — RPM history plot for speed stability monitoring

---

## Hardware Overview

| Component | Recommended Part | Notes |
|---|---|---|
| Computer | Raspberry Pi 4B (2GB+) or Pi 5 | Python GUI, GPIO, plenty of power |
| Display | Official Pi 7" Touchscreen | DSI connection, capacitive touch |
| Stepper Motor | NEMA 17 Closed-Loop (2A, 0.9°) | 400 steps/rev for finer resolution |
| Stepper Driver | BigTreeTech TMC2209 | UART mode, silent, up to 256 µsteps |
| RPM Sensor | KY-003 Hall Effect + magnet | Or optical slot sensor (KY-010) |
| Speed Knob | KY-040 Rotary Encoder (100 PPR) | Heavy-duty knob for feel |
| Buttons | Panel-mount momentary (3×) | MODE, GO/STOP, E-STOP (NC, mushroom) |
| Power Supply | 24V 3A (motor) + 5V 3A (Pi) | Separate supplies recommended |
| Buck Converter | — | Not needed if using separate 5V PSU |
| Timing Belt | GT2 6mm + pulleys | Match to your lathe spindle |
| Motor Mount | Custom bracket/3D print | Per your specific lathe |

> **Motor choice note:** A 0.9° stepper (400 steps/rev) at 256 microsteps through a 4:1 gear ratio gives **409,600 steps/rev** — that's 0.00088° per step, far exceeding any watchmaking indexing requirement.

---

## Software Architecture

```
watchmaker/
├── requirements.txt        # Python dependencies
├── install.sh              # First-time Pi setup script
├── run.sh                  # Launch script
├── config.ini              # User configuration (gear ratio, pins, etc.)
│
├── src/
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration loader
│   ├── motor.py            # Stepper motor driver (GPIO + TMC2209)
│   ├── rpm_sensor.py       # Hall/optical RPM sensor (interrupt-driven)
│   ├── pid.py              # PID controller for RPM regulation
│   ├── indexer.py          # Division math engine (from Index project)
│   ├── presets.py          # Watchmaking-specific presets
│   ├── input_hw.py         # Rotary encoder + buttons (GPIO)
│   └── gui/
│       ├── app.py          # Main tkinter application
│       ├── lathe_page.py   # Variable speed / RPM control screen
│       ├── index_page.py   # Indexing / dividing screen
│       ├── preset_page.py  # Preset browser screen
│       ├── settings_page.py# Configuration / setup screen
│       └── widgets.py      # Reusable UI components (gauges, graphs)
│
└── docs/
    ├── BOM.md              # Bill of materials
    ├── WIRING.md           # Wiring guide
    └── SETUP.md            # Installation & calibration
```

---

## Indexing Math

Same proven formula from the Index project:

$$\text{Steps per division} = \frac{\text{Motor steps/rev} \times \text{Microsteps} \times \text{Gear Ratio}}{\text{Number of divisions}}$$

Example — cutting an 18-tooth escape wheel with 400-step motor, 256 µsteps, 4:1 ratio:

$$\frac{400 \times 256 \times 4}{18} = 22{,}755.6 \text{ steps/div}$$

The Bresenham algorithm distributes the fractional remainder so that after 18 divisions you're at **exactly** 409,600 steps (one full revolution) — zero cumulative error.

---

## RPM Control

The PID loop:

$$u(t) = K_p \cdot e(t) + K_i \int e(t)\,dt + K_d \frac{de}{dt}$$

Where $e(t) = \text{RPM}_\text{target} - \text{RPM}_\text{measured}$

The controller adjusts the step pulse frequency to maintain the target RPM, measured via the Hall-effect sensor. Sampling rate: 20 Hz. PID is auto-tuned on first run.

---

## Getting Started

1. **Assemble hardware** per [docs/WIRING.md](docs/WIRING.md)
2. **Flash Raspberry Pi OS** (64-bit Lite or Desktop)
3. **Run installer:** `chmod +x install.sh && ./install.sh`
4. **Edit `config.ini`** — set your gear ratio and pin assignments
5. **Launch:** `./run.sh` or auto-start on boot

---

## License

MIT — Use freely for personal and commercial projects.
