// ============================================================================
// Index Controller — Main Firmware
// HHIP 5C Indexing Spin Jig (3900-1604) Stepper Controller
//
// ESP32 + TMC2209 + OLED + Rotary Encoder
// ============================================================================

#include <Arduino.h>
#include "config.h"
#include "stepper.h"
#include "indexer.h"
#include "display.h"
#include "input.h"
#include "presets.h"

// ============================================================================
// Application Modes
// ============================================================================
enum class AppMode {
    INDEX,          // Normal indexing — GO advances to next division
    DIVISION_EDIT,  // Editing the number of divisions via encoder
    PRESET_SELECT,  // Browsing presets
    JOG,            // Manual jog with encoder
    INFO            // Show calculation info
};

// --- Application State ---
static AppMode   appMode          = AppMode::INDEX;
static int       divisions        = 6;          // Default: hexagon
static int       presetIndex      = 0;          // Current preset cursor
static float     jogIncrement     = 1.0f;       // Jog step: 0.1°, 1°, 10°
static bool      needsRedraw      = true;       // Flag for display update
static uint32_t  lastActivityMs   = 0;

// Jog increment options
static const float jogIncrements[] = { 0.1f, 0.5f, 1.0f, 5.0f, 10.0f };
static const int   jogIncrementCount = sizeof(jogIncrements) / sizeof(jogIncrements[0]);
static int         jogIncrementIdx = 2;  // Start at 1.0°

// ============================================================================
// Forward declarations
// ============================================================================
static void handleIndexMode(InputEvent evt);
static void handleDivisionEditMode(InputEvent evt);
static void handlePresetSelectMode(InputEvent evt);
static void handleJogMode(InputEvent evt);
static void handleInfoMode(InputEvent evt);
static void updateDisplay();
static void applyDivisions(int newDivisions);
static void printStatus();

// ============================================================================
// SETUP
// ============================================================================
void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);  // Let serial settle

    Serial.println(F(""));
    Serial.println(F("========================================"));
    Serial.println(F("  5C INDEX CONTROLLER"));
    Serial.println(F("  HHIP 3900-1604 Spin Jig"));
    Serial.println(F("========================================"));
    Serial.println(F(""));

    // Initialize subsystems
    display_init();
    display_splash();

    stepper_init();
    indexer_init();
    input_init();

    // Apply default divisions
    applyDivisions(divisions);

    // Show splash for configured duration
    delay(SPLASH_DURATION_MS);

    // Enable motor
    stepper_enable(true);

    // Initial display
    needsRedraw = true;
    lastActivityMs = millis();

    printStatus();
    Serial.println(F("[MAIN] Ready. Waiting for input..."));
}

// ============================================================================
// MAIN LOOP
// ============================================================================
void loop() {
    // 1. Process stepper motion (must run every iteration for smooth accel)
    stepper_run();

    // 2. Poll input
    InputEvent evt = input_poll();

    if (evt != InputEvent::NONE) {
        lastActivityMs = millis();
        needsRedraw = true;

        // Global: GO long press = emergency stop from any mode
        if (evt == InputEvent::BTN_GO_LONG) {
            stepper_emergency_stop();
            display_status("E-STOP");
            delay(1000);
            // Reset e-stop state — user must re-home
            stepper_set_position(stepper_get_position());
            appMode = AppMode::INDEX;
            Serial.println(F("[MAIN] E-STOP cleared. Re-home recommended."));
            needsRedraw = true;
            return;
        }

        // Dispatch to active mode handler
        switch (appMode) {
            case AppMode::INDEX:          handleIndexMode(evt);          break;
            case AppMode::DIVISION_EDIT:  handleDivisionEditMode(evt);  break;
            case AppMode::PRESET_SELECT:  handlePresetSelectMode(evt);  break;
            case AppMode::JOG:            handleJogMode(evt);           break;
            case AppMode::INFO:           handleInfoMode(evt);          break;
        }
    }

    // 3. Update display if needed (and not currently moving — avoid flicker)
    if (needsRedraw && !stepper_is_moving()) {
        updateDisplay();
        needsRedraw = false;
    }

    // 4. When motion completes, refresh display
    static bool wasMoving = false;
    bool isMoving = stepper_is_moving();
    if (wasMoving && !isMoving) {
        needsRedraw = true;
    }
    wasMoving = isMoving;
}

