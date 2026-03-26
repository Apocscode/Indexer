# Assembly Guide

## Step-by-Step Build Instructions for Both Controller Systems

---

## Part 1: ESP32 Indexing Controller (HHIP 5C Spin Jig)

### Phase 1 — Prepare Components

**Time estimate: 15 minutes**

1. Unpack and verify all components against the [Materials List](MATERIALS.md) Section A.
2. Inspect the TMC2209 driver board — confirm no bent pins or solder bridges.
3. Verify the stepper motor coil pairs with a multimeter:
   - Set meter to resistance (Ω) mode.
   - Identify two wire pairs that read 1–3Ω between them (these are coil A and coil B).
   - The other combinations will read open (∞).
   - Label the pairs: **A+ / A-** and **B+ / B-**.
4. Confirm the OLED display I2C address (printed on the back — usually 0x3C).
5. Test the buck converter **before** connecting to the ESP32:
   - Connect 24V PSU to the buck converter input.
   - Measure output voltage with a multimeter.
   - Adjust the trimpot until output reads **5.0V ± 0.1V**.
   - **Do NOT connect ESP32 until output is verified.**

### Phase 2 — Prepare the Enclosure

**Time estimate: 30 minutes**

1. Mark panel hole positions:
   - OLED display window (rectangular cutout: 26mm × 14mm)
   - Rotary encoder shaft hole (7mm dia)
   - 3× button holes (12mm dia each)
   - Power jack hole (12mm dia)
   - Power toggle switch hole (match your switch)
   - Motor cable gland hole (PG9: 15.5mm dia)
   - Signal cable gland(s) if needed (PG7: 12.5mm dia)
2. Drill all holes. Start with a pilot drill (3mm), then step up.
3. Cut the OLED window with a rotary tool or nibbler.
4. Deburr all holes with a countersink or file.
5. Test-fit all panel components (buttons, encoder, switch, jack) before wiring.

### Phase 3 — Build the Electronics Board

**Time estimate: 45–60 minutes**

1. **Mount components on perfboard** (70×90mm):
   - TMC2209 driver — use header sockets so the driver is removable
   - Screw terminal blocks — for motor output, power input
   - 1kΩ resistor — between ESP32 GPIO 19 pad and TMC2209 PDN_UART pad
   - 4× 10kΩ pull-up resistors — from encoder/button input pads to 3.3V rail
   - 100µF capacitor — across TMC2209 VM and GND pads (observe polarity!)

2. **Solder the ESP32 DevKit** — use pin headers (not directly soldered) if you want it removable.

3. **Wire the power rails:**
   - 24V input terminals → TMC2209 VM + Buck converter input
   - Buck converter output (5V) → ESP32 VIN
   - Ground bus: PSU GND → TMC2209 GND → ESP32 GND → Buck converter GND

4. **Wire signal connections** (22 AWG):
   - GPIO 16 → TMC2209 STEP
   - GPIO 17 → TMC2209 DIR
   - GPIO 18 → TMC2209 EN
   - GPIO 19 → 1kΩ → TMC2209 PDN_UART
   - GPIO 21 → OLED SDA
   - GPIO 22 → OLED SCL
   - GPIO 32 → Encoder CLK (+ 10kΩ to 3.3V)
   - GPIO 33 → Encoder DT (+ 10kΩ to 3.3V)
   - GPIO 25 → Encoder SW (+ 10kΩ to 3.3V)
   - GPIO 26 → MODE button (+ 10kΩ to 3.3V)
   - GPIO 27 → PRESET button (+ 10kΩ to 3.3V)
   - GPIO 14 → GO/STOP button (+ 10kΩ to 3.3V)

5. **Insulate** all solder joints with heat shrink tubing.

### Phase 4 — Install Panel Components

**Time estimate: 20 minutes**

