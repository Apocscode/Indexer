"""
Watchmaker's Lathe Controller — Configuration Loader
Reads config.ini and provides typed access to all settings.
"""

import configparser
import os
import logging
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini")


@dataclass
class MotorConfig:
    steps_per_rev: int = 400
    microsteps: int = 256
    current_ma: int = 1200
    hold_current_ma: int = 400
    invert_direction: bool = False


@dataclass
class GearConfig:
    motor_teeth: int = 20
    spindle_teeth: int = 60

    @property
    def ratio(self) -> float:
        return self.spindle_teeth / self.motor_teeth

    @property
    def total_steps_per_rev(self) -> int:
        """Total microsteps for one spindle revolution."""
        # We need motor config for this — computed externally
        raise NotImplementedError("Use Config.total_steps_per_rev instead")


@dataclass
class SpeedConfig:
    min_rpm: float = 50.0
    max_rpm: float = 8000.0
    default_rpm: float = 500.0
    accel_rpm_per_sec: float = 500.0
    decel_rpm_per_sec: float = 800.0
    soft_start_ms: int = 1000


@dataclass
class PIDConfig:
    kp: float = 0.8
    ki: float = 0.3
    kd: float = 0.05
    sample_rate_hz: float = 20.0
    output_min: float = 0.0
    output_max: float = 1.0
    integral_max: float = 100.0


@dataclass
class RPMSensorConfig:
    enabled: bool = True
    gpio_pin: int = 23
    pulses_per_rev: int = 1
    filter_samples: int = 4
    timeout_ms: int = 2000


@dataclass
class GPIOConfig:
    pin_step: int = 17
    pin_dir: int = 27
    pin_enable: int = 22
    pin_uart_tx: int = 14
    pin_uart_rx: int = 15
    pin_enc_clk: int = 5
    pin_enc_dt: int = 6
    pin_enc_sw: int = 13
    pin_btn_mode: int = 16
    pin_btn_go_stop: int = 20
    pin_btn_estop: int = 21


@dataclass
class DisplayConfig:
    fullscreen: bool = True
    width: int = 800
    height: int = 480
    theme: str = "dark"
    font_size: int = 14
    show_rpm_graph: bool = True
    graph_history_sec: int = 30


@dataclass
class IndexingConfig:
    default_divisions: int = 6
    jog_increments: List[float] = field(default_factory=lambda: [0.01, 0.1, 1.0, 5.0, 10.0])
    default_jog_index: int = 2


@dataclass
class AdvancedConfig:
    step_pulse_us: int = 2
    dir_setup_us: int = 5
    enable_delay_ms: int = 10
    uart_baud: int = 115200
    log_level: str = "INFO"


