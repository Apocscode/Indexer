# Wiring Guide — Watchmaker's Lathe Controller

## Raspberry Pi GPIO Pinout

---

## Power Distribution

```
┌─────────────────┐                    ┌──────────────┐
│  5V 3A USB-C    │───────────────────►│ Raspberry Pi │
│  (Pi PSU)       │                    │              │
└─────────────────┘                    └──────────────┘

┌─────────────────┐
│  24V 3A PSU     │
│                 │
│  V+ ────────────┬──── TMC2209 VM (+ 100µF cap across VM/GND)
│                 │
│  V- ────────────┬──── TMC2209 GND ──── Pi GND (common ground!)
│                 │
│  (Earth) ───────── Enclosure ground
└─────────────────┘
```

> **CRITICAL:** The Pi GND and motor PSU GND **must** share a common ground. Connect them at a single star-ground point.

---

## Raspberry Pi GPIO Assignments

```
Pin#  GPIO   Function           Direction    Connection
────────────────────────────────────────────────────────────
 11   GPIO17  STEP              Output  ──►  TMC2209 STEP
 13   GPIO27  DIR               Output  ──►  TMC2209 DIR
 15   GPIO22  ENABLE            Output  ──►  TMC2209 EN (active LOW)
 08   GPIO14  UART TX           Output  ──►  TMC2209 PDN_UART (via 1kΩ)
 10   GPIO15  UART RX           Input   ◄──  TMC2209 PDN_UART (via 1kΩ)

 16   GPIO23  RPM_SENSOR        Input   ◄──  Hall effect OUT (3.3V safe)

 29   GPIO5   ENCODER_A (CLK)   Input   ◄──  Rotary encoder CLK
 31   GPIO6   ENCODER_B (DT)    Input   ◄──  Rotary encoder DT
 33   GPIO13  ENCODER_SW        Input   ◄──  Rotary encoder push

 36   GPIO16  BTN_MODE          Input   ◄──  MODE button
 38   GPIO20  BTN_GO_STOP       Input   ◄──  GO/STOP button
 40   GPIO21  BTN_ESTOP         Input   ◄──  Emergency stop (NC)

 01   3.3V    Logic power       ──►     ──►  TMC2209 VIO, sensor VCC
 02   5V      —                 ──►     ──►  (reserved)
 06   GND     Common ground     ──►     ──►  All GND connections
 09   GND     Common ground     ──►     ──►  Button/encoder ground
```

---

## TMC2209 Stepper Driver

```
TMC2209 Module          Raspberry Pi              NEMA 17 Motor
┌─────────────┐                                   ┌────────────┐
│ VM ─────────── 24V PSU V+                       │            │
│ GND ────────── 24V PSU GND + Pi GND (common)    │  A+ (Red)  │
│              │                                   │  A- (Blue) │
│ 1A ──────────────────────────────────────────►───│            │
│ 1B ──────────────────────────────────────────►───│  B+ (Green)│
│ 2A ──────────────────────────────────────────►───│  B- (Black)│
│ 2B ──────────────────────────────────────────►───│            │
│              │                                   └────────────┘
│ STEP ───────── GPIO17 (pin 11)
│ DIR ────────── GPIO27 (pin 13)
│ EN ─────────── GPIO22 (pin 15)     (LOW = enabled)
│              │
│ PDN_UART ──┬── GPIO14 TX (pin 08) via 1kΩ
│            └── GPIO15 RX (pin 10) via 1kΩ
│              │
│ VIO ────────── Pi 3.3V (pin 01)
│ GND ────────── Pi GND  (pin 06)
└─────────────┘
```

### TMC2209 UART (Pi Hardware UART)

```
Pi GPIO14 (TX) ──── 1kΩ ────┐
                              ├──── TMC2209 PDN_UART
Pi GPIO15 (RX) ──── 1kΩ ────┘
```

> **Pi UART setup:** You must disable the Pi's serial console and enable the hardware UART. The install script handles this. See `install.sh`.

---

## RPM Sensor (Hall Effect)

### Option A: KY-003 Hall Effect Module

