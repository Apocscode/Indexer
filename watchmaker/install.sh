#!/usr/bin/env bash
# ============================================================================
# Watchmaker's Lathe Controller — Installation Script
# Run on Raspberry Pi:  chmod +x install.sh && sudo ./install.sh
# ============================================================================

set -e

echo "============================================"
echo " Watchmaker's Lathe Controller — Installer"
echo "============================================"
echo ""

# ---- System packages ------------------------------------------------------
echo "[1/5] Updating system packages..."
apt-get update -y
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-tk \
    pigpio \
    fonts-dejavu-core

# ---- Enable hardware interfaces -------------------------------------------
echo "[2/5] Enabling hardware interfaces..."

# Enable hardware UART (for TMC2209)
if ! grep -q "enable_uart=1" /boot/config.txt 2>/dev/null && \
   ! grep -q "enable_uart=1" /boot/firmware/config.txt 2>/dev/null; then
    CONFIG_FILE="/boot/config.txt"
    [ -f /boot/firmware/config.txt ] && CONFIG_FILE="/boot/firmware/config.txt"
    echo "" >> "$CONFIG_FILE"
    echo "# Watchmaker Lathe Controller — UART for TMC2209" >> "$CONFIG_FILE"
    echo "enable_uart=1" >> "$CONFIG_FILE"
    echo "dtoverlay=disable-bt" >> "$CONFIG_FILE"
    echo "  → UART enabled in $CONFIG_FILE (reboot required)"
fi

# Disable serial console (frees up UART)
if [ -f /boot/cmdline.txt ]; then
    sed -i 's/console=serial0,[0-9]* //g' /boot/cmdline.txt 2>/dev/null || true
fi

# ---- pigpio daemon ---------------------------------------------------------
echo "[3/5] Configuring pigpio daemon..."
systemctl enable pigpiod
systemctl start pigpiod || true
echo "  → pigpiod enabled and started"

# ---- Python virtual environment -------------------------------------------
echo "[4/5] Setting up Python environment..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"
deactivate

echo "  → Virtual environment created at $VENV_DIR"

# ---- Auto-start (optional) ------------------------------------------------
echo "[5/5] Setting up auto-start service..."

SERVICE_FILE="/etc/systemd/system/watchmaker-lathe.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Watchmaker's Lathe Controller
After=pigpiod.service graphical.target
Wants=pigpiod.service

[Service]
Type=simple
User=$SUDO_USER
Environment=DISPLAY=:0
ExecStart=$VENV_DIR/bin/python $SCRIPT_DIR/src/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

systemctl daemon-reload
echo "  → Service file created: $SERVICE_FILE"
echo "  → To enable auto-start:  sudo systemctl enable watchmaker-lathe"
echo "  → To start now:          sudo systemctl start watchmaker-lathe"

echo ""
echo "============================================"
echo " Installation complete!"
echo ""
echo " To run manually:"
echo "   cd $SCRIPT_DIR"
echo "   ./run.sh"
echo ""
echo " ⚠ REBOOT REQUIRED for UART changes!"
echo "   sudo reboot"
echo "============================================"
