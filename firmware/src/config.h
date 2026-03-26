#pragma once
// ============================================================================
// Index Controller — Configuration
// HHIP 5C Indexing Spin Jig (3900-1604) Stepper Controller
// ============================================================================

// --- Motor & Driver ---
#define MOTOR_STEPS_PER_REV   200       // 1.8° per full step (standard NEMA 23)
#define MICROSTEPS            16        // TMC2209 microstepping (1, 2, 4, 8, 16, 32, 64, 128, 256)
#define MOTOR_CURRENT_MA      1200      // RMS current in milliamps
#define MOTOR_HOLD_CURRENT_MA 600       // Hold current (reduced to save power/heat)
#define INVERT_DIRECTION      false     // Set true if motor spins wrong way

// --- Gear Ratio (Timing Belt Pulleys) ---
// Ratio = NUMERATOR / DENOMINATOR = driven (indexer) / drive (motor)
// Example: 60T indexer / 20T motor = 3:1 (motor turns 3x per indexer rev)
#define GEAR_RATIO_NUMERATOR    60
#define GEAR_RATIO_DENOMINATOR  20

// --- Derived Constants (do not edit) ---
#define GEAR_RATIO            ((float)GEAR_RATIO_NUMERATOR / (float)GEAR_RATIO_DENOMINATOR)
#define TOTAL_STEPS_PER_REV   ((long)MOTOR_STEPS_PER_REV * MICROSTEPS * GEAR_RATIO_NUMERATOR / GEAR_RATIO_DENOMINATOR)

// --- Motion ---
#define MAX_SPEED_STEPS_SEC   4000      // Maximum stepping speed (steps/sec)
#define ACCEL_STEPS_SEC2      2000      // Acceleration (steps/sec²)
#define JOG_SPEED_STEPS_SEC   800       // Jog mode speed

// --- GPIO Pins: TMC2209 ---
#define PIN_STEP              16
#define PIN_DIR               17
#define PIN_EN                18
#define PIN_UART              19        // TMC2209 PDN_UART (single-wire)

// --- GPIO Pins: OLED Display (I2C) ---
#define PIN_SDA               21
#define PIN_SCL               22
#define OLED_ADDRESS          0x3C      // Try 0x3D if display doesn't work
#define OLED_WIDTH            128
#define OLED_HEIGHT           64

// --- GPIO Pins: Rotary Encoder ---
#define PIN_ENC_CLK           32
#define PIN_ENC_DT            33
#define PIN_ENC_SW            25

// --- GPIO Pins: Buttons ---
#define PIN_BTN_MODE          26
#define PIN_BTN_PRESET        27
#define PIN_BTN_GO            14

// --- Button Debounce ---
#define DEBOUNCE_MS           50        // Milliseconds for button debounce
#define LONG_PRESS_MS         1000      // Milliseconds for long-press detection
#define ENCODER_DEBOUNCE_MS   2         // Encoder rotary debounce

// --- Serial Debug ---
#define SERIAL_BAUD           115200
#define DEBUG_ENABLED         true

// --- OLED UI ---
#define SCREEN_TIMEOUT_MS     0         // 0 = never timeout (always on)
#define SPLASH_DURATION_MS    2000      // Splash screen display time
