#pragma once
// ============================================================================
// Stepper Motor Controller — Header
// Handles TMC2209 communication and AccelStepper motion control
// ============================================================================

#include <Arduino.h>

/// Motion state of the stepper
enum class MotionState {
    IDLE,
    MOVING,
    HOMING,
    JOGGING,
    EMERGENCY_STOP
};

/// Initialize the stepper driver (TMC2209 via UART) and AccelStepper
void stepper_init();

/// Enable or disable the motor driver
void stepper_enable(bool enabled);

/// Move a specific number of steps (signed: + = CW, - = CCW)
void stepper_move_steps(long steps);

/// Move to an absolute step position
void stepper_move_to(long position);

/// Must be called every loop iteration to process step pulses
/// Returns true if motor is still moving
bool stepper_run();

/// Stop the motor immediately (decelerate to stop)
void stepper_stop();

/// Emergency stop — kill motion instantly (may lose position)
void stepper_emergency_stop();

/// Get the current absolute position in steps
long stepper_get_position();

/// Set the current position as a new reference (redefine zero)
void stepper_set_position(long position);

/// Get current motion state
MotionState stepper_get_state();

/// Check if motor is currently moving
bool stepper_is_moving();

/// Set maximum speed (steps/sec)
void stepper_set_max_speed(float speed);

/// Set acceleration (steps/sec²)
void stepper_set_acceleration(float accel);

/// Get the distance remaining in current move
long stepper_distance_to_go();
