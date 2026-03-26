# Indexer — Project Report

## Stepper Motor Indexing & Lathe Controller System

**Repository:** [github.com/Apocscode/Indexer](https://github.com/Apocscode/Indexer)
**Date:** March 2026
**Status:** Firmware complete · GUI complete · Ready for hardware build

---

## 1. Executive Summary

This project delivers two complete stepper-motor control systems for precision angular positioning:

1. **ESP32 Indexing Controller** — A standalone firmware for automating an HHIP 5C Indexing Spin Jig (3900-1604). Uses an ESP32 microcontroller, TMC2209 stepper driver, OLED display, and rotary encoder. Designed for machine shop use: bolt circles, gear blanks, hex features, etc.

2. **Watchmaker's Lathe Controller** — A Raspberry Pi-based system with a 7" touchscreen GUI for controlling a watchmaker's lathe. Adds variable-speed spindle control with PID-regulated RPM, a hall-effect RPM sensor, and 120+ watchmaking-specific indexing presets (escape wheels, train wheels, pinions, etc.).

Both systems use GT2 timing belts for zero-backlash mechanical coupling and Bresenham-algorithm division math for zero cumulative positioning error.

---

## 2. System Architecture

### 2.1 ESP32 Indexing Controller

```
┌──────────────────────────────────────────────────────┐
│                    ESP32 DevKit V1                    │
│                                                      │
│  Inputs:               Core:              Outputs:   │
│  ┌──────────┐    ┌──────────────┐    ┌────────────┐  │
│  │ Rotary   │───►│ Division     │───►│ TMC2209    │  │
│  │ Encoder  │    │ Math Engine  │    │ Stepper    │  │
│  ├──────────┤    │ (Bresenham)  │    │ Driver     │  │
│  │ MODE Btn │───►│              │    ├────────────┤  │
│  │ PRESET   │───►│ Preset       │───►│ NEMA 23    │  │
│  │ GO/STOP  │───►│ Library      │    │ Motor      │  │
│  └──────────┘    └──────────────┘    ├────────────┤  │
│                                      │ SSD1306    │  │
│                                      │ OLED 128×64│  │
│                                      └────────────┘  │
└──────────────────────────────────────────────────────┘
          │                                    │
          └────── GT2 Timing Belt ─────────────┘
                         │
              ┌──────────────────┐
              │ HHIP 5C Indexing │
              │ Spin Jig         │
              │ (3900-1604)      │
              └──────────────────┘
```

**Key Specs:**
- Motor: NEMA 23, 200 steps/rev, 1.8°
- Microstepping: 16 (configurable up to 256)
- Gear ratio: 3:1 (20T motor → 60T indexer)
- Total resolution: 9,600 steps/revolution (0.0375° per step)
- Max stepping speed: 4,000 steps/sec
- Acceleration: 2,000 steps/sec²

**Operating Modes:**
- **Index mode** — Set number of divisions, press GO to advance
- **Jog mode** — Manual jog in 0.1°, 1°, or 10° increments
- **Preset mode** — Quick-select common division counts
- **Continuous mode** — Free rotation at set speed

### 2.2 Watchmaker's Lathe Controller

```
┌──────────────────────────────────────────────────────────────────┐
│                      Raspberry Pi 4B                             │
│                                                                  │
│  Hardware:              Software:               GUI:             │
│  ┌──────────┐    ┌────────────────┐    ┌──────────────────┐     │
│  │ Rotary   │───►│ StepperMotor   │    │ 7" Touchscreen   │     │
│  │ Encoder  │    │ (pigpio waves) │    │ 800×480          │     │
│  ├──────────┤    ├────────────────┤    │                  │     │
│  │ Buttons  │───►│ PID Controller │    │ ┌──────────────┐ │     │
│  │ MODE     │    │ (20 Hz loop)   │    │ │ Lathe Page   │ │     │
│  │ GO/STOP  │    ├────────────────┤    │ │ RPM gauge    │ │     │
│  │ E-STOP   │    │ RPM Sensor     │    │ │ RPM graph    │ │     │
│  ├──────────┤    │ (Hall effect)  │    │ │ Speed slider │ │     │
│  │ Hall     │───►├────────────────┤    │ ├──────────────┤ │     │
│  │ Effect   │    │ Indexer        │    │ │ Index Page   │ │     │
│  │ Sensor   │    │ (Bresenham)    │    │ │ Div ring     │ │     │
│  └──────────┘    ├────────────────┤    │ │ Navigation   │ │     │
│                  │ Presets (120+) │    │ ├──────────────┤ │     │
│                  │ Watchmaking    │    │ │ Presets Page  │ │     │
│                  └────────────────┘    │ ├──────────────┤ │     │
│                                       │ │ Settings     │ │     │
│                                       │ └──────────────┘ │     │
│                                       └──────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
          │                                        │
          └─────────── GT2 Timing Belt ────────────┘
                            │
                 ┌─────────────────────┐
                 │  Watchmaker's Lathe │
                 │  (Levin, Boley,     │
                 │   Sherline, etc.)   │
                 └─────────────────────┘
```

**Key Specs:**
- Motor: NEMA 17, 400 steps/rev, 0.9°
- Microstepping: 256 (configurable)
- Gear ratio: 3:1 default (20T motor → 60T spindle), configurable
- Total resolution: 307,200 steps/revolution (0.00117° per step)
- RPM range: 50–8,000 at spindle
- PID-controlled RPM regulation at 20 Hz update rate

**Operating Modes:**
- **Lathe mode** — Variable speed control with RPM gauge, PID or open-loop
- **Index mode** — Precision division with visual ring display
- **Preset browser** — 120+ watchmaking presets, searchable by category

---

## 3. Division Math — Bresenham Algorithm

Both controllers use a Bresenham-style error accumulation algorithm to distribute steps evenly across divisions, guaranteeing **zero cumulative error** over a full revolution.

### The Problem

With 9,600 total steps and 7 divisions:

$$\frac{9600}{7} = 1371.4286...$$

Simple rounding (1371 steps × 7 = 9597) loses 3 steps per revolution, causing progressive drift.

### The Solution

Bresenham distribution spreads the remainder across divisions:

```
Division 1:  1372 steps  (error accumulated, extra step added)
Division 2:  1371 steps
Division 3:  1372 steps  (extra step)
Division 4:  1371 steps
Division 5:  1372 steps  (extra step)
Division 6:  1371 steps
Division 7:  1371 steps
─────────────────────────
Total:       9600 steps  ← exact
```

After any number of full revolutions, the position returns to exactly zero. This is critical for indexing operations where cumulative error would produce misaligned features.

---

## 4. Software Components

### 4.1 ESP32 Firmware (C++ / Arduino / PlatformIO)

| File | Purpose |
|------|---------|
| `config.h` | Pin assignments, motor parameters, gear ratio |
| `stepper.h/.cpp` | AccelStepper wrapper with TMC2209 UART configuration |
| `indexer.h/.cpp` | Bresenham division engine |
| `display.h/.cpp` | SSD1306 OLED UI rendering |
| `input.h/.cpp` | Rotary encoder + button handling with debounce |
| `presets.h/.cpp` | Common division presets |
| `main.cpp` | Setup + main loop |

**Libraries:** AccelStepper, TMCStepper, Adafruit SSD1306, Adafruit GFX

### 4.2 Watchmaker Python Application (Python 3 / tkinter / pigpio)

| File | Purpose |
|------|---------|
| `config.py` | INI loader with typed dataclasses |
| `motor.py` | Stepper control via pigpio wave chains |
| `rpm_sensor.py` | Hall effect interrupt-based RPM measurement |
| `pid.py` | Discrete PID with anti-windup and configurable gains |
| `indexer.py` | Bresenham division engine (Python port) |
| `presets.py` | 120+ watchmaking presets across 15 categories |
| `input_hw.py` | Rotary encoder + button polling via pigpio |
| `gui/app.py` | Main tkinter application + AppController bridge |
| `gui/widgets.py` | Custom widgets: RPM gauge, graph, division ring |
| `gui/lathe_page.py` | Variable-speed lathe control page |
| `gui/index_page.py` | Division/indexing control page |
| `gui/preset_page.py` | Searchable preset browser |
| `gui/settings_page.py` | Tabbed configuration editor |
| `main.py` | Entry point with argparse and hardware init |

---

## 5. Mechanical Design

### Belt Drive System

Both systems use a **GT2 timing belt** (2mm pitch, 6mm wide) for zero-backlash power transmission between the stepper motor and the workholding spindle.

**Component chain:**
```
NEMA Motor Shaft → GT2 Small Pulley → GT2 Belt → GT2 Large Pulley → Spindle
     (5mm)           (20T, 5mm bore)   (6mm)     (60T, bore varies)
```

**Gear ratio** is determined by pulley tooth counts:

$$\text{Ratio} = \frac{\text{Spindle pulley teeth}}{\text{Motor pulley teeth}} = \frac{60}{20} = 3:1$$

This means:
- The motor turns **3 times** for each spindle revolution
- Torque at the spindle is **3× motor torque**
- Angular resolution is **3× finer** than the motor alone
- Maximum spindle RPM is **⅓ of motor max RPM**

### Lathe Mounting

The motor mounts to the lathe bed or headstock via a custom bracket (L-bracket for most lathes, 3D-printed adapter for others). The large pulley either:
- **Replaces** the existing headstock pulley (Levin, Taig, Cowells)
- **Adapts over** the existing pulley (Boley, Lorch)
- **Mounts to** the spindle nose or collet system (Sherline)

### Belt Tensioning

A spring-loaded GT2 idler bearing provides adjustable belt tension. Target: 3–5mm deflection at the belt midpoint when pressed with a finger.

---

## 6. Safety Features

| Feature | Implementation |
|---------|---------------|
| Emergency stop | NC (normally closed) mushroom button — fail-safe on wire break |
| Motor disable | EN pin driven HIGH to cut motor current |
| Soft start | Configurable ramp-up time (default 1000ms) |
| Deceleration | Controlled ramp-down, not instant stop (prevents step loss) |
| Hold current reduction | Idle current drops to 33–50% to reduce heat |
| PID output limits | Output clamped to 0.0–1.0 prevents runaway |
| Anti-windup | PID integral term capped to prevent windup oscillation |
| Over-speed protection | Software-enforced max RPM limit |

---

## 7. Supported Lathes

| Lathe | Type | Spindle Connection | Difficulty |
|-------|------|-------------------|------------|
| Sherline | Hobby/micro | ER16 nose or standard, motor pulley on bed | Easy |
| Levin | Watchmaker's | Replace headstock pulley | Easy |
| Boley F1 | Instrument | Adapter over round-belt pulley | Moderate |
| Lorch KD50 | Instrument | Belt-drive compatible | Easy |
| Taig Micro | Micro lathe | Direct pulley swap (1/2" shaft) | Easy |
| Cowells ME90 | Model engineering | Belt drive, direct swap | Easy |
| HHIP 5C Jig | Indexing fixture | Dedicated bracket + pulley | Easy |

---

## 8. Preset Library (Watchmaker)

The watchmaker controller includes 120+ presets organized into 15 categories:

| Category | Examples | Count |
|----------|----------|-------|
| Escape Wheels | Club tooth (15T), Swiss lever (20T), English lever (15T) | 8+ |
| Train Wheels | Center wheel (80T), Third wheel (75T), Fourth wheel (60T) | 10+ |
| Pinions | Escape pinion (7–10), Center pinion (10–12) | 8+ |
| Winding | Crown wheel (varies), Ratchet wheel (varies) | 6+ |
| Motion Work | Hour wheel (36T), Minute wheel (varies), Cannon pinion | 8+ |
| Chronograph | Column wheel (7–9), Coupling wheel, Heart cam (2) | 6+ |
| Clock | Great wheel (96–144T), Center (64T), Escape wheel (30T) | 8+ |
| Dials & Decoration | Hour markers (12), Minute markers (60), Guilloche | 8+ |
| Geometric | Triangle (3), Square (4), Pentagon (5), Hexagon (6) | 10+ |
| Degrees | 1° (360), 5° (72), 15° (24), 30° (12), 45° (8), 90° (4) | 10+ |
| Fasteners | Socket head (6), Spanner (2), Torx (6), Phillips (4) | 8+ |
| Flutes | 2-flute, 3-flute, 4-flute, 6-flute, 8-flute | 6+ |
| Splines | 6-spline, 8-spline, 12-spline, 24-spline, 36-spline | 6+ |
| Knurling | Fine straight (120), Medium diamond (90), Coarse (60) | 6+ |
| Miscellaneous | Custom entry, common primes | Various |

---

## 9. Cost Summary

| System | Total Estimate | Key Components |
|--------|---------------|----------------|
| ESP32 Indexing Controller | $100–$170 | ESP32 + TMC2209 + NEMA 23 + OLED + PSU |
| Watchmaker's Lathe Controller | $240–$400 | Pi 4B + 7" touchscreen + NEMA 17 + TMC2209 + PSU + sensor |

---

## 10. File Structure

```
Indexer/
├── README.md                     ← Project overview
├── docs/
│   ├── REPORT.md                 ← This document
│   ├── MATERIALS.md              ← Consolidated materials list
│   ├── ASSEMBLY.md               ← Step-by-step assembly guide
│   ├── WIRING_COMPLETE.md        ← Combined wiring reference
│   ├── BOM.md                    ← ESP32 bill of materials
│   ├── WIRING.md                 ← ESP32 wiring diagram
│   └── SETUP.md                  ← ESP32 setup/calibration
├── firmware/                     ← ESP32 Arduino/PlatformIO
│   ├── platformio.ini
│   └── src/
│       ├── main.cpp
│       ├── config.h
│       ├── stepper.h / .cpp
│       ├── indexer.h / .cpp
│       ├── display.h / .cpp
│       ├── input.h / .cpp
│       └── presets.h / .cpp
└── watchmaker/                   ← Raspberry Pi Python
    ├── config.ini
    ├── requirements.txt
    ├── install.sh / run.sh
    ├── docs/
    │   ├── BOM.md
    │   ├── WIRING.md
    │   └── SETUP.md
    └── src/
        ├── main.py
        ├── config.py
        ├── motor.py
        ├── rpm_sensor.py
        ├── pid.py
        ├── indexer.py
        ├── presets.py
        ├── input_hw.py
        └── gui/
            ├── app.py
            ├── widgets.py
            ├── lathe_page.py
            ├── index_page.py
            ├── preset_page.py
            └── settings_page.py
```

---

## 11. Future Enhancements

- **Closed-loop feedback** — AS5600 magnetic encoder for position verification
- **WiFi dashboard** — Remote RPM monitoring via Pi's built-in WiFi
- **Foot pedal** — USB sustain pedal for hands-free speed control
- **G-code input** — Accept simple G-code for automated multi-step operations
- **Data logging** — RPM/position history export to CSV
- **Camera integration** — Pi Camera for magnified viewing of fine work
- **Multi-motor** — Support for compound slide or cross-slide stepper

---

*Generated March 2026 — Apocscode/Indexer*
