# Wiring Guide — Complete Reference

## Both Systems: ESP32 5C Indexer + Watchmaker's Lathe Controller

---

## Part 1: ESP32 Indexing Controller

### 1.1 Power Distribution

```
                    ┌──────────────────────────┐
                    │       24V 5A PSU         │
                    │    (Mean Well LRS-150)    │
                    │                          │
                    │  AC IN ◄── Mains via     │
                    │            toggle switch  │
                    │                          │
                    │  V+ ─────┬───────────────┼──► TMC2209 VM
                    │          │               │
                    │          └──► LM2596 IN+ │
                    │               │          │
                    │          LM2596 OUT+ ────┼──► ESP32 VIN (5V)
                    │                          │
                    │  V- ─────┬───────────────┼──► TMC2209 GND
                    │          │               │
                    │          └──► LM2596 IN- │
                    │               │          │
                    │          LM2596 OUT- ────┼──► ESP32 GND
                    │                          │
                    │  Earth ──────────────────┼──► Enclosure Ground
                    └──────────────────────────┘
```

> **CRITICAL:** Verify LM2596 output is 5.0V ± 0.1V with a multimeter **before** connecting the ESP32. Adjust the trimpot if needed.

> Place a 100µF 50V electrolytic capacitor across TMC2209 VM and GND, as close to the driver as possible. Observe polarity (long leg = +).

### 1.2 TMC2209 Stepper Driver

```
    TMC2209 Module              ESP32                 NEMA 23 Motor
    ┌──────────────┐                                  ┌──────────────┐
    │              │                                  │              │
    │ VM ──────────── 24V PSU V+ ──── [100µF cap]    │              │
    │ GND ─────────── 24V PSU V- ──── [cap GND]     │              │
    │              │                                  │              │
    │ 1A ─────────────────────────────────────────────│── A+ (Red)   │
    │ 1B ─────────────────────────────────────────────│── A- (Blue)  │
    │ 2A ─────────────────────────────────────────────│── B+ (Green) │
    │ 2B ─────────────────────────────────────────────│── B- (Black) │
    │              │                                  │              │
    │ STEP ────────── GPIO 16                        └──────────────┘
    │ DIR ─────────── GPIO 17
    │ EN ──────────── GPIO 18        (active LOW)
    │              │
    │ PDN_UART ──┬── GPIO 19        (via 1kΩ resistor)
    │            │
    │ VIO ─────────── 3.3V          (logic level ref)
    │ GND ─────────── ESP32 GND     (common ground)
    └──────────────┘
```

**UART detail:**
```
    ESP32 GPIO 19 ────── [1kΩ] ────── TMC2209 PDN_UART
```
Single-wire UART — the 1kΩ resistor is mandatory for proper bidirectional communication on one pin.

**TMC2209 Jumpers (BigTreeTech v1.3):**
- MS1 = LOW, MS2 = LOW → UART address 0b00 (default)
- Microstepping is configured via UART in firmware (not by jumpers)

### 1.3 OLED Display (I2C)

```
    SSD1306 OLED             ESP32
    ┌──────────────┐
    │ VCC ─────────── 3.3V
    │ GND ─────────── GND
    │ SDA ─────────── GPIO 21
    │ SCL ─────────── GPIO 22
    └──────────────┘
```

Default I2C address: `0x3C`. If blank, try `0x3D` in `config.h`.

### 1.4 Rotary Encoder (KY-040)

```
    KY-040                   ESP32                     Pull-ups
    ┌──────────────┐
    │ CLK ─────────── GPIO 32 ──────── [10kΩ] ──── 3.3V
    │ DT ──────────── GPIO 33 ──────── [10kΩ] ──── 3.3V
    │ SW ──────────── GPIO 25 ──────── [10kΩ] ──── 3.3V
    │ + ───────────── 3.3V
    │ GND ─────────── GND
    └──────────────┘
```

> External 10kΩ pull-ups are recommended over internal pull-ups for cleaner signals in a shop environment with electrical noise from the motor.

### 1.5 Control Buttons

```
                          Pull-ups             ESP32
    ┌──────────┐
    │ MODE     │──── [10kΩ] ──── 3.3V ─────── GPIO 26
    │ PRESET   │──── [10kΩ] ──── 3.3V ─────── GPIO 27
    │ GO/STOP  │──── [10kΩ] ──── 3.3V ─────── GPIO 14
    │          │
    │ Common   │──── GND
    └──────────┘
```

All buttons: **normally open (NO)**, active LOW (pressed = GND).

### 1.6 Motor Cable (GX16-4 Aviation Connector)

| Pin | Wire Color (typical) | Function |
|-----|---------------------|----------|
| 1 | Red | A+ (Coil 1+) |
| 2 | Blue | A- (Coil 1-) |
| 3 | Green | B+ (Coil 2+) |
| 4 | Black | B- (Coil 2-) |

