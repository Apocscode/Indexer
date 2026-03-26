"""
Watchmaker's Lathe Controller — RPM Sensor
Interrupt-driven Hall effect / optical sensor for closed-loop RPM measurement.
"""

import logging
import time
import threading
from collections import deque
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import pigpio
    HAS_PIGPIO = True
except ImportError:
    HAS_PIGPIO = False


class RPMSensor:
    """
    Measures spindle RPM using a Hall effect or optical sensor.
    
    The sensor produces one pulse per spindle revolution (or per
    pulses_per_rev revolutions). RPM is calculated from the time
    between consecutive pulses using a moving average filter.
    """

    def __init__(self, config):
        self.cfg = config
        self._pi: Optional[pigpio.pi] = None
        self._callback = None
        self._enabled = config.rpm_sensor.enabled

        # Pulse timing
        self._last_tick = 0
        self._pulse_intervals = deque(maxlen=config.rpm_sensor.filter_samples)
        self._rpm = 0.0
        self._peak_rpm = 0.0
        self._pulse_count = 0
        self._lock = threading.Lock()

        # RPM history for graphing
        self._history = deque(maxlen=600)  # 30 sec at 20 Hz
        self._history_thread: Optional[threading.Thread] = None
        self._recording = False

    # ================================================================
    # Init / Shutdown
    # ================================================================
    def init(self, pi: pigpio.pi = None):
        """Initialize the RPM sensor GPIO interrupt."""
        if not self._enabled:
            logger.info("[RPM] Sensor disabled in config")
            return True

        if not HAS_PIGPIO:
            logger.info("[RPM] Simulation mode — no GPIO")
            return True

        if pi:
            self._pi = pi
        else:
            self._pi = pigpio.pi()
            if not self._pi.connected:
                logger.error("[RPM] Failed to connect to pigpio daemon")
                return False

        pin = self.cfg.rpm_sensor.gpio_pin
        self._pi.set_mode(pin, pigpio.INPUT)
        self._pi.set_pull_up_down(pin, pigpio.PUD_UP)

        # Glitch filter: ignore pulses shorter than 100µs (noise)
        self._pi.set_glitch_filter(pin, 100)

        # Register falling-edge callback (Hall sensor pulls LOW when magnet passes)
        self._callback = self._pi.callback(pin, pigpio.FALLING_EDGE, self._on_pulse)

        # Start history recording
        self._recording = True
        self._history_thread = threading.Thread(target=self._history_loop, daemon=True)
        self._history_thread.start()

        logger.info(f"[RPM] Sensor initialized on GPIO {pin}, "
                     f"pulses/rev={self.cfg.rpm_sensor.pulses_per_rev}")
        return True

    def shutdown(self):
        """Release sensor resources."""
        self._recording = False
        if self._history_thread and self._history_thread.is_alive():
            self._history_thread.join(timeout=2.0)

        if self._callback:
            self._callback.cancel()
            self._callback = None

        logger.info("[RPM] Sensor shutdown")

    # ================================================================
    # RPM Reading
    # ================================================================
    @property
    def rpm(self) -> float:
        """Current smoothed RPM reading."""
        with self._lock:
            # Check for timeout (spindle stopped)
            if HAS_PIGPIO and self._pi and self._last_tick > 0:
                now = self._pi.get_current_tick()
                elapsed_us = pigpio.tickDiff(self._last_tick, now)
                if elapsed_us > self.cfg.rpm_sensor.timeout_ms * 1000:
                    self._rpm = 0.0
                    self._pulse_intervals.clear()
            return self._rpm

    @property
    def peak_rpm(self) -> float:
        """Peak RPM recorded since last reset."""
        return self._peak_rpm

    @property
    def pulse_count(self) -> int:
        """Total pulse count since init."""
        return self._pulse_count

    @property
    def history(self) -> list:
        """RPM history as a list of (timestamp, rpm) tuples."""
        with self._lock:
            return list(self._history)

    def reset_peak(self):
        """Reset peak RPM tracker."""
        self._peak_rpm = 0.0

    # ================================================================
    # Simulated RPM (for testing without hardware)
    # ================================================================
    def set_simulated_rpm(self, rpm: float):
        """Set RPM value directly (for simulation/testing)."""
        with self._lock:
            self._rpm = rpm
            if rpm > self._peak_rpm:
                self._peak_rpm = rpm

    # ================================================================
    # Internal: Pulse callback
    # ================================================================
    def _on_pulse(self, gpio, level, tick):
        """Called on each sensor pulse (falling edge)."""
        with self._lock:
            self._pulse_count += 1

            if self._last_tick > 0:
                # Calculate interval in microseconds
                interval_us = pigpio.tickDiff(self._last_tick, tick)

                if interval_us > 0:
                    self._pulse_intervals.append(interval_us)

                    # Calculate RPM from moving average
                    if len(self._pulse_intervals) > 0:
                        avg_interval = sum(self._pulse_intervals) / len(self._pulse_intervals)
                        # RPM = (60 seconds × 1,000,000 µs/s) / (interval_µs × pulses_per_rev)
                        self._rpm = 60_000_000.0 / (avg_interval * self.cfg.rpm_sensor.pulses_per_rev)

                        if self._rpm > self._peak_rpm:
                            self._peak_rpm = self._rpm

            self._last_tick = tick

    # ================================================================
    # Internal: History recording
    # ================================================================
    def _history_loop(self):
        """Record RPM history at a fixed rate for graphing."""
        interval = 1.0 / self.cfg.pid.sample_rate_hz

        while self._recording:
            with self._lock:
                self._history.append((time.time(), self._rpm))
            time.sleep(interval)
