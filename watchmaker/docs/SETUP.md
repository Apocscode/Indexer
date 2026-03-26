# Setup Guide — Watchmaker's Lathe Controller

## Prerequisites

| Item | Notes |
|------|-------|
| Raspberry Pi 4B (2 GB+) | Pi 3B+ works but Pi 4 recommended |
| Raspberry Pi OS (Bookworm or Bullseye) | Desktop version — needed for GUI |
| 7" Official Pi Touchscreen (or HDMI monitor) | 800×480 recommended |
| Internet connection | For initial setup only |

---

## 1. Hardware Assembly

Refer to [WIRING.md](WIRING.md) for the full GPIO pin table and wiring diagram.

### Quick Checklist

- [ ] TMC2209 driver board connected (STEP → GPIO 17, DIR → GPIO 27, EN → GPIO 22)
- [ ] TMC2209 UART wired (TX → GPIO 14, RX → GPIO 15, 1kΩ resistor on PDN_UART)
- [ ] Stepper motor connected to TMC2209 (A1/A2, B1/B2)
- [ ] GT2 belt + pulleys installed (motor → spindle)
- [ ] 24V PSU powering TMC2209 VMOT (NOT through the Pi!)
- [ ] Hall effect sensor wired (signal → GPIO 23, VCC → 3.3V, GND)
- [ ] Magnet(s) glued to spindle (aligned to pass sensor)
- [ ] Rotary encoder wired (CLK → GPIO 5, DT → GPIO 6, SW → GPIO 13)
- [ ] Buttons wired (Mode → GPIO 16, Go/Stop → GPIO 20, E-Stop → GPIO 21)
- [ ] E-Stop wired **Normally Closed** (NC → GPIO 21 + GND, opens on press)
- [ ] All grounds tied together (Pi GND, TMC2209 GND, sensor GND)

### Power-On Sequence

1. Connect all wiring **before** applying power
2. Power the 24V supply first (motor driver)
3. Power the Pi (5V USB-C or GPIO header)
4. Never hot-swap the motor while powered

---

## 2. Software Installation

### One-Line Install

```bash
cd ~/Indexer/watchmaker
chmod +x install.sh
sudo ./install.sh
```

This script:
- Installs Python 3, tkinter, pigpio
- Enables UART on the Pi (for TMC2209 communication)
- Starts `pigpiod` daemon
- Creates a Python virtual environment
- Installs pip dependencies
- Creates a systemd service (optional auto-start)

### Manual Install