> Verify coil pairs with a multimeter: pairs should read 1–3Ω. Other combinations read open circuit.

### 1.7 ESP32 Complete Pin Table

| GPIO | Pin | Function | Direction | Pull | Wire Color |
|------|-----|----------|-----------|------|------------|
| 16 | — | TMC2209 STEP | Output | — | Yellow |
| 17 | — | TMC2209 DIR | Output | — | Orange |
| 18 | — | TMC2209 EN | Output | — | Brown |
| 19 | — | TMC2209 UART | Bidir | — | White (via 1kΩ) |
| 21 | — | OLED SDA | Bidir | — | Blue |
| 22 | — | OLED SCL | Output | — | Purple |
| 25 | — | Encoder SW | Input | 10kΩ ↑ | Green |
| 26 | — | MODE Button | Input | 10kΩ ↑ | Red |
| 27 | — | PRESET Button | Input | 10kΩ ↑ | Orange |
| 32 | — | Encoder CLK | Input | 10kΩ ↑ | Blue |
| 33 | — | Encoder DT | Input | 10kΩ ↑ | Purple |
| 14 | — | GO/STOP Button | Input | 10kΩ ↑ | Green |
| 3.3V | — | Logic power | — | — | Red |
| VIN | — | 5V from buck | Power In | — | Red |
| GND | — | Common ground | — | — | Black |

---

## Part 2: Watchmaker's Lathe Controller (Raspberry Pi)

### 2.1 Power Distribution

```
    ┌─────────────────────┐                    ┌──────────────────┐
    │  USB-C 5V 3A PSU    │───────────────────►│  Raspberry Pi 4B │
    │  (Official Pi PSU)  │                    │  (powers Pi +    │
    └─────────────────────┘                    │   touchscreen)   │
                                               └──────────────────┘

    ┌─────────────────────┐
    │  24V 3A PSU         │
    │  (Mean Well LRS-75) │
    │                     │
    │  V+ ───────────┬────┼──► TMC2209 VM
    │                │    │    + [100µF 50V cap across VM/GND]
    │                │    │
    │  V- ───────────┬────┼──► TMC2209 GND
    │                │    │
    │                └────┼──► Pi GND (pin 6) ← COMMON GROUND
    │                     │
    │  Earth ─────────────┼──► Enclosure ground
    └─────────────────────┘
```

> **CRITICAL:** The Pi GND and motor PSU GND **must** share a common ground. Connect them at a single star-ground point. Without this, the TMC2209 cannot communicate with the Pi.

### 2.2 TMC2209 Stepper Driver

```
    TMC2209 Module              Raspberry Pi          NEMA 17 Motor
    ┌──────────────┐                                  ┌──────────────┐
    │              │                                  │              │
    │ VM ──────────── 24V PSU V+ ──── [100µF cap]    │              │
    │ GND ─────────── 24V PSU V- ──── [cap GND]     │              │
    │              │                                  │              │
    │ 1A ─────────────────────────────────────────────│── A+ (Red)   │
    │ 1B ─────────────────────────────────────────────│── A- (Blue)  │
    │ 2A ─────────────────────────────────────────────│── B+ (Green) │
    │ 2B ─────────────────────────────────────────────│── B- (Black) │
    │              │                                  │              │
    │ STEP ────────── GPIO 17  (pin 11)              └──────────────┘
    │ DIR ─────────── GPIO 27  (pin 13)
    │ EN ──────────── GPIO 22  (pin 15)    (active LOW)
    │              │
    │ PDN_UART ──┬── GPIO 14  (pin 08) TX   (via 1kΩ)
    │            └── GPIO 15  (pin 10) RX   (via 1kΩ)
    │              │
    │ VIO ─────────── 3.3V    (pin 01)
    │ GND ─────────── GND     (pin 06)
    └──────────────┘
```

**UART detail (Pi uses hardware UART — two wires):**
```
    Pi GPIO 14 (TX, pin 08) ────── [1kΩ] ───┐
                                              ├──── TMC2209 PDN_UART
    Pi GPIO 15 (RX, pin 10) ────── [1kΩ] ───┘
```

> The Pi uses hardware UART (/dev/ttyAMA0) with separate TX and RX lines, unlike the ESP32's single-wire UART. Both connect to the TMC2209's PDN_UART pin through individual 1kΩ resistors.

**Pi UART prerequisite:**
- Serial console must be disabled
- Hardware UART must be enabled
- Add to `/boot/config.txt` (or `/boot/firmware/config.txt` on Bookworm):
  ```
  enable_uart=1
  dtoverlay=disable-bt
  ```
- Remove `console=serial0,115200` from `/boot/cmdline.txt`
- Reboot.

### 2.3 RPM Sensor (Hall Effect)

