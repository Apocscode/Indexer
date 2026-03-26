"""
Watchmaker's Lathe Controller — PID Controller
Closed-loop RPM regulation using sensor feedback.
"""

import time
import logging

logger = logging.getLogger(__name__)


class PIDController:
    """
    Discrete PID controller for RPM regulation.
    
    Adjusts motor step frequency to maintain target RPM based on
    sensor feedback. Includes anti-windup, derivative filtering,
    and output clamping.
    """

    def __init__(self, config):
        self.cfg = config
        self.kp = config.pid.kp
        self.ki = config.pid.ki
        self.kd = config.pid.kd
        self.output_min = config.pid.output_min
        self.output_max = config.pid.output_max
        self.integral_max = config.pid.integral_max

        # Internal state
        self._setpoint = 0.0         # Target RPM
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = 0.0
        self._output = 0.0
        self._enabled = False

        # Derivative filter (low-pass to reduce noise)
        self._d_filter_alpha = 0.1
        self._d_filtered = 0.0

    # ================================================================
    # Control
    # ================================================================
    @property
    def setpoint(self) -> float:
        return self._setpoint

    @setpoint.setter
    def setpoint(self, rpm: float):
        self._setpoint = max(0.0, rpm)
        logger.debug(f"[PID] Setpoint: {rpm:.0f} RPM")

    @property
    def output(self) -> float:
        """Current PID output (0.0 to 1.0 frequency multiplier)."""
        return self._output

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self):
        """Enable PID control loop."""
        self.reset()
        self._enabled = True
        logger.info("[PID] Enabled")

    def disable(self):
        """Disable PID — output holds at last value."""
        self._enabled = False
        logger.info("[PID] Disabled")

    def reset(self):
        """Reset all PID state."""
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = time.monotonic()
        self._output = 0.0
        self._d_filtered = 0.0

    # ================================================================
    # Update — call at sample_rate_hz
    # ================================================================
    def update(self, measured_rpm: float) -> float:
        """
        Compute PID output given current measured RPM.
        
        Returns:
            Output value between output_min and output_max.
            This is a multiplier applied to the step frequency.
        """
        if not self._enabled or self._setpoint <= 0:
            self._output = 0.0
            return 0.0

        now = time.monotonic()
        dt = now - self._prev_time
        if dt <= 0:
            return self._output
        self._prev_time = now

        # Error
        error = self._setpoint - measured_rpm

        # Proportional
        p_term = self.kp * error

        # Integral with anti-windup
        self._integral += error * dt
        self._integral = max(-self.integral_max, min(self._integral, self.integral_max))
        i_term = self.ki * self._integral

        # Derivative with low-pass filter
        raw_derivative = (error - self._prev_error) / dt
        self._d_filtered = (self._d_filter_alpha * raw_derivative +
                           (1.0 - self._d_filter_alpha) * self._d_filtered)
        d_term = self.kd * self._d_filtered
        self._prev_error = error

        # Sum and clamp
        output = p_term + i_term + d_term
        output = max(self.output_min, min(output, self.output_max))

        self._output = output
        return output

    # ================================================================
    # Tuning
    # ================================================================
    def set_gains(self, kp: float, ki: float, kd: float):
        """Update PID gains at runtime."""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.reset()
        logger.info(f"[PID] Gains updated: Kp={kp}, Ki={ki}, Kd={kd}")

    def get_diagnostics(self) -> dict:
        """Return PID internal state for debugging/display."""
        return {
            "setpoint": self._setpoint,
            "output": self._output,
            "integral": self._integral,
            "prev_error": self._prev_error,
            "d_filtered": self._d_filtered,
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd,
            "enabled": self._enabled,
        }
