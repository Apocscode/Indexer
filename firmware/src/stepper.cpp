// ============================================================================
// Stepper Motor Controller — Implementation
// TMC2209 UART + AccelStepper for smooth motion control
// ============================================================================

#include "stepper.h"
#include "config.h"
#include <AccelStepper.h>
#include <TMCStepper.h>

// --- TMC2209 UART driver instance ---
// Single-wire UART on PIN_UART, R_sense = 0.11Ω (typical for BTT TMC2209)
#define R_SENSE   0.11f
#define DRIVER_ADDRESS 0b00  // MS1=LOW, MS2=LOW

static HardwareSerial &driverSerial = Serial1;
static TMC2209Stepper tmc_driver(&driverSerial, R_SENSE, DRIVER_ADDRESS);

// --- AccelStepper instance ---
static AccelStepper accelStepper(AccelStepper::DRIVER, PIN_STEP, PIN_DIR);

// --- State tracking ---
static MotionState currentState = MotionState::IDLE;

// ============================================================================
// Initialization
// ============================================================================
void stepper_init() {
    // Configure GPIO
    pinMode(PIN_EN, OUTPUT);
    digitalWrite(PIN_EN, HIGH);  // Disabled at start (EN is active LOW)

    // Start UART for TMC2209
    // ESP32 Serial1: we remap TX/RX to the same pin for single-wire UART
    driverSerial.begin(115200, SERIAL_8N1, PIN_UART, PIN_UART);

    // Initialize TMC2209
    tmc_driver.begin();
    tmc_driver.toff(4);                      // Enable driver (toff > 0)
    tmc_driver.rms_current(MOTOR_CURRENT_MA); // Set motor RMS current
    tmc_driver.microsteps(MICROSTEPS);        // Set microstepping
    tmc_driver.pwm_autoscale(true);           // Enable StealthChop auto-tuning
    tmc_driver.en_spreadCycle(false);         // StealthChop mode (quiet)
    tmc_driver.ihold(calcIhold());            // Hold current
    tmc_driver.iholddelay(6);                 // Delay before reducing to hold current

    // Verify UART communication
    uint8_t result = tmc_driver.test_connection();
    if (result != 0) {
        Serial.println(F("[STEPPER] WARNING: TMC2209 UART communication failed!"));
        Serial.print(F("[STEPPER] test_connection() = "));
        Serial.println(result);
    } else {
        Serial.println(F("[STEPPER] TMC2209 initialized OK via UART"));
        Serial.print(F("[STEPPER] Microsteps: "));
        Serial.println(tmc_driver.microsteps());
    }

    // Configure AccelStepper
    if (INVERT_DIRECTION) {
        accelStepper.setPinsInverted(true, false, false);
    }
    accelStepper.setMaxSpeed(MAX_SPEED_STEPS_SEC);
    accelStepper.setAcceleration(ACCEL_STEPS_SEC2);
    accelStepper.setCurrentPosition(0);

    currentState = MotionState::IDLE;

    Serial.print(F("[STEPPER] Total steps per indexer revolution: "));
    Serial.println(TOTAL_STEPS_PER_REV);
}

// ============================================================================
// Internal: calculate ihold register value from milliamps
// ============================================================================
static uint8_t calcIhold() {
    // Scale hold current relative to run current (0-31 range)
    float ratio = (float)MOTOR_HOLD_CURRENT_MA / (float)MOTOR_CURRENT_MA;
    uint8_t ihold = (uint8_t)(ratio * 31.0f);
    if (ihold > 31) ihold = 31;
    return ihold;
}

// ============================================================================
// Enable / Disable
// ============================================================================
void stepper_enable(bool enabled) {
    digitalWrite(PIN_EN, enabled ? LOW : HIGH);  // Active LOW
    if (enabled) {
        Serial.println(F("[STEPPER] Motor ENABLED"));
    } else {
        Serial.println(F("[STEPPER] Motor DISABLED"));
        currentState = MotionState::IDLE;
    }
}

// ============================================================================
// Motion Commands
// ============================================================================
void stepper_move_steps(long steps) {
    if (currentState == MotionState::EMERGENCY_STOP) return;

    stepper_enable(true);
    accelStepper.move(steps);
    currentState = MotionState::MOVING;

    if (DEBUG_ENABLED) {
        Serial.print(F("[STEPPER] Moving "));
        Serial.print(steps);
        Serial.println(F(" steps"));
    }
}

void stepper_move_to(long position) {
    if (currentState == MotionState::EMERGENCY_STOP) return;

    stepper_enable(true);
    accelStepper.moveTo(position);
    currentState = MotionState::MOVING;

    if (DEBUG_ENABLED) {
        Serial.print(F("[STEPPER] Moving to position "));
        Serial.println(position);
    }
}

// ============================================================================
// Run Loop — MUST be called every loop() iteration
// ============================================================================
bool stepper_run() {
    if (currentState == MotionState::EMERGENCY_STOP) return false;

    bool moving = accelStepper.run();

    if (!moving && currentState == MotionState::MOVING) {
        currentState = MotionState::IDLE;
        if (DEBUG_ENABLED) {
            Serial.print(F("[STEPPER] Move complete. Position: "));
            Serial.println(accelStepper.currentPosition());
        }
    }

    return moving;
}

// ============================================================================
// Stop
// ============================================================================
void stepper_stop() {
    accelStepper.stop();  // Decelerate to stop
    // State will transition to IDLE via stepper_run() when decel completes
    Serial.println(F("[STEPPER] Stopping (decelerate)"));
}

void stepper_emergency_stop() {
    accelStepper.setCurrentPosition(accelStepper.currentPosition());
    // setCurrentPosition clears speed and target, instant stop
    currentState = MotionState::EMERGENCY_STOP;
    Serial.println(F("[STEPPER] EMERGENCY STOP"));
}

// ============================================================================
// Position
// ============================================================================
long stepper_get_position() {
    return accelStepper.currentPosition();
}

void stepper_set_position(long position) {
    accelStepper.setCurrentPosition(position);
    if (DEBUG_ENABLED) {
        Serial.print(F("[STEPPER] Position set to "));
        Serial.println(position);
    }
}

// ============================================================================
// State / Status
// ============================================================================
MotionState stepper_get_state() {
    return currentState;
}

bool stepper_is_moving() {
    return currentState == MotionState::MOVING || currentState == MotionState::JOGGING;
}

long stepper_distance_to_go() {
    return accelStepper.distanceToGo();
}

void stepper_set_max_speed(float speed) {
    accelStepper.setMaxSpeed(speed);
}

void stepper_set_acceleration(float accel) {
    accelStepper.setAcceleration(accel);
}