```
    KY-003 Hall Effect          Pi                   Pull-up
    ┌──────────────┐
    │ VCC ─────────── 3.3V (pin 01)     ⚠ Verify module is 3.3V safe!
    │ GND ─────────── GND  (pin 06)
    │ OUT ─────────── GPIO 23 (pin 16) ──── [10kΩ] ──── 3.3V
    └──────────────┘
```

**Magnet placement:**
```
    ┌─────────────────────────────────────────────┐
    │            Spindle / Motor Pulley            │
    │                                             │
    │         ┌─── Neodymium magnet (3×1mm)       │
    │         │    epoxied flush to surface        │
    │    ┌────●────┐                              │
    │    │  Pulley │  ◄── Rotation                │
    │    └─────────┘                              │
    │         │                                   │
    │    2-3mm gap                                │
    │         │                                   │
    │    ┌────┴────┐                              │
    │    │ KY-003  │  ◄── Hall effect sensor      │
    │    │ sensor  │      (stationary mount)       │
    │    └─────────┘                              │
    └─────────────────────────────────────────────┘
```

- Magnet passes sensor once per revolution → low pulse
- Software measures time between pulses → RPM
- If using 2 magnets, set `pulses_per_rev = 2` in config.ini

### 2.4 Rotary Encoder (Speed Knob)

```
    KY-040 / PEC11R             Pi                   Pull-ups
    ┌──────────────┐
    │ CLK ─────────── GPIO 5  (pin 29) ──── [10kΩ] ──── 3.3V
    │ DT ──────────── GPIO 6  (pin 31) ──── [10kΩ] ──── 3.3V
    │ SW ──────────── GPIO 13 (pin 33) ──── [10kΩ] ──── 3.3V
    │ + ───────────── 3.3V
    │ GND ─────────── GND    (pin 09)
    └──────────────┘
```

> Attach a heavy machined aluminum knob (25–38mm) to the encoder shaft for a quality lathe-like feel.

### 2.5 Buttons

```
    ┌──────────────────────────────────────────────────────────────┐
    │                                                              │
    │  [MODE]      GPIO 16 (pin 36) ──── [10kΩ] ──── 3.3V        │
    │     │                                                        │
    │     └─── GND (when pressed)                                  │
    │                                                              │
    │  [GO/STOP]   GPIO 20 (pin 38) ──── [10kΩ] ──── 3.3V        │
    │     │                                                        │
    │     └─── GND (when pressed)                                  │
    │                                                              │
    │  [E-STOP]    GPIO 21 (pin 40) ──── [10kΩ] ──── 3.3V        │
    │     │                                                        │
    │     └─── GND (NORMALLY CLOSED — opens when pressed)          │
    │                                                              │
    │  All button common terminals ──── GND (pin 06/09)            │
    └──────────────────────────────────────────────────────────────┘
```

**E-STOP Safety Design:**
- The mushroom button has **NC (normally closed)** contacts
- Normal state: GPIO 21 is pulled LOW through the closed switch
- Pressed/fault: GPIO 21 goes HIGH (pulled up by 10kΩ)
- A broken wire also reads HIGH → triggers E-STOP
- This is **fail-safe** — any wiring failure stops the motor

### 2.6 Motor Cable (GX12-4 Aviation Connector)

| Pin | Wire Color (typical) | Function |
|-----|---------------------|----------|
| 1 | Red | A+ (Coil 1+) |
| 2 | Blue | A- (Coil 1-) |
| 3 | Green | B+ (Coil 2+) |
| 4 | Black | B- (Coil 2-) |

### 2.7 Pi GPIO Complete Pin Table

| Pi Pin# | GPIO | Function | Direction | Pull | Wire Color |
|---------|------|----------|-----------|------|------------|
| 11 | GPIO 17 | TMC2209 STEP | Output | — | Yellow |
| 13 | GPIO 27 | TMC2209 DIR | Output | — | Orange |
| 15 | GPIO 22 | TMC2209 EN | Output | — | Brown |
| 08 | GPIO 14 | UART TX → TMC | Output | — | White (via 1kΩ) |
| 10 | GPIO 15 | UART RX ← TMC | Input | — | Gray (via 1kΩ) |
| 16 | GPIO 23 | RPM Sensor | Input | 10kΩ ↑ | Green |
| 29 | GPIO 5 | Encoder CLK | Input | 10kΩ ↑ | Blue |
| 31 | GPIO 6 | Encoder DT | Input | 10kΩ ↑ | Purple |
| 33 | GPIO 13 | Encoder SW | Input | 10kΩ ↑ | Blue/White |
| 36 | GPIO 16 | MODE Button | Input | 10kΩ ↑ | Red |
| 38 | GPIO 20 | GO/STOP Button | Input | 10kΩ ↑ | Green |
| 40 | GPIO 21 | E-STOP (NC) | Input | 10kΩ ↑ | Red/White |
| 01 | 3.3V | Logic power | Power | — | Red |
| 02 | 5V | (reserved) | Power | — | — |
| 06 | GND | Ground bus 1 | Ground | — | Black |
| 09 | GND | Ground bus 2 | Ground | — | Black |