```
KY-003 Module          Pi
┌────────────┐
│ VCC ───────── 3.3V (pin 01)      ⚠ Confirm module is 3.3V safe!
│ GND ───────── GND  (pin 06)
│ OUT ───────── GPIO23 (pin 16) ── 10kΩ pull-up to 3.3V
└────────────┘
```

Mount a small neodymium magnet (3×1mm disc) on the motor pulley or lathe spindle:
- Magnet passes sensor once per revolution
- Sensor outputs LOW when magnet is near
- Software measures time between pulses → RPM

### Option B: Optical Slot Sensor

```
TCPT1300 / KY-010       Pi
┌────────────┐
│ VCC ───────── 3.3V
│ GND ───────── GND
│ OUT ───────── GPIO23 (pin 16) ── 10kΩ pull-up to 3.3V
└────────────┘
```

Use a 3D-printed slotted disc (1 slot) on the shaft. Adjust sensor gap to ~3mm.

---

## Rotary Encoder (Speed Knob)

```
KY-040 / PEC11R         Pi
┌────────────┐
│ CLK ───────── GPIO5  (pin 29) ── 10kΩ pull-up to 3.3V
│ DT ────────── GPIO6  (pin 31) ── 10kΩ pull-up to 3.3V
│ SW ────────── GPIO13 (pin 33) ── 10kΩ pull-up to 3.3V
│ + ─────────── 3.3V
│ GND ───────── GND   (pin 09)
└────────────┘
```

> For a nice lathe feel, use a heavy machined aluminum knob (25-38mm diameter) on the encoder shaft.

---

## Buttons

```
[MODE]     ── GPIO16 (pin 36) ── 10kΩ pull-up to 3.3V
                │
                └── GND (when pressed)

[GO/STOP]  ── GPIO20 (pin 38) ── 10kΩ pull-up to 3.3V
                │
                └── GND (when pressed)

[E-STOP]   ── GPIO21 (pin 40) ── 10kΩ pull-up to 3.3V
                │
                └── GND (mushroom button, NORMALLY CLOSED)
```

> **E-STOP is NORMALLY CLOSED (NC).** When the mushroom button is pressed, it OPENS the circuit (GPIO goes HIGH). This is fail-safe — a broken wire also triggers E-STOP.

---

## Complete Wiring Summary

| Pi Pin# | GPIO | Function | Pull | Wire Color (suggested) |
|---------|------|----------|------|------------------------|
| 11 | GPIO17 | STEP | — | Yellow |
| 13 | GPIO27 | DIR | — | Orange |
| 15 | GPIO22 | ENABLE | — | Brown |
| 08 | GPIO14 | UART TX | — | White |
| 10 | GPIO15 | UART RX | — | Gray |
| 16 | GPIO23 | RPM Sensor | 10kΩ ↑ | Green |
| 29 | GPIO5 | Encoder CLK | 10kΩ ↑ | Blue |
| 31 | GPIO6 | Encoder DT | 10kΩ ↑ | Purple |
| 33 | GPIO13 | Encoder SW | 10kΩ ↑ | Blue/White |
| 36 | GPIO16 | MODE btn | 10kΩ ↑ | Red |
| 38 | GPIO20 | GO/STOP btn | 10kΩ ↑ | Green |
| 40 | GPIO21 | E-STOP btn | 10kΩ ↑ | Red/White |
| 01 | 3.3V | Logic power | — | Red |
| 06 | GND | Ground bus | — | Black |
| 09 | GND | Ground bus | — | Black |

---

## Assembly Checklist

- [ ] Pi boots to desktop with touchscreen working
- [ ] Serial console disabled, hardware UART enabled
- [ ] Common ground between Pi GND and 24V PSU GND
- [ ] 100µF cap soldered at TMC2209 VM/GND
- [ ] 1kΩ resistors on UART TX and RX lines
- [ ] 10kΩ pull-ups on all input GPIOs
- [ ] RPM sensor magnet aligned and tested (spin by hand, verify pulse)
- [ ] E-STOP wired NC (continuity when button is UP, open when pressed)
- [ ] Motor coils verified (measure 1–3Ω between pairs)
- [ ] No exposed conductors near moving parts
- [ ] Belt tension correct (~3–5mm deflection at midpoint)
- [ ] Encoder knob firmly attached, no slipping
