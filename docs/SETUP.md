# Setup & Calibration Guide

## First-Time Setup for the 5C Indexing Controller

---

## Step 1: Verify Hardware

1. **Check buck converter output** — Measure with multimeter, confirm 5.0V ± 0.1V before connecting the ESP32.
2. **Verify motor wiring** — Confirm coil pairs with multimeter (1–3Ω between A+/A- and B+/B-).
3. **Confirm TMC2209 power** — VM should read 24V, VIO should read 3.3V.

## Step 2: Flash Firmware

1. Install [VS Code](https://code.visualstudio.com/) + [PlatformIO extension](https://platformio.org/install/ide?install=vscode).
2. Open the `firmware/` folder in VS Code.
3. Connect ESP32 via USB-C.
4. Click the PlatformIO **Upload** button (→ arrow) or run:
   ```
   pio run -t upload
   ```
5. Open Serial Monitor (baud 115200) to verify boot messages.

## Step 3: Configure Gear Ratio

Edit `firmware/src/config.h`:

```cpp
// Your pulley teeth counts
#define GEAR_RATIO_NUMERATOR    60   // Driven pulley (on indexer)
#define GEAR_RATIO_DENOMINATOR  20   // Drive pulley (on motor)
```

This gives a 3:1 ratio. The motor turns 3 times for 1 indexer revolution.

**Common Ratios:**

| Motor Pulley | Indexer Pulley | Ratio | Resolution (16µstep) |
|---|---|---|---|
| 20T | 40T | 2:1 | 0.056° per step |
| 20T | 60T | 3:1 | 0.0375° per step |
| 16T | 48T | 3:1 | 0.0375° per step |
| 20T | 80T | 4:1 | 0.028° per step |

Higher ratios = finer resolution + more torque, but slower movement.

## Step 4: Verify Motor Direction

1. Power on the system.
2. Set divisions to **4** (90° increments).
3. Press **GO** — the indexer should rotate **clockwise** when viewed from the front.
4. If it rotates the wrong way, either:
   - Swap **A+ / A-** motor wires, OR
   - Change `#define INVERT_DIRECTION true` in `config.h`

## Step 5: Verify Step Count

1. Mark the indexer with a reference line (use a marker or tape).
2. Set divisions to **1** (full 360° revolution).
3. Press **GO** — the indexer should complete exactly one full revolution.
4. If it overshoots or undershoots:
   - Recheck your gear ratio in `config.h`
   - Verify the motor is 200 steps/rev (1.8° motors)
   - Check microstepping setting (default: 16)

## Step 6: Set Motor Current

The default motor current is set to **1200mA** in firmware. Adjust in `config.h`:

```cpp
#define MOTOR_CURRENT_MA  1200  // RMS current in milliamps
```

- Start low (800mA) and increase if the motor skips steps under load.
- Never exceed your motor's rated current.
- The TMC2209 will auto-reduce current when idle (via firmware).

## Step 7: Belt Tension

- The belt should have slight tension — press with a finger at the midpoint, it should deflect ~3–5mm.
- Too tight = excess bearing load and motor strain.
- Too loose = tooth skipping under load.
- Re-check after first hour of use — new belts stretch slightly.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Motor doesn't move | EN pin not low / wiring error | Check GPIO 18, verify motor power |
| Motor vibrates but doesn't turn | Coil wires swapped | Swap one coil pair (A+↔A- or swap B pair) |
| Steps are inconsistent | Belt slipping | Tighten belt, check pulley set screws |
| Display blank | I2C address wrong | Try `0x3D` in config, check SDA/SCL |
| Encoder skips counts | Noise on lines | Add/verify 10kΩ pull-ups, use shielded wire |
| Motor overheating | Current too high | Reduce `MOTOR_CURRENT_MA`, check ventilation |
| Position drifts over time | Missed steps | Increase current, reduce speed, check belt |
| UART error on boot | 1kΩ resistor missing | Add resistor on PDN_UART line |