### 2.8 Touchscreen (DSI)

```
    Pi DSI Port                7" Touchscreen Display
    ┌──────────────┐          ┌──────────────────────┐
    │ DSI Ribbon ──────────────── DSI Ribbon          │
    │              │          │                      │
    │ 5V (pin 02) ──────────────── Display 5V        │
    │ GND (pin 06) ─────────────── Display GND       │
    └──────────────┘          └──────────────────────┘
```

The DSI ribbon cable handles both video and touch input. The 5V/GND jumpers power the display backlight.

---

## Part 3: Grounding Best Practices

### Star Ground Topology

```
                        ┌─── TMC2209 GND
                        │
    PSU GND ────────────┼─── MCU GND (ESP32 or Pi)
    (single point)      │
                        ├─── Sensor GND
                        │
                        └─── Button/Encoder GND
```

**Rules:**
1. Run **separate ground wires** from the PSU to each subsystem.
2. All grounds meet at **one single point** near the power supply.
3. Do **NOT** daisy-chain grounds through the perfboard.
4. Keep motor wires (18 AWG) physically separated from signal wires (22 AWG).
5. Motor current must not flow through signal ground paths.

### Why This Matters

Motor current draw creates voltage spikes (back-EMF) that can couple into signal lines, causing:
- False encoder readings
- Missed step pulses
- Corrupted UART communication
- Phantom button presses

Proper star grounding prevents these issues.

---

## Part 4: Wire Gauge Reference

| Wire | Gauge | Max Current | Used For |
|------|-------|-------------|----------|
| Motor coils | 18 AWG | 7A | A+/A-/B+/B- to TMC2209 |
| Power supply leads | 18 AWG | 7A | 24V PSU → TMC2209, PSU → buck |
| GPIO signals | 22 AWG | 0.9A | All logic connections |
| I2C bus | 22 AWG | — | OLED SDA/SCL |
| UART | 22 AWG | — | TMC2209 PDN_UART |
| Sensor | 22 AWG | — | Hall effect / encoder |

> Use **silicone-insulated** wire for signal runs — it's more flexible and heat-resistant than PVC.

---

## Part 5: Connector Reference

| Connector | Type | Pin Count | Used For |
|-----------|------|-----------|----------|
| GX16-4 (ESP32) | Aviation, panel-mount | 4 | NEMA 23 motor disconnect |
| GX12-4 (Watchmaker) | Aviation, panel-mount | 4 | NEMA 17 motor disconnect |
| JST-XH | Crimp, locking | 3–4 | Sensor, encoder connections |
| 5.08mm Screw Terminal | PCB-mount | 2 | Power input/output on board |
| DC Barrel Jack | 5.5×2.1mm, panel-mount | 2 | External 24V PSU input (ESP32) |
| PG7 Cable Gland | Threaded, panel-mount | — | 3–6mm cable entry |
| PG9 Cable Gland | Threaded, panel-mount | — | 5–8mm cable entry |

---

## Part 6: Testing Procedure After Wiring

### Before Applying Power

1. **Continuity test:** Verify no shorts between V+ and GND on any connector.
2. **Resistance test:** Verify motor coil pairs (1–3Ω between A+/A- and B+/B-).
3. **Visual inspection:** No solder bridges, no exposed conductors, correct cap polarity.

### First Power-On (ESP32)

1. Connect 24V PSU only (no ESP32 connected).
2. Measure TMC2209 VM: should read 24V.
3. Measure TMC2209 VIO: should read 0V (not yet connected to 3.3V source).
4. Measure buck converter output: should read 5.0V.
5. Disconnect 24V.
6. Connect ESP32 to USB-C (powered from computer, not buck converter).
7. Verify ESP32 boots (serial monitor).
8. Power off, connect buck converter output to ESP32 VIN.
9. Apply 24V — ESP32 should boot from buck converter.
10. Verify TMC2209 VIO now reads 3.3V (from ESP32).

### First Power-On (Watchmaker)

1. Connect 24V PSU only (Pi disconnected).
2. Measure TMC2209 VM: should read 24V.
3. Boot the Pi separately (USB-C power only, no 24V).
4. Verify Pi boots to desktop.
5. Connect the common ground wire between Pi GND and 24V PSU GND.
6. Apply 24V — TMC2209 VIO should now read 3.3V (from Pi via pin 01).
7. Run the software in demo mode to verify GPIO connections.

---

*Complete wiring reference — March 2026*