class Config:
    """Master configuration container — loads from config.ini."""

    def __init__(self, path: str = None):
        self.path = path or CONFIG_PATH
        self.motor = MotorConfig()
        self.gear = GearConfig()
        self.speed = SpeedConfig()
        self.pid = PIDConfig()
        self.rpm_sensor = RPMSensorConfig()
        self.gpio = GPIOConfig()
        self.display = DisplayConfig()
        self.indexing = IndexingConfig()
        self.advanced = AdvancedConfig()

        if os.path.exists(self.path):
            self._load()
            logger.info(f"Config loaded from {self.path}")
        else:
            logger.warning(f"Config file not found at {self.path}, using defaults")

    def _load(self):
        cp = configparser.ConfigParser()
        cp.read(self.path)

        def get_bool(section, key, default):
            try:
                val = cp.get(section, key).strip().lower()
                return val in ("true", "yes", "1", "on")
            except (configparser.NoSectionError, configparser.NoOptionError):
                return default

        def get_int(section, key, default):
            try:
                return cp.getint(section, key)
            except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
                return default

        def get_float(section, key, default):
            try:
                return cp.getfloat(section, key)
            except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
                return default

        def get_str(section, key, default):
            try:
                return cp.get(section, key).strip()
            except (configparser.NoSectionError, configparser.NoOptionError):
                return default

        # Motor
        self.motor.steps_per_rev = get_int("motor", "steps_per_rev", 400)
        self.motor.microsteps = get_int("motor", "microsteps", 256)
        self.motor.current_ma = get_int("motor", "current_ma", 1200)
        self.motor.hold_current_ma = get_int("motor", "hold_current_ma", 400)
        self.motor.invert_direction = get_bool("motor", "invert_direction", False)

        # Gear ratio
        self.gear.motor_teeth = get_int("gear_ratio", "motor_teeth", 20)
        self.gear.spindle_teeth = get_int("gear_ratio", "spindle_teeth", 60)

        # Speed
        self.speed.min_rpm = get_float("speed", "min_rpm", 50.0)
        self.speed.max_rpm = get_float("speed", "max_rpm", 8000.0)
        self.speed.default_rpm = get_float("speed", "default_rpm", 500.0)
        self.speed.accel_rpm_per_sec = get_float("speed", "accel_rpm_per_sec", 500.0)
        self.speed.decel_rpm_per_sec = get_float("speed", "decel_rpm_per_sec", 800.0)
        self.speed.soft_start_ms = get_int("speed", "soft_start_ms", 1000)

        # PID
        self.pid.kp = get_float("pid", "kp", 0.8)
        self.pid.ki = get_float("pid", "ki", 0.3)
        self.pid.kd = get_float("pid", "kd", 0.05)
        self.pid.sample_rate_hz = get_float("pid", "sample_rate_hz", 20.0)
        self.pid.output_min = get_float("pid", "output_min", 0.0)
        self.pid.output_max = get_float("pid", "output_max", 1.0)
        self.pid.integral_max = get_float("pid", "integral_max", 100.0)

        # RPM sensor
        self.rpm_sensor.enabled = get_bool("rpm_sensor", "enabled", True)
        self.rpm_sensor.gpio_pin = get_int("rpm_sensor", "gpio_pin", 23)
        self.rpm_sensor.pulses_per_rev = get_int("rpm_sensor", "pulses_per_rev", 1)
        self.rpm_sensor.filter_samples = get_int("rpm_sensor", "filter_samples", 4)
        self.rpm_sensor.timeout_ms = get_int("rpm_sensor", "timeout_ms", 2000)

        # GPIO
        self.gpio.pin_step = get_int("gpio", "pin_step", 17)
        self.gpio.pin_dir = get_int("gpio", "pin_dir", 27)
        self.gpio.pin_enable = get_int("gpio", "pin_enable", 22)
        self.gpio.pin_uart_tx = get_int("gpio", "pin_uart_tx", 14)
        self.gpio.pin_uart_rx = get_int("gpio", "pin_uart_rx", 15)
        self.gpio.pin_enc_clk = get_int("gpio", "pin_enc_clk", 5)
        self.gpio.pin_enc_dt = get_int("gpio", "pin_enc_dt", 6)
        self.gpio.pin_enc_sw = get_int("gpio", "pin_enc_sw", 13)
        self.gpio.pin_btn_mode = get_int("gpio", "pin_btn_mode", 16)
        self.gpio.pin_btn_go_stop = get_int("gpio", "pin_btn_go_stop", 20)
        self.gpio.pin_btn_estop = get_int("gpio", "pin_btn_estop", 21)

        # Display
        self.display.fullscreen = get_bool("display", "fullscreen", True)
        self.display.width = get_int("display", "width", 800)
        self.display.height = get_int("display", "height", 480)
        self.display.theme = get_str("display", "theme", "dark")
        self.display.font_size = get_int("display", "font_size", 14)
        self.display.show_rpm_graph = get_bool("display", "show_rpm_graph", True)
        self.display.graph_history_sec = get_int("display", "graph_history_sec", 30)

        # Indexing
        self.indexing.default_divisions = get_int("indexing", "default_divisions", 6)
        self.indexing.default_jog_index = get_int("indexing", "default_jog_index", 2)
        try:
            raw = cp.get("indexing", "jog_increments")
            self.indexing.jog_increments = [float(x.strip()) for x in raw.split(",")]
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

        # Advanced
        self.advanced.step_pulse_us = get_int("advanced", "step_pulse_us", 2)
        self.advanced.dir_setup_us = get_int("advanced", "dir_setup_us", 5)
        self.advanced.enable_delay_ms = get_int("advanced", "enable_delay_ms", 10)
        self.advanced.uart_baud = get_int("advanced", "uart_baud", 115200)
        self.advanced.log_level = get_str("advanced", "log_level", "INFO")

    @property
    def gear_ratio(self) -> float:
        return self.gear.spindle_teeth / self.gear.motor_teeth

    @property
    def total_steps_per_rev(self) -> int:
        """Total microsteps for one full spindle revolution."""
        return int(self.motor.steps_per_rev * self.motor.microsteps * self.gear_ratio)

    @property
    def degrees_per_step(self) -> float:
        """Angular resolution in degrees per microstep at the spindle."""
        return 360.0 / self.total_steps_per_rev

    def rpm_to_step_freq(self, rpm: float) -> float:
        """Convert spindle RPM to step pulse frequency (Hz)."""
        if rpm <= 0:
            return 0.0
        motor_rpm = rpm * self.gear_ratio
        steps_per_sec = (motor_rpm / 60.0) * self.motor.steps_per_rev * self.motor.microsteps
        return steps_per_sec

    def step_freq_to_rpm(self, freq: float) -> float:
        """Convert step frequency (Hz) to spindle RPM."""
        if freq <= 0:
            return 0.0
        motor_rps = freq / (self.motor.steps_per_rev * self.motor.microsteps)
        motor_rpm = motor_rps * 60.0
        spindle_rpm = motor_rpm / self.gear_ratio
        return spindle_rpm

    def __repr__(self):
        return (
            f"Config(steps/rev={self.motor.steps_per_rev}, µsteps={self.motor.microsteps}, "
            f"gear={self.gear_ratio:.1f}:1, total_steps={self.total_steps_per_rev}, "
            f"resolution={self.degrees_per_step:.6f}°)"
        )