// ============================================================================
// INDEX MODE — Normal indexing operation
// ============================================================================
static void handleIndexMode(InputEvent evt) {
    switch (evt) {
        case InputEvent::BTN_GO: {
            // Advance to next division
            if (!stepper_is_moving()) {
                long steps = indexer_get_next_steps();
                stepper_move_steps(steps);
                display_status("MOVE");

                Serial.print(F("[INDEX] -> Division "));
                Serial.print(indexer_get_current_division() + 1);
                Serial.print(F("/"));
                Serial.print(indexer_get_total_divisions());
                Serial.print(F("  Steps: "));
                Serial.print(steps);
                Serial.print(F("  Deg: "));
                Serial.println(indexer_get_degrees(), 3);
            }
            break;
        }

        case InputEvent::ENC_CW: {
            // Next division (same as GO)
            if (!stepper_is_moving()) {
                long steps = indexer_get_next_steps();
                stepper_move_steps(steps);
            }
            break;
        }

        case InputEvent::ENC_CCW: {
            // Previous division
            if (!stepper_is_moving()) {
                long steps = indexer_get_prev_steps();
                stepper_move_steps(steps);
            }
            break;
        }

        case InputEvent::ENC_PRESS: {
            // Go to division edit mode
            appMode = AppMode::DIVISION_EDIT;
            Serial.println(F("[MAIN] Mode -> DIVISION EDIT"));
            break;
        }

        case InputEvent::ENC_LONG_PRESS: {
            // Return to home
            if (!stepper_is_moving()) {
                long steps = indexer_steps_to_home();
                if (steps != 0) {
                    stepper_move_steps(steps);
                    display_status("HOME");
                    Serial.println(F("[INDEX] Returning to HOME"));
                } else {
                    display_status("AT HOME");
                }
                indexer_reset_home();
                stepper_set_position(0);
            }
            break;
        }

        case InputEvent::BTN_MODE: {
            // Cycle through modes: INDEX -> JOG -> INFO -> INDEX
            appMode = AppMode::JOG;
            Serial.println(F("[MAIN] Mode -> JOG"));
            break;
        }

        case InputEvent::BTN_MODE_LONG: {
            // Show info screen
            appMode = AppMode::INFO;
            Serial.println(F("[MAIN] Mode -> INFO"));
            break;
        }

        case InputEvent::BTN_PRESET: {
            // Open preset browser
            appMode = AppMode::PRESET_SELECT;
            Serial.println(F("[MAIN] Mode -> PRESET SELECT"));
            break;
        }

        default:
            break;
    }
}

// ============================================================================
// DIVISION EDIT MODE — Change division count with encoder
// ============================================================================
static void handleDivisionEditMode(InputEvent evt) {
    switch (evt) {
        case InputEvent::ENC_CW:
            divisions++;
            if (divisions > 360) divisions = 360;
            needsRedraw = true;
            break;

        case InputEvent::ENC_CCW:
            divisions--;
            if (divisions < 1) divisions = 1;
            needsRedraw = true;
            break;

        case InputEvent::ENC_PRESS:
        case InputEvent::BTN_GO: {
            // Confirm selection and go back to INDEX mode
            applyDivisions(divisions);
            appMode = AppMode::INDEX;
            display_status("SET");
            delay(500);
            Serial.print(F("[MAIN] Divisions set to "));
            Serial.println(divisions);
            break;
        }

        case InputEvent::BTN_MODE: {
            // Cancel, go back to INDEX
            appMode = AppMode::INDEX;
            Serial.println(F("[MAIN] Division edit cancelled"));
            break;
        }

        default:
            break;
    }
}

// ============================================================================
// PRESET SELECT MODE — Browse and select presets
// ============================================================================
static void handlePresetSelectMode(InputEvent evt) {
    switch (evt) {
        case InputEvent::ENC_CW:
        case InputEvent::BTN_PRESET:
            presetIndex = presets_next(presetIndex);
            needsRedraw = true;
            break;

        case InputEvent::ENC_CCW:
            presetIndex = presets_prev(presetIndex);
            needsRedraw = true;
            break;

        case InputEvent::ENC_PRESS:
        case InputEvent::BTN_GO: {
            // Apply selected preset
            const IndexPreset& preset = presets_get(presetIndex);
            divisions = preset.divisions;
            applyDivisions(divisions);
            appMode = AppMode::INDEX;

            Serial.print(F("[PRESET] Selected: "));
            Serial.print(preset.name);
            Serial.print(F(" ("));
            Serial.print(preset.divisions);
            Serial.println(F(" divisions)"));

            display_status("LOADED");
            delay(500);
            break;
        }

        case InputEvent::BTN_MODE: {
            // Cancel, go back
            appMode = AppMode::INDEX;
            break;
        }

        default:
            break;
    }
}