```bash
# System packages
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk pigpio

# Enable pigpio daemon
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Python environment
cd ~/Indexer/watchmaker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Enable UART (required for TMC2209)

Add to `/boot/config.txt` (or `/boot/firmware/config.txt` on Bookworm):

```
enable_uart=1
dtoverlay=disable-bt
```

Disable serial console in `/boot/cmdline.txt` — remove `console=serial0,115200`.

**Reboot after UART changes:** `sudo reboot`

---

## 3. Configuration

Edit `config.ini` in the watchmaker directory:

```bash
nano ~/Indexer/watchmaker/config.ini
```

### Critical Settings to Verify

| Setting | Default | Check |
|---------|---------|-------|
| `steps_per_rev` | 200 | Match your motor (200 for 1.8°, 400 for 0.9°) |
| `microsteps` | 16 | Match TMC2209 config |
| `motor_teeth` | 20 | Count your motor pulley teeth |
| `spindle_teeth` | 60 | Count your spindle pulley teeth |
| `current_ma` | 800 | Match your motor's rated current |
| `magnets` | 1 | Number of magnets on spindle |

### Gear Ratio Examples

| Motor Pulley | Spindle Pulley | Ratio | Total Steps (200×16) |
|-------------|----------------|-------|---------------------|
| 20T | 20T | 1:1 | 3,200 |
| 20T | 40T | 2:1 | 6,400 |
| 20T | 60T | 3:1 | 9,600 |
| 16T | 48T | 3:1 | 9,600 |
| 16T | 80T | 5:1 | 16,000 |

Higher ratios = better angular resolution but lower max RPM.

---

## 4. Running

### Normal Launch (touchscreen, fullscreen)

```bash
cd ~/Indexer/watchmaker
./run.sh
```

### Demo Mode (no hardware — test on any computer)

```bash
./run.sh --demo --windowed
```

### Options

```
--demo        Run without hardware (simulated motor/sensor)
--windowed    Windowed mode instead of fullscreen
--theme       dark (default) or light
--config      Path to alternate config.ini
--log-level   DEBUG, INFO (default), WARNING, ERROR
--width       Window width in pixels (default: 800)
--height      Window height in pixels (default: 480)
```

### Auto-Start on Boot

```bash
sudo systemctl enable watchmaker-lathe
sudo systemctl start watchmaker-lathe
```

Check status: `sudo systemctl status watchmaker-lathe`

View logs: `journalctl -u watchmaker-lathe -f`

---

## 5. First Run Calibration

1. **Start in demo mode** first to verify the GUI works
2. Power up with hardware connected
3. Go to **Settings → Motor** — verify steps/rev, microsteps, current
4. Go to **Settings → Gear Ratio** — enter your actual pulley tooth counts
5. Go to **Lathe** page → set a low RPM (100) → press START
6. Verify the motor spins in the correct direction
7. If direction is wrong: swap A1↔A2 on the motor, OR invert in settings
8. Check RPM sensor: the gauge should show actual RPM
9. If RPM reads double: you have 2 magnets — set `magnets = 2` in config
10. Try **PID mode**: toggle OPEN → PID, set 500 RPM, motor should hold steady
11. Go to **Index** page → set 6 divisions → press NEXT
12. Verify the spindle moves exactly 60°
13. Press NEXT 5 more times — spindle should be back at exactly 0°

### PID Tuning

If RPM oscillates or is sluggish in PID mode:

1. Set Ki = 0, Kd = 0
2. Increase Kp until RPM reaches setpoint but oscillates slightly
3. Reduce Kp by ~30%
4. Slowly increase Ki until steady-state error disappears
5. Add small Kd if there's overshoot on speed changes

---

## 6. Troubleshooting

| Problem | Solution |
|---------|----------|
| "pigpio not installed" | `sudo apt install pigpio` then reboot |
| "pigpio daemon not running" | `sudo pigpiod` or `sudo systemctl start pigpiod` |
| Motor doesn't move | Check EN pin (active LOW), check 24V PSU, check wiring |
| Motor vibrates but doesn't spin | Swap one coil pair (A1↔A2 or B1↔B2) |
| RPM reads 0 | Check magnet alignment, sensor distance (<3mm), GPIO pin |
| RPM reads double | Set `magnets = 2` in config.ini |
| GUI won't start | `export DISPLAY=:0` or run from Pi desktop |
| UART errors | Check `/boot/config.txt` UART settings, reboot |
| Index position drifts | Check belt tension, reduce speed, verify gear ratio |
| E-Stop doesn't work | Must be wired NC (normally closed) |

---

## 7. File Structure

```
watchmaker/
├── config.ini              ← User configuration
├── requirements.txt        ← Python dependencies
├── install.sh              ← One-time setup script
├── run.sh                  ← Launch script
├── docs/
│   ├── BOM.md              ← Parts list
│   ├── WIRING.md           ← GPIO wiring guide
│   └── SETUP.md            ← This file
└── src/
    ├── main.py             ← Entry point
    ├── config.py           ← Config loader
    ├── motor.py            ← Stepper motor driver
    ├── rpm_sensor.py       ← Hall effect RPM sensor
    ├── pid.py              ← PID controller
    ├── indexer.py          ← Division math engine
    ├── presets.py           ← 120+ watchmaking presets
    ├── input_hw.py         ← Rotary encoder + buttons
    └── gui/
        ├── __init__.py
        ├── widgets.py      ← Gauge, graph, ring, buttons
        ├── lathe_page.py   ← Variable speed control
        ├── index_page.py   ← Division / indexing
        ├── preset_page.py  ← Preset browser
        ├── settings_page.py← Configuration editor
        └── app.py          ← Main application frame
```
