#pragma once
// ============================================================================
// Indexer — Division Math Engine Header
// Calculates step counts for any division, tracks position in degrees
// ============================================================================

#include <Arduino.h>

/// Represents the result of a division calculation
struct DivisionResult {
    int      divisions;           // Number of equal divisions requested
    long     stepsPerDivision;    // Base steps per division (integer part)
    long     remainderSteps;      // Extra steps to distribute (Bresenham)
    float    degreesPerDivision;  // Exact angle per division
    long     totalStepsPerRev;    // Total steps for full revolution
    bool     exact;               // True if division is perfectly even
};

/// Initialize the indexer math engine
void indexer_init();

/// Calculate the step distribution for N equal divisions
DivisionResult indexer_calculate(int divisions);

/// Set the number of divisions and prepare for indexing
void indexer_set_divisions(int divisions);

/// Get the number of steps to move to the NEXT division position
/// Uses Bresenham error accumulation so all positions are exact over a full rev
long indexer_get_next_steps();

/// Get the number of steps to move to the PREVIOUS division position
long indexer_get_prev_steps();

/// Get the current division index (0-based, 0 = home)
int indexer_get_current_division();

/// Get total number of divisions
int indexer_get_total_divisions();

/// Get current position in degrees (0.000 – 359.999)
float indexer_get_degrees();

/// Get current position in steps (absolute)
long indexer_get_position_steps();

/// Return to home (position 0)
long indexer_steps_to_home();

/// Reset position to home (define current as 0)
void indexer_reset_home();

/// Move to a specific division index (0-based)
long indexer_steps_to_division(int divisionIndex);

/// Convert degrees to steps
long indexer_degrees_to_steps(float degrees);

/// Convert steps to degrees
float indexer_steps_to_degrees(long steps);

/// Get the jog step count for a given increment (0.1°, 1°, 10°)
long indexer_jog_steps(float jogDegrees);