// ============================================================================
// JOG MODE — Manual positioning with encoder
// ============================================================================
static void handleJogMode(InputEvent evt) {
    switch (evt) {
        case InputEvent::ENC_CW: {
            // Jog clockwise
            if (!stepper_is_moving()) {
                long steps = indexer_jog_steps(jogIncrement);
                stepper_move_steps(steps);
            }
            break;
        }

        case InputEvent::ENC_CCW: {
            // Jog counter-clockwise
            if (!stepper_is_moving()) {
                long steps = indexer_jog_steps(jogIncrement);
                stepper_move_steps(-steps);
            }
            break;
        }

        case InputEvent::ENC_PRESS: {
            // Cycle jog increment
            jogIncrementIdx = (jogIncrementIdx + 1) % jogIncrementCount;
            jogIncrement = jogIncrements[jogIncrementIdx];
            Serial.print(F("[JOG] Increment: "));
            Serial.print(jogIncrement, 1);
            Serial.println(F("°"));
            needsRedraw = true;
            break;
        }

        case InputEvent::ENC_LONG_PRESS: {
            // Set current position as home
            stepper_set_position(0);
            indexer_reset_home();
            display_status("ZEROED");
            delay(500);
            Serial.println(F("[JOG] Position zeroed"));
            break;
        }

        case InputEvent::BTN_MODE: {
            // Back to INDEX mode
            appMode = AppMode::INDEX;
            Serial.println(F("[MAIN] Mode -> INDEX"));
            break;
        }

        case InputEvent::BTN_GO: {
            // In jog mode, GO returns to home
            if (!stepper_is_moving()) {
                long steps = -stepper_get_position();
                if (steps != 0) {
                    stepper_move_steps(steps);
                    display_status("HOME");
                }
            }
            break;
        }

        default:
            break;
    }
}

// ============================================================================
// INFO MODE — Display calculation details
// ============================================================================
static void handleInfoMode(InputEvent evt) {
    switch (evt) {
        case InputEvent::BTN_MODE:
        case InputEvent::ENC_PRESS:
        case InputEvent::BTN_GO:
            appMode = AppMode::INDEX;
            Serial.println(F("[MAIN] Mode -> INDEX"));
            break;
        default:
            break;
    }
}

// ============================================================================
// Display refresh
// ============================================================================
static void updateDisplay() {
    switch (appMode) {
        case AppMode::INDEX:
            display_main(
                indexer_get_current_division(),
                indexer_get_total_divisions(),
                indexer_get_degrees(),
                stepper_is_moving()
            );
            break;

        case AppMode::DIVISION_EDIT: {
            DivisionResult r = indexer_calculate(divisions);
            display_division_edit(
                divisions,
                r.stepsPerDivision,
                r.degreesPerDivision,
                r.exact
            );
            break;
        }

        case AppMode::PRESET_SELECT: {
            const IndexPreset& preset = presets_get(presetIndex);
            display_preset_select(
                preset.name,
                preset.divisions,
                presetIndex,
                presets_get_count()
            );
            break;
        }

        case AppMode::JOG:
            display_jog(
                indexer_steps_to_degrees(stepper_get_position()),
                jogIncrement
            );
            break;

        case AppMode::INFO: {
            DivisionResult r = indexer_calculate(divisions);
            display_info(
                divisions,
                r.totalStepsPerRev,
                r.stepsPerDivision,
                r.degreesPerDivision,
                GEAR_RATIO,
                MICROSTEPS
            );
            break;
        }
    }
}

// ============================================================================
// Apply new division setting
// ============================================================================
static void applyDivisions(int newDivisions) {
    divisions = newDivisions;
    indexer_set_divisions(divisions);
    stepper_set_position(0);  // Reset motor position reference
}

// ============================================================================
// Serial status dump
// ============================================================================
static void printStatus() {
    Serial.println(F(""));
    Serial.println(F("--- Configuration ---"));
    Serial.print(F("  Motor steps/rev:  ")); Serial.println(MOTOR_STEPS_PER_REV);
    Serial.print(F("  Microsteps:       ")); Serial.println(MICROSTEPS);
    Serial.print(F("  Gear ratio:       ")); Serial.print(GEAR_RATIO_NUMERATOR);
    Serial.print(F(":")); Serial.println(GEAR_RATIO_DENOMINATOR);
    Serial.print(F("  Total steps/rev:  ")); Serial.println(TOTAL_STEPS_PER_REV);
    Serial.print(F("  Motor current:    ")); Serial.print(MOTOR_CURRENT_MA);
    Serial.println(F(" mA"));
    Serial.print(F("  Max speed:        ")); Serial.print(MAX_SPEED_STEPS_SEC);
    Serial.println(F(" steps/sec"));
    Serial.print(F("  Acceleration:     ")); Serial.print(ACCEL_STEPS_SEC2);
    Serial.println(F(" steps/sec²"));
    Serial.print(F("  Divisions:        ")); Serial.println(divisions);

    DivisionResult r = indexer_calculate(divisions);
    Serial.print(F("  Steps/division:   ")); Serial.println(r.stepsPerDivision);
    Serial.print(F("  Degrees/division: ")); Serial.println(r.degreesPerDivision, 4);
    Serial.print(F("  Exact division:   ")); Serial.println(r.exact ? "YES" : "NO");
    Serial.print(F("  Presets loaded:   ")); Serial.println(presets_get_count());
    Serial.println(F("---------------------"));
    Serial.println(F(""));
}
