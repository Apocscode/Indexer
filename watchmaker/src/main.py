"""
Watchmaker's Lathe Controller — Entry Point
Initializes hardware subsystems, loads config, and launches the GUI.

Usage:
    python main.py              # Normal launch
    python main.py --demo       # Demo mode (no hardware)
    python main.py --windowed   # Windowed mode (not fullscreen)
    python main.py --theme light
"""

import sys
import os
import signal
import logging
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.motor import StepperMotor
from src.rpm_sensor import RPMSensor
from src.pid import PIDController
from src.indexer import Indexer
from src.input_hw import HardwareInput
from src.gui.app import App, AppController

# ============================================================================
# Logging
# ============================================================================
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                os.path.join(os.path.dirname(__file__), "..", "watchmaker.log"),
                mode="a"
            ),
        ]
    )


logger = logging.getLogger("watchmaker")


# ============================================================================
# Main
# ============================================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Watchmaker's Lathe Controller")
    parser.add_argument("--demo", action="store_true",
                       help="Run in demo mode without hardware")
    parser.add_argument("--windowed", action="store_true",
                       help="Run in windowed mode")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark",
                       help="UI color theme")
    parser.add_argument("--config", type=str, default=None,
                       help="Path to config.ini file")
    parser.add_argument("--log-level", type=str, default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    parser.add_argument("--width", type=int, default=800,
                       help="Window width (windowed mode)")
    parser.add_argument("--height", type=int, default=480,
                       help="Window height (windowed mode)")
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args.log_level)

    logger.info("=" * 60)
    logger.info("Watchmaker's Lathe Controller starting")
    logger.info("=" * 60)

    # ---- Load configuration -------------------------------------------
    config_path = args.config or os.path.join(
        os.path.dirname(__file__), "..", "config.ini")
    config_path = os.path.abspath(config_path)

    logger.info(f"Loading config: {config_path}")
    config = Config.load(config_path)
    logger.info(f"  Steps/rev: {config.total_steps_per_rev}")
    logger.info(f"  Gear ratio: {config.gear.spindle_teeth / config.gear.motor_teeth:.2f}:1")
    logger.info(f"  Max RPM: {config.speed.max_rpm}")

    # ---- Initialize hardware ------------------------------------------
    demo = args.demo
    pi = None

    if not demo:
        try:
            import pigpio
            pi = pigpio.pi()
            if not pi.connected:
                logger.warning("pigpio daemon not running — falling back to demo mode")
                logger.warning("Start with: sudo pigpiod")
                demo = True
                pi = None
        except ImportError:
            logger.warning("pigpio not installed — falling back to demo mode")
            demo = True

    if demo:
        logger.info("Running in DEMO mode (no hardware)")

    # Motor
    motor = StepperMotor(
        pi=pi,
        step_pin=config.gpio.step_pin,
        dir_pin=config.gpio.dir_pin,
        enable_pin=config.gpio.enable_pin,
        steps_per_rev=config.motor.steps_per_rev,
        microsteps=config.motor.microsteps
    )
    motor.enable()
    logger.info("Motor initialized")

    # RPM Sensor
    rpm_sensor = RPMSensor(
        pi=pi,
        gpio_pin=config.gpio.rpm_pin,
        magnets=config.rpm_sensor.magnets,
        filter_size=config.rpm_sensor.filter_size,
        timeout_s=config.rpm_sensor.timeout_s
    )
    rpm_sensor.start()
    logger.info("RPM sensor initialized")

    # PID Controller
    pid = PIDController(
        kp=config.pid.kp,
        ki=config.pid.ki,
        kd=config.pid.kd,
        output_min=config.pid.output_min,
        output_max=config.pid.output_max,
        sample_interval=config.pid.sample_interval
    )
    logger.info("PID controller initialized")

    # Indexer
    indexer = Indexer(
        total_steps_per_rev=config.total_steps_per_rev,
        default_divisions=config.indexing.default_divisions
    )
    logger.info(f"Indexer initialized: {config.indexing.default_divisions} divisions")

    # Hardware Input
    hw_input = HardwareInput(
        pi=pi,
        enc_clk=config.gpio.enc_clk,
        enc_dt=config.gpio.enc_dt,
        enc_sw=config.gpio.enc_sw,
        btn_mode=config.gpio.btn_mode,
        btn_go=config.gpio.btn_go,
        btn_estop=config.gpio.btn_estop
    )
    hw_input.start()
    logger.info("Hardware input initialized")

    # ---- Create controller & GUI --------------------------------------
    controller = AppController(
        config=config,
        motor=motor,
        rpm_sensor=rpm_sensor,
        pid_controller=pid,
        indexer=indexer,
        hw_input=hw_input
    )

    app = App(
        controller=controller,
        fullscreen=not args.windowed,
        width=args.width,
        height=args.height,
        theme_name=args.theme
    )

    # ---- Signal handlers ----------------------------------------------
    def shutdown_handler(signum, frame):
        logger.info(f"Signal {signum} received — shutting down")
        cleanup(motor, rpm_sensor, hw_input, pi)
        app.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # ---- Run -----------------------------------------------------------
    logger.info("GUI ready — entering main loop")
    try:
        app.run()
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
    finally:
        cleanup(motor, rpm_sensor, hw_input, pi)

    logger.info("Shutdown complete")


def cleanup(motor, rpm_sensor, hw_input, pi):
    """Release all hardware resources."""
    logger.info("Cleaning up hardware resources")
    try:
        motor.disable()
    except Exception:
        pass
    try:
        rpm_sensor.stop()
    except Exception:
        pass
    try:
        hw_input.stop()
    except Exception:
        pass
    if pi:
        try:
            pi.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
