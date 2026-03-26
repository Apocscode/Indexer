"""
Watchmaker's Lathe Controller — Stepper Motor Driver
Controls TMC2209 via GPIO step/dir pulses and optional UART configuration.
Uses pigpio for hardware-timed step pulses (jitter-free).
"""

from __future__ import annotations

import logging
import time
import threading
from enum import Enum, auto
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import pigpio (Pi-only); fall back to mock for dev on other platforms
try:
    import pigpio
    HAS_PIGPIO = True
except ImportError:
    HAS_PIGPIO = False
    logger.warning("pigpio not available — running in simulation mode")


class MotorState(Enum):
    IDLE = auto()
    RUNNING = auto()        # Continuous rotation (lathe mode)
    INDEXING = auto()       # Moving a fixed number of steps
    JOGGING = auto()
    STOPPING = auto()
    ESTOP = auto()
    DISABLED = auto()


class StepperMotor:
    """
    High-level stepper motor controller.
    
    Uses pigpio wave chains for jitter-free step generation at up to
    hundreds of kHz — critical for smooth high-RPM lathe operation.
    """

    def __init__(self, config):
        self.cfg = config
        self.state = MotorState.DISABLED
        self._pi: Optional[pigpio.pi] = None
        self._wave_id = -1
        self._current_freq = 0.0       # Current step frequency (Hz)
        self._target_freq = 0.0        # Target step frequency
        self._direction = 1            # 1 = forward, -1 = reverse
        self._position = 0             # Absolute step position
        self._steps_remaining = 0      # For indexing moves
        self._lock = threading.Lock()
        self._ramp_thread: Optional[threading.Thread] = None
        self._ramp_running = False

        # Step counting callback
        self._step_cb = None

    # ================================================================
    # Initialization
    # ================================================================
    def init(self):
        """Initialize GPIO and pigpio daemon connection."""
        if not HAS_PIGPIO:
            logger.info("[MOTOR] Simulation mode — no GPIO available")
            self.state = MotorState.IDLE
            return True

        self._pi = pigpio.pi()
        if not self._pi.connected:
            logger.error("[MOTOR] Failed to connect to pigpio daemon!")
            logger.error("[MOTOR] Run: sudo pigpiod")
            return False

        # Configure pins
        self._pi.set_mode(self.cfg.gpio.pin_step, pigpio.OUTPUT)
        self._pi.set_mode(self.cfg.gpio.pin_dir, pigpio.OUTPUT)
        self._pi.set_mode(self.cfg.gpio.pin_enable, pigpio.OUTPUT)

        # Start disabled
        self._pi.write(self.cfg.gpio.pin_enable, 1)  # HIGH = disabled
        self._pi.write(self.cfg.gpio.pin_step, 0)
        self._set_direction(1)

        # Set up step counting callback
        self._step_cb = self._pi.callback(
            self.cfg.gpio.pin_step, pigpio.RISING_EDGE, self._on_step_pulse
        )

        self.state = MotorState.IDLE
        logger.info(f"[MOTOR] Initialized on GPIO STEP={self.cfg.gpio.pin_step} "
                     f"DIR={self.cfg.gpio.pin_dir} EN={self.cfg.gpio.pin_enable}")
        return True

    def shutdown(self):
        """Clean up GPIO resources."""
        self.emergency_stop()

        if self._step_cb:
            self._step_cb.cancel()
            self._step_cb = None

        if self._pi and self._pi.connected:
            self._stop_wave()
            self._pi.write(self.cfg.gpio.pin_enable, 1)  # Disable
            self._pi.stop()
            self._pi = None

        self.state = MotorState.DISABLED
        logger.info("[MOTOR] Shutdown complete")

    # ================================================================
    # Enable / Disable
    # ================================================================
    def enable(self):
        """Enable the motor driver."""
        if self._pi and self._pi.connected:
            self._pi.write(self.cfg.gpio.pin_enable, 0)  # Active LOW
            time.sleep(self.cfg.advanced.enable_delay_ms / 1000.0)
        if self.state == MotorState.DISABLED or self.state == MotorState.ESTOP:
            self.state = MotorState.IDLE
        logger.info("[MOTOR] Enabled")

    def disable(self):
        """Disable motor driver (motor free-wheels)."""
        self.stop()
        if self._pi and self._pi.connected:
            self._pi.write(self.cfg.gpio.pin_enable, 1)  # HIGH = disabled
        self.state = MotorState.DISABLED
        logger.info("[MOTOR] Disabled")

    # ================================================================
    # Continuous Rotation (Lathe Mode)
    # ================================================================
    def run_continuous(self, rpm: float, direction: int = 1):
        """
        Start continuous rotation at the specified spindle RPM.
        Ramps up smoothly from current speed.
        """
        if self.state == MotorState.ESTOP:
            logger.warning("[MOTOR] Cannot run — E-STOP active")
            return

        rpm = max(self.cfg.speed.min_rpm, min(rpm, self.cfg.speed.max_rpm))
        target_freq = self.cfg.rpm_to_step_freq(rpm)

        self._set_direction(direction)
        self._target_freq = target_freq
        self.state = MotorState.RUNNING

        # Start ramp thread if not already running
        if not self._ramp_running:
            self._ramp_running = True
            self._ramp_thread = threading.Thread(target=self._ramp_loop, daemon=True)
            self._ramp_thread.start()

        logger.info(f"[MOTOR] Run continuous: {rpm:.0f} RPM → {target_freq:.0f} Hz")

    def set_rpm(self, rpm: float):
        """Update target RPM while running (smooth transition)."""
        rpm = max(0, min(rpm, self.cfg.speed.max_rpm))
        if rpm < self.cfg.speed.min_rpm and rpm > 0:
            rpm = self.cfg.speed.min_rpm
        self._target_freq = self.cfg.rpm_to_step_freq(rpm)

    # ================================================================
    # Indexed Movement (Dividing Mode)
    # ================================================================
    def move_steps(self, steps: int, speed_hz: float = None):
        """
        Move a specific number of steps (signed).
        Blocks until movement is complete.
        """
        if self.state == MotorState.ESTOP:
            return

        if steps == 0:
            return

        direction = 1 if steps > 0 else -1
        abs_steps = abs(steps)
        self._set_direction(direction)

        if speed_hz is None:
            speed_hz = self.cfg.rpm_to_step_freq(self.cfg.speed.default_rpm)
            speed_hz = min(speed_hz, 50000)  # Cap for indexing moves

        self.state = MotorState.INDEXING
        self._steps_remaining = abs_steps

        self.enable()

        if self._pi and self._pi.connected:
            self._generate_step_burst(abs_steps, speed_hz)
        else:
            # Simulation: just update position
            time.sleep(abs_steps / max(speed_hz, 1))

        with self._lock:
            self._position += steps
            self._steps_remaining = 0

        self.state = MotorState.IDLE
        logger.debug(f"[MOTOR] Moved {steps} steps → position {self._position}")

    def move_steps_async(self, steps: int, speed_hz: float = None):
        """Non-blocking version of move_steps — runs in a thread."""
        t = threading.Thread(target=self.move_steps, args=(steps, speed_hz), daemon=True)
        t.start()
        return t

    # ================================================================
    # Stop / Emergency Stop
    # ================================================================
    def stop(self):
        """Graceful stop — ramp down to zero."""
        self._target_freq = 0
        self._ramp_running = False
        if self._ramp_thread and self._ramp_thread.is_alive():
            self._ramp_thread.join(timeout=2.0)
        self._stop_wave()
        self._current_freq = 0
        if self.state not in (MotorState.DISABLED, MotorState.ESTOP):
            self.state = MotorState.IDLE
        logger.info("[MOTOR] Stopped")

    def emergency_stop(self):
        """Instant stop — kills all motion immediately."""
        self._ramp_running = False
        self._target_freq = 0
        self._current_freq = 0
        self._stop_wave()
        self.state = MotorState.ESTOP
        logger.warning("[MOTOR] EMERGENCY STOP")

    def clear_estop(self):
        """Clear E-STOP state (must be called before motor can run again)."""
        if self.state == MotorState.ESTOP:
            self.state = MotorState.IDLE
            logger.info("[MOTOR] E-STOP cleared")

    # ================================================================
    # Position
    # ================================================================
    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, value: int):
        with self._lock:
            self._position = value

    @property
    def direction(self) -> int:
        return self._direction

    @property
    def current_freq(self) -> float:
        return self._current_freq

    @property
    def current_rpm(self) -> float:
        return self.cfg.step_freq_to_rpm(self._current_freq)

    @property
    def is_moving(self) -> bool:
        return self.state in (MotorState.RUNNING, MotorState.INDEXING, MotorState.JOGGING)

    # ================================================================
    # Internal: Direction
    # ================================================================
    def _set_direction(self, direction: int):
        """Set motor direction. 1=forward, -1=reverse."""
        self._direction = direction
        if self.cfg.motor.invert_direction:
            direction = -direction
        pin_val = 0 if direction >= 0 else 1
        if self._pi and self._pi.connected:
            self._pi.write(self.cfg.gpio.pin_dir, pin_val)

    # ================================================================
    # Internal: pigpio wave-based step generation
    # ================================================================
    def _start_wave(self, freq_hz: float):
        """Start a continuous step waveform at the given frequency."""
        if not self._pi or not self._pi.connected:
            return
        if freq_hz < 1:
            self._stop_wave()
            return

        self._stop_wave()

        period_us = int(1_000_000 / freq_hz)
        pulse_us = max(self.cfg.advanced.step_pulse_us, 2)
        off_us = max(period_us - pulse_us, 2)

        wf = [
            pigpio.pulse(1 << self.cfg.gpio.pin_step, 0, pulse_us),
            pigpio.pulse(0, 1 << self.cfg.gpio.pin_step, off_us),
        ]

        self._pi.wave_clear()
        self._pi.wave_add_generic(wf)
        self._wave_id = self._pi.wave_create()

        if self._wave_id >= 0:
            self._pi.wave_send_repeat(self._wave_id)
            self._current_freq = freq_hz

    def _stop_wave(self):
        """Stop any active waveform."""
        if not self._pi or not self._pi.connected:
            return
        self._pi.wave_tx_stop()
        if self._wave_id >= 0:
            try:
                self._pi.wave_delete(self._wave_id)
            except Exception:
                pass
            self._wave_id = -1
        self._pi.write(self.cfg.gpio.pin_step, 0)

    def _generate_step_burst(self, steps: int, freq_hz: float):
        """Generate a fixed number of step pulses with trapezoidal profile."""
        if not self._pi or not self._pi.connected:
            return

        # Simple approach: use pigpio's wave chain for fixed step count
        # For short moves, just bit-bang at the target frequency
        period_us = int(1_000_000 / min(freq_hz, 500_000))
        pulse_us = max(self.cfg.advanced.step_pulse_us, 2)
        off_us = max(period_us - pulse_us, 2)

        # For small step counts, use direct GPIO toggling (more responsive)
        if steps <= 10000:
            for _ in range(steps):
                if self.state == MotorState.ESTOP:
                    break
                self._pi.gpio_trigger(self.cfg.gpio.pin_step, pulse_us, 1)
                time.sleep(off_us / 1_000_000.0)
        else:
            # For larger moves, use wave chains
            wf = [
                pigpio.pulse(1 << self.cfg.gpio.pin_step, 0, pulse_us),
                pigpio.pulse(0, 1 << self.cfg.gpio.pin_step, off_us),
            ]
            self._pi.wave_clear()
            self._pi.wave_add_generic(wf)
            wid = self._pi.wave_create()

            if wid >= 0:
                # Build chain: repeat wave `steps` times
                chain = []
                remaining = steps
                while remaining > 0:
                    count = min(remaining, 65535)
                    chain += [255, 0, wid, 255, 1, count & 0xFF, (count >> 8) & 0xFF]
                    remaining -= count

                self._pi.wave_chain(chain)

                # Wait for completion
                while self._pi.wave_tx_busy():
                    if self.state == MotorState.ESTOP:
                        self._pi.wave_tx_stop()
                        break
                    time.sleep(0.01)

                try:
                    self._pi.wave_delete(wid)
                except Exception:
                    pass

    # ================================================================
    # Internal: Speed ramping thread
    # ================================================================
    def _ramp_loop(self):
        """Background thread: smoothly ramp step frequency toward target."""
        ramp_interval = 0.02  # 50 Hz update rate

        while self._ramp_running:
            with self._lock:
                target = self._target_freq
                current = self._current_freq

            if abs(target - current) < 10:
                # Close enough — snap to target
                if target > 0:
                    self._start_wave(target)
                else:
                    self._stop_wave()
                    self._current_freq = 0
                    self.state = MotorState.IDLE
                    break
            else:
                # Calculate ramp
                if target > current:
                    # Accelerating
                    accel_hz = self.cfg.rpm_to_step_freq(self.cfg.speed.accel_rpm_per_sec)
                    step = accel_hz * ramp_interval
                    new_freq = min(current + step, target)
                else:
                    # Decelerating
                    decel_hz = self.cfg.rpm_to_step_freq(self.cfg.speed.decel_rpm_per_sec)
                    step = decel_hz * ramp_interval
                    new_freq = max(current - step, target)

                if new_freq < 10:
                    self._stop_wave()
                    self._current_freq = 0
                    if target <= 0:
                        self.state = MotorState.IDLE
                        break
                else:
                    self._start_wave(new_freq)

            time.sleep(ramp_interval)

        self._ramp_running = False

    # ================================================================
    # Internal: Step counting callback
    # ================================================================
    def _on_step_pulse(self, gpio, level, tick):
        """Called on every step pulse rising edge — tracks position."""
        with self._lock:
            self._position += self._direction
            if self._steps_remaining > 0:
                self._steps_remaining -= 1
