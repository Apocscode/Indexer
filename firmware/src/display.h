#pragma once
// ============================================================================
// Display Module — Header
// SSD1306 128x64 OLED UI for the indexer controller
// ============================================================================

#include <Arduino.h>

/// Display operating modes
enum class DisplayPage {
    SPLASH,
    MAIN,           // Normal indexing view
    DIVISION_EDIT,  // Editing number of divisions
    PRESET_SELECT,  // Browsing presets
    JOG,            // Jog mode
    SETTINGS,       // Settings menu
    INFO            // Shows calculation details
};

/// Initialize the OLED display
void display_init();

/// Show the splash screen
void display_splash();

/// Update the main indexing display
/// @param currentDivision  Current division index (0-based)
/// @param totalDivisions   Total number of divisions
/// @param degrees          Current position in degrees
/// @param isMoving         True if motor is in motion
void display_main(int currentDivision, int totalDivisions,
                  float degrees, bool isMoving);

/// Show the division editor
/// @param divisions   Currently selected division count
/// @param stepsPerDiv Steps per division for display
/// @param degreesPerDiv Degrees per division
/// @param isExact     True if divisions divide evenly
void display_division_edit(int divisions, long stepsPerDiv,
                           float degreesPerDiv, bool isExact);

/// Show a preset name and its division count
/// @param presetName  Name of the preset
/// @param divisions   Number of divisions
/// @param index       Current preset index
/// @param total       Total number of presets
void display_preset_select(const char* presetName, int divisions,
                           int index, int total);

/// Show jog mode display
/// @param degrees     Current position degrees
/// @param jogIncrement Current jog increment in degrees
void display_jog(float degrees, float jogIncrement);

/// Show a brief status message overlay
/// @param message  Status text (e.g., "MOVING...", "HOME", "DONE")
void display_status(const char* message);

/// Show an error message
void display_error(const char* message);

/// Show the info/calculation detail screen
void display_info(int divisions, long totalSteps, long stepsPerDiv,
                  float degreesPerDiv, float gearRatio, int microsteps);

/// Clear the display
void display_clear();

/// Force display refresh
void display_update();
