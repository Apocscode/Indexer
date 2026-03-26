#!/usr/bin/env bash
# ============================================================================
# Watchmaker's Lathe Controller — Launch Script
# Usage:  ./run.sh [options]
#   ./run.sh              — Normal launch (fullscreen on Pi display)
#   ./run.sh --demo       — Demo mode (no hardware needed)
#   ./run.sh --windowed   — Windowed mode
#   ./run.sh --theme light
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

# Set display for Pi (if not set)
export DISPLAY="${DISPLAY:-:0}"

# Ensure pigpiod is running
if ! pgrep -x pigpiod > /dev/null 2>&1; then
    echo "Starting pigpio daemon..."
    sudo pigpiod 2>/dev/null || echo "Warning: Could not start pigpiod (run with sudo or install.sh first)"
fi

# Launch
cd "$SCRIPT_DIR"
exec python3 src/main.py "$@"