1. Mount the OLED display in the window cutout — secure with hot glue or small brackets.
2. Install the rotary encoder through its panel hole — tighten the nut.
3. Install the 3 push buttons — tighten panel nuts.
4. Install the DC power jack and power toggle switch.
5. Thread the motor cable through the cable gland (don't tighten yet).
6. Connect wires from panel components to the electronics board:
   - Button common pins → GND bus
   - Button NO pins → respective GPIO pads (with pull-ups)
   - Encoder CLK/DT/SW → respective GPIO pads
   - Encoder +/GND → 3.3V / GND

### Phase 5 — Motor & Drive System

**Time estimate: 30–45 minutes**

1. **Install the motor pulley:**
   - Slide the GT2 20T pulley onto the NEMA 23 motor shaft.
   - Align the pulley: the teeth should be in the same plane as the indexer pulley.
   - Tighten the set screw(s) firmly with an Allen wrench.
   - Pull-test: the pulley should not slip on the shaft.

2. **Install the indexer pulley:**
   - Slide the GT2 60T pulley onto the HHIP 5C spin jig's spindle.
   - If the bore doesn't match, use a shaft bushing/sleeve.
   - Tighten the set screw(s).
   - Ensure the pulley face is aligned with the motor pulley (within 1mm).

3. **Mount the motor bracket:**
   - Position the NEMA 23 motor so the shaft is parallel to the indexer spindle.
   - The center-to-center distance should allow the belt to slip on without excessive tension.
   - Mark and drill mounting holes in the bracket.
   - Bolt the motor to the bracket securely — use lock washers or thread locker.

4. **Install the timing belt:**
   - Loop the GT2 belt around both pulleys.
   - Adjust the motor bracket position for proper tension.
   - Target: 3–5mm deflection when pressing the belt at its midpoint with a finger.
   - Too tight = excess bearing load. Too loose = teeth will skip under load.
   - If using an idler tensioner, mount it on the slack side.

5. **Connect the motor cable:**
   - Wire the motor leads to the GX16-4 aviation connector:
     - Pin 1 → A+ (Red)
     - Pin 2 → A- (Blue)
     - Pin 3 → B+ (Green)
     - Pin 4 → B- (Black)
   - Verify your motor's color code (it may differ — use the multimeter coil test).
   - Solder and heat-shrink all connections.
   - Tighten the cable gland for strain relief.

### Phase 6 — Flash & Test

**Time estimate: 15 minutes**

1. **Install PlatformIO** — VS Code extension.
2. Open the `firmware/` folder in VS Code.
3. Connect the ESP32 via USB-C.
4. Edit `firmware/src/config.h`:
   - Set `GEAR_RATIO_NUMERATOR` and `GEAR_RATIO_DENOMINATOR` to match your pulleys.
   - Verify pin assignments match your wiring.
5. Build and upload: click the PlatformIO Upload button or run `pio run -t upload`.
6. Open Serial Monitor (115200 baud) — verify boot messages.
7. The OLED should display the splash screen, then the main UI.

### Phase 7 — Calibrate

**Time estimate: 10 minutes**

1. Set divisions to **4** → press GO → verify spindle moves exactly 90°.
2. If direction is wrong: swap A+ / A- motor wires, or set `INVERT_DIRECTION true`.
3. Set divisions to **1** → press GO → verify one full revolution returns to start.
4. Test jog mode: jog 10° increments, verify with a protractor or dial indicator.
5. Run 10 full revolutions with divisions set to 7 (worst case for rounding) — verify return to zero.

### Phase 8 — Final Assembly

**Time estimate: 10 minutes**

1. Secure the electronics board inside the enclosure with standoffs or screws.
2. Route all wires neatly — separate power (18 AWG) from signal (22 AWG).
3. Zip-tie cable bundles.
4. Tighten all cable glands.
5. Close the enclosure.
6. Apply labels if desired (MODE, PRESET, GO/STOP, POWER).
7. Re-check belt tension after installation is complete.

---

## Part 2: Watchmaker's Lathe Controller (Raspberry Pi)

### Phase 1 — Prepare Components

**Time estimate: 15 minutes**

1. Unpack and verify all components against the [Materials List](MATERIALS.md) Section B.
2. Test the stepper motor coil pairs with a multimeter (same procedure as ESP32 build).
3. Test the hall effect sensor:
   - Apply 3.3V and GND.
   - Pass a magnet near the sensor face.
   - Measure the output pin — should toggle between HIGH (no magnet) and LOW (magnet near).
4. Verify the 24V PSU outputs 24V with a multimeter (unloaded).

### Phase 2 — Raspberry Pi Setup

**Time estimate: 30 minutes**

1. Flash **Raspberry Pi OS (Bookworm, Desktop)** to the MicroSD card using Raspberry Pi Imager.
2. Insert the MicroSD card into the Pi.
3. Connect the 7" touchscreen to the Pi via the DSI ribbon cable:
   - Power off the Pi.
   - Lift the ribbon cable connector latch on both the Pi and the display.
   - Insert the ribbon cable (silver contacts facing the board on the Pi end).
   - Close both latches.
   - Connect the display power jumper wires (5V + GND from Pi to display board).
4. Mount the Pi in the touchscreen case.
5. Connect USB keyboard, mouse, and power. Boot the Pi.
6. Complete the first-boot wizard (WiFi, locale, password).
7. Open a terminal and run:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### Phase 3 — Software Installation

**Time estimate: 10 minutes**

1. Clone the repository:
   ```bash
   cd ~
   git clone https://github.com/Apocscode/Indexer.git
   ```
2. Run the installer:
   ```bash
   cd ~/Indexer/watchmaker
   chmod +x install.sh
   sudo ./install.sh
   ```
3. This installs: Python 3, tkinter, pigpio, creates a virtual environment, configures UART, and sets up the systemd service.
4. **Reboot** after installation (required for UART changes):
   ```bash
   sudo reboot
   ```

### Phase 4 — Build the Electronics

**Time estimate: 45–60 minutes**

1. **Prepare the GPIO breakout board / HAT proto board:**
   - Mount on the Pi's 40-pin GPIO header.
   - Plan component layout: TMC2209 driver, resistors, terminal blocks.

2. **Solder the TMC2209 driver section:**
   - Use header sockets (removable driver).
   - 100µF cap across VM and GND (observe polarity!).
   - 24V input terminals → TMC2209 VM / GND.
   - Common ground: 24V PSU GND → TMC2209 GND → Pi GND (pin 6).

3. **Wire TMC2209 signal connections:**
   - GPIO 17 (pin 11) → TMC2209 STEP
   - GPIO 27 (pin 13) → TMC2209 DIR
   - GPIO 22 (pin 15) → TMC2209 EN
   - GPIO 14 (pin 08) → 1kΩ → TMC2209 PDN_UART
   - GPIO 15 (pin 10) → 1kΩ → TMC2209 PDN_UART
   - Pi 3.3V (pin 01) → TMC2209 VIO
   - Pi GND (pin 06) → TMC2209 GND

4. **Wire RPM sensor:**
   - Hall effect VCC → Pi 3.3V (pin 01)
   - Hall effect GND → Pi GND (pin 06)
   - Hall effect OUT → GPIO 23 (pin 16) + 10kΩ pull-up to 3.3V

5. **Wire rotary encoder:**
   - Encoder CLK → GPIO 5 (pin 29) + 10kΩ pull-up to 3.3V
   - Encoder DT → GPIO 6 (pin 31) + 10kΩ pull-up to 3.3V
   - Encoder SW → GPIO 13 (pin 33) + 10kΩ pull-up to 3.3V
   - Encoder + → 3.3V
   - Encoder GND → Pi GND (pin 09)

6. **Wire buttons:**
   - MODE button → GPIO 16 (pin 36) + 10kΩ pull-up to 3.3V
   - GO/STOP button → GPIO 20 (pin 38) + 10kΩ pull-up to 3.3V
   - E-STOP button (NC) → GPIO 21 (pin 40) + 10kΩ pull-up to 3.3V
   - All button commons → GND (pin 06 or pin 09)

> **E-STOP wiring:** The mushroom button must be **normally closed (NC)**. The NC terminal connects between GPIO 21 and GND. When pressed, it opens the circuit (GPIO goes HIGH). A broken wire also triggers E-STOP — this is fail-safe by design.

### Phase 5 — Prepare the Enclosure

**Time estimate: 30 minutes**

1. Mark panel hole positions:
   - Rotary encoder shaft (7mm dia)
   - MODE button (16mm dia)
   - GO/STOP button (16mm dia)
   - E-STOP mushroom button (22mm dia)
   - Power switch (match your switch)
   - Motor cable gland (PG7: 12.5mm dia)
   - Sensor cable gland (PG7: 12.5mm dia)
   - Power cable gland (PG7: 12.5mm dia)
2. Drill all holes. Start with pilot drill, step up.
3. Deburr all holes.
4. Mount panel components — test fit before final tightening.
5. Install the heavy machined knob on the encoder shaft.

### Phase 6 — Motor & Drive System

**Time estimate: 30–45 minutes**

1. **Install the motor pulley:**
   - Slide GT2 20T pulley onto NEMA 17 shaft (5mm).
   - Align with the spindle pulley plane.
   - Tighten set screw(s).

2. **Install the spindle pulley** (varies by lathe — see table below):

   | Lathe | Procedure |
   |-------|-----------|
   | **Levin** | Remove the existing round-belt headstock pulley. Install GT2 60T pulley with matching bore. Tighten set screw. |
   | **Boley F1** | Slide adapter sleeve (3D printed or machined) over the existing round-belt pulley. The adapter has GT2 teeth on the outside. |
   | **Sherline** | Mount GT2 pulley to the spindle nose or use an ER16 collet adapter. |
   | **Taig** | Remove stock V-belt pulley. Install GT2 pulley on 1/2" shaft. |
   | **Cowells** | Remove stock belt pulley. Install GT2 pulley with matching bore. |

3. **Mount the motor:**
   - Fabricate or 3D-print a bracket to hold the NEMA 17 near the lathe headstock.
   - Motor shaft must be parallel to lathe spindle.
   - Secure with bolts — use slots (not round holes) in the bracket for belt tension adjustment.

4. **Install the timing belt:**
   - Loop GT2 belt around both pulleys.
   - Adjust motor position for correct tension (3–5mm deflection at midpoint).
   - Install the idler tensioner on the slack side if used.

5. **Install the RPM magnet:**
   - Epoxy a 3×1mm neodymium magnet to the motor pulley or lathe spindle.
   - Position so the magnet passes within 3mm of the hall effect sensor face.
   - The magnet must be flush — no protruding edges to catch the belt.

6. **Mount the hall effect sensor:**
   - Position 2–3mm from the magnet path.
   - Secure with hot glue, bracket, or 3D-printed mount.
   - Run the sensor cable back to the enclosure through a cable gland.

7. **Connect the motor:**
   - Wire motor leads to GX12-4 aviation connector:
     - Pin 1 → A+ (Red)
     - Pin 2 → A- (Blue)
     - Pin 3 → B+ (Green)
     - Pin 4 → B- (Black)
   - Verify wire pairs before connecting.

### Phase 7 — Final Wiring & Assembly

**Time estimate: 20 minutes**

1. Mount the Pi + touchscreen assembly on or near the lathe (viewing angle matters).
2. Mount the electronics enclosure near the motor.
3. Run cables:
   - Pi GPIO ribbon/cable → electronics enclosure
   - Motor cable → aviation connector
   - Sensor cable → enclosure
   - 24V PSU → enclosure
   - Pi USB-C PSU → Pi
4. Secure all cables with zip ties, away from moving parts and chips.
5. Close the enclosure and tighten all cable glands.

### Phase 8 — Configure & Test

**Time estimate: 20 minutes**

1. Edit the configuration file:
   ```bash
   nano ~/Indexer/watchmaker/config.ini
   ```
2. Verify/set these values:
   - `steps_per_rev` — 400 (for 0.9° motor) or 200 (for 1.8° motor)
   - `microsteps` — 256 (default) or your chosen setting
   - `motor_teeth` — count your motor pulley teeth
   - `spindle_teeth` — count your spindle pulley teeth
   - `current_ma` — match your motor's rated current

3. **Start in demo mode first** (no motor movement):
   ```bash
   cd ~/Indexer/watchmaker
   ./run.sh --demo --windowed
   ```
   - Verify the GUI loads correctly.
   - Navigate all 4 pages (Lathe, Index, Presets, Settings).

4. **Start with hardware:**
   ```bash
   ./run.sh
   ```
5. Go to **Lathe page** → set 100 RPM → press START:
   - Motor should spin smoothly.
   - RPM gauge should show actual RPM (from hall sensor).
   - If direction is wrong: swap one motor coil pair, or set `invert_direction = true`.

6. Test RPM sensor:
   - Spin the motor at 500 RPM.
   - The RPM gauge should track accurately.
   - If RPM reads double: set `pulses_per_rev = 2` in config.ini.

7. Test PID mode:
   - Toggle from OPEN to PID on the lathe page.
   - Set 500 RPM — motor should regulate to that speed under varying load.
   - If oscillating: reduce Kp. If sluggish: increase Kp.

8. Test indexing:
   - Go to **Index page** → set 6 divisions → press NEXT.
   - Spindle should rotate exactly 60°.
   - Press NEXT 5 more times — should return to exactly 0°.

9. Run a full test:
   - Set 7 divisions (worst case for Bresenham).
   - Press NEXT 7 times — must return to exactly 0°.
   - Repeat for 10 full revolutions — no drift allowed.

### Phase 9 — Enable Auto-Start (Optional)

```bash
sudo systemctl enable watchmaker-lathe
sudo systemctl start watchmaker-lathe
```

The controller will now start automatically when the Pi boots.

---

## Assembly Checklist — ESP32

- [ ] Buck converter output verified at 5.0V ± 0.1V
- [ ] Motor coil pairs identified and labeled
- [ ] TMC2209 mounted in removable sockets
- [ ] 100µF cap installed at TMC2209 VM/GND (correct polarity)
- [ ] 1kΩ resistor on UART line (GPIO 19 → PDN_UART)
- [ ] 10kΩ pull-ups on all input GPIOs (encoder + buttons)
- [ ] All solder joints clean and shiny
- [ ] Power switch installed and functional
- [ ] Motor pulley and indexer pulley aligned (same plane, ±1mm)
- [ ] Belt tension correct (3–5mm deflection at midpoint)
- [ ] Pulley set screws tight (pull-tested)
- [ ] Motor connector wired correctly (coil pairs verified)
- [ ] No exposed conductors — all joints insulated
- [ ] Enclosure closed, cable glands tight
- [ ] Firmware flashed and serial output verified
- [ ] All 4 test modes validated (index, jog, preset, continuous)
- [ ] 360° full-revolution accuracy confirmed

## Assembly Checklist — Watchmaker

- [ ] Pi boots to desktop with touchscreen working
- [ ] UART enabled, serial console disabled (install.sh handles this)
- [ ] pigpiod daemon running (`sudo systemctl status pigpiod`)
- [ ] 24V PSU output verified at 24V
- [ ] Common ground between Pi GND and 24V PSU GND
- [ ] TMC2209 mounted in removable sockets
- [ ] 100µF cap at TMC2209 VM/GND (correct polarity)
- [ ] 1kΩ resistors on UART TX and RX lines
- [ ] 10kΩ pull-ups on all input GPIOs (sensor + encoder + buttons)
- [ ] E-STOP wired NC (continuity when button is UP, open when pressed)
- [ ] RPM sensor magnet securely epoxied, flush with surface
- [ ] RPM sensor positioned 2–3mm from magnet path
- [ ] Motor coils verified (pairs identified with multimeter)
- [ ] Motor and spindle pulleys aligned (same plane, ±1mm)
- [ ] Belt tension correct (3–5mm deflection at midpoint)
- [ ] Pulley set screws tight (pull-tested)
- [ ] GUI launches correctly in demo mode
- [ ] Motor direction verified at low RPM
- [ ] RPM sensor reads accurately (within ±5%)
- [ ] PID tracks setpoint under load
- [ ] Index mode: 7 divisions × 10 revolutions returns to exactly 0°
- [ ] All cable glands tight, no exposed wires near moving parts

---

## Estimated Build Times

| Phase | ESP32 | Watchmaker |
|-------|-------|------------|
| Component prep | 15 min | 15 min |
| Pi/Display setup | — | 30 min |
| Software install | 5 min | 10 min |
| Enclosure prep | 30 min | 30 min |
| Electronics build | 45–60 min | 45–60 min |
| Panel components | 20 min | 20 min |
| Motor & belt | 30–45 min | 30–45 min |
| Final wiring | 10 min | 20 min |
| Config & testing | 25 min | 20 min |
| **Total** | **~3–4 hours** | **~4–5 hours** |

> Times assume basic soldering experience. First-time builders should allow 50% extra time.

---

*Assembly guide — March 2026*
