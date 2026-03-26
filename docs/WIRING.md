# Wiring Guide

## HHIP 5C Indexing Spin Jig — Stepper Controller

---

## Power Distribution

```
┌──────────────┐
│  24V 5A PSU  │
│              │
│  V+ ────────────┬──────────────── TMC2209 VM
│              │   │
│              │   └──── LM2596 IN+ ──── LM2596 OUT+ ──── ESP32 VIN (5V)
│              │
│  V- ────────────┬──────────────── TMC2209 GND
│              │   │
│              │   └──── LM2596 IN- ──── LM2596 OUT- ──── ESP32 GND
│              │
│  (Earth) ───────── Enclosure Ground
└──────────────┘
```

> **IMPORTANT:** Place a 100µF 50V electrolytic capacitor across TMC2209 VM and GND, as close to the driver as possible.

---

## TMC2209 Stepper Driver Wiring

```
TMC2209 Module          ESP32                   Motor (NEMA 23)
┌─────────────┐                                ┌────────────┐
│ VM ─────────── 24V PSU V+                    │            │
│ GND ────────── 24V PSU GND                   │  A+ (Red)  │◄── 1A
│              │                                │  A- (Blue) │◄── 1B
│ 1A ──────────────────────────────────────────►│            │
│ 1B ──────────────────────────────────────────►│  B+ (Green)│◄── 2A
│ 2A ──────────────────────────────────────────►│  B- (Black)│◄── 2B
│ 2B ──────────────────────────────────────────►│            │
│              │                                └────────────┘
│ STEP ───────── GPIO 16
│ DIR ────────── GPIO 17
│ EN ─────────── GPIO 18          (LOW = enabled)
│              │
│ PDN/UART ───── GPIO 19          (via 1kΩ resistor)
│              │
│ VIO ────────── ESP32 3.3V       (logic level reference)
│ GND ────────── ESP32 GND        (common ground)
└─────────────┘
```

### TMC2209 UART Connection Detail

```
ESP32 GPIO 19 ───── 1kΩ ────┬──── TMC2209 PDN_UART
                             │
                        (single-wire UART, directly to pin)
```

> The TMC2209 uses a single-wire UART interface via the PDN_UART pin. The 1kΩ resistor is required for proper communication.

### TMC2209 Configuration Jumpers

On the BigTreeTech TMC2209 module:
- **MS1 = LOW, MS2 = LOW** → UART address 0b00 (default)
- Microstepping is set via UART in firmware (not jumpers)

---

## OLED Display (I2C)

```
SSD1306 OLED           ESP32
┌────────────┐
│ VCC ───────── 3.3V
│ GND ───────── GND
│ SDA ───────── GPIO 21
│ SCL ───────── GPIO 22
└────────────┘
```

> Default I2C address: `0x3C`. If your display uses `0x3D`, update `OLED_ADDRESS` in `config.h`.

---

## Rotary Encoder (KY-040)

```
KY-040 Encoder         ESP32
┌────────────┐
│ CLK ───────── GPIO 32 ──── 10kΩ pull-up to 3.3V
│ DT ────────── GPIO 33 ──── 10kΩ pull-up to 3.3V
│ SW ────────── GPIO 25 ──── 10kΩ pull-up to 3.3V
│ + ─────────── 3.3V
│ GND ───────── GND
└────────────┘
```

> Pull-up resistors are recommended even though ESP32 has internal pull-ups. External 10kΩ gives cleaner signals in a shop environment.

---

## Control Buttons

```
Button Layout              ESP32
┌──────────────┐
│ [MODE]    ───── GPIO 26 ──── 10kΩ pull-up to 3.3V
│ [PRESET]  ───── GPIO 27 ──── 10kΩ pull-up to 3.3V  
│ [GO/STOP] ───── GPIO 14 ──── 10kΩ pull-up to 3.3V
│                  │
│ Common ─────────── GND
└──────────────┘
```

All buttons are **normally open (NO)**, active **LOW** (pressed = GND).

---

## Complete Pin Summary

| ESP32 GPIO | Function | Direction | Notes |
|------------|----------|-----------|-------|
| 16 | STEP | Output | TMC2209 step pulse |
| 17 | DIR | Output | TMC2209 direction |
| 18 | EN | Output | TMC2209 enable (active LOW) |
| 19 | UART TX/RX | Bidirectional | TMC2209 PDN_UART via 1kΩ |
| 21 | I2C SDA | Bidirectional | OLED display |
| 22 | I2C SCL | Output | OLED display |
| 25 | Encoder SW | Input | Encoder push button |
| 26 | MODE Button | Input | Mode selection |
| 27 | PRESET Button | Input | Preset selection |
| 32 | Encoder CLK | Input | Rotation A |
| 33 | Encoder DT | Input | Rotation B |
| 14 | GO/STOP Button | Input | Execute / halt move |
| 3.3V | Power | — | OLED, encoder, TMC2209 VIO |
| VIN | Power In | — | 5V from buck converter |
| GND | Ground | — | Common ground bus |

---

## Grounding Notes

- **Use a star-ground topology** — run separate ground wires from the power supply to the driver, to the ESP32, and to the signal ground bus, meeting at a single point near the PSU.
- **Do NOT daisy-chain grounds** through the perfboard — motor current can induce noise on logic signals.
- Keep motor wires (18 AWG) physically separated from signal wires (22 AWG).

---

## Motor Cable (GX16-4 Aviation Connector)

| Pin | Color (typical) | Function |
|-----|-----------------|----------|
| 1 | Red | A+ (Coil 1+) |
| 2 | Blue | A- (Coil 1-) |
| 3 | Green | B+ (Coil 2+) |
| 4 | Black | B- (Coil 2-) |

> Verify your motor's wiring with a multimeter — measure resistance between pairs. Coil pairs will show ~1–3Ω.

---

## Assembly Checklist

- [ ] All solder joints clean and shiny
- [ ] 100µF cap installed at TMC2209 VM/GND
- [ ] 1kΩ resistor on UART line
- [ ] Pull-up resistors on all input pins
- [ ] Motor connector secure with strain relief
- [ ] Buck converter output verified at 5.0V before connecting ESP32
- [ ] No exposed conductors / all connections insulated
- [ ] Enclosure mounted securely to workbench or indexer base
