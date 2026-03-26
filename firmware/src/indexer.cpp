// ============================================================================
// Indexer — Division Math Engine Implementation
// Handles all division math, Bresenham error distribution, position tracking
// ============================================================================

#include "indexer.h"
#include "config.h"

// --- Internal state ---
static long     totalStepsPerRev = 0;
static int      numDivisions     = 1;
static long     baseSteps        = 0;     // Floor(totalSteps / divisions)
static long     remainder        = 0;     // totalSteps % divisions
static int      currentDivision  = 0;     // 0 = home, up to (numDivisions - 1)
static long     currentPosition  = 0;     // Absolute step position
static long     bresenhamError   = 0;     // Accumulated error for Bresenham

// ============================================================================
// Initialization
// ============================================================================
void indexer_init() {
    totalStepsPerRev = TOTAL_STEPS_PER_REV;
    numDivisions     = 1;
    baseSteps        = totalStepsPerRev;
    remainder        = 0;
    currentDivision  = 0;
    currentPosition  = 0;
    bresenhamError   = 0;

    Serial.print(F("[INDEXER] Initialized. Steps/rev = "));
    Serial.println(totalStepsPerRev);
    Serial.print(F("[INDEXER] Gear ratio = "));
    Serial.print(GEAR_RATIO_NUMERATOR);
    Serial.print(F(":"));
    Serial.println(GEAR_RATIO_DENOMINATOR);
}

// ============================================================================
// Calculate division parameters
// ============================================================================
DivisionResult indexer_calculate(int divisions) {
    DivisionResult result;
    result.divisions          = divisions;
    result.totalStepsPerRev   = totalStepsPerRev;
    result.degreesPerDivision = 360.0f / (float)divisions;

    if (divisions <= 0) {
        result.stepsPerDivision = 0;
        result.remainderSteps   = 0;
        result.exact            = false;
        return result;
    }

    result.stepsPerDivision = totalStepsPerRev / divisions;
    result.remainderSteps   = totalStepsPerRev % divisions;
    result.exact            = (result.remainderSteps == 0);

    return result;
}

// ============================================================================
// Set active division count
// ============================================================================
void indexer_set_divisions(int divisions) {
    if (divisions < 1) divisions = 1;
    if (divisions > 360) divisions = 360;  // Practical upper limit

    numDivisions    = divisions;
    baseSteps       = totalStepsPerRev / divisions;
    remainder       = totalStepsPerRev % divisions;
    currentDivision = 0;
    currentPosition = 0;
    bresenhamError  = 0;

    DivisionResult r = indexer_calculate(divisions);

    Serial.print(F("[INDEXER] Divisions: "));
    Serial.print(divisions);
    Serial.print(F("  Steps/div: "));
    Serial.print(r.stepsPerDivision);
    Serial.print(F("  Remainder: "));
    Serial.print(r.remainderSteps);
    Serial.print(F("  Degrees/div: "));
    Serial.print(r.degreesPerDivision, 4);
    Serial.print(F("  Exact: "));
    Serial.println(r.exact ? "YES" : "NO");
}

// ============================================================================
// Bresenham-style step distribution
// Distributes remainder steps evenly across divisions so that after a full
// revolution, the total is EXACTLY totalStepsPerRev.
//
// Example: 9600 steps / 7 divisions = 1371 base + 3 remainder
//   Divisions get: 1372, 1371, 1372, 1371, 1371, 1372, 1371 = 9600 exactly
// ============================================================================
long indexer_get_next_steps() {
    if (numDivisions <= 0) return 0;

    long steps = baseSteps;

    // Bresenham error accumulation
    bresenhamError += remainder;
    if (bresenhamError >= numDivisions) {
        bresenhamError -= numDivisions;
        steps += 1;  // This division gets one extra step
    }

    // Advance division counter (wrap around)
    currentDivision = (currentDivision + 1) % numDivisions;
    currentPosition += steps;

    // Wrap position within one revolution
    if (currentPosition >= totalStepsPerRev) {
        currentPosition -= totalStepsPerRev;
        bresenhamError = 0;  // Reset error at home
    }

    return steps;
}

long indexer_get_prev_steps() {
    if (numDivisions <= 0) return 0;

    // Go backward: we need to "undo" the Bresenham for the current position
    // Calculate what the step count WAS to get to current division
    // Then return the negative

    // Move division counter backward
    currentDivision--;
    if (currentDivision < 0) {
        currentDivision = numDivisions - 1;
    }

    // Recalculate Bresenham for this division index
    // We recompute from scratch to avoid backward-error issues
    long targetPosition = 0;
    long err = 0;
    for (int i = 0; i < currentDivision; i++) {
        targetPosition += baseSteps;
        err += remainder;
        if (err >= numDivisions) {
            err -= numDivisions;
            targetPosition += 1;
        }
    }

    long steps = currentPosition - targetPosition;
    currentPosition = targetPosition;
    bresenhamError = err;

    // Handle wrap-around
    if (currentPosition < 0) {
        currentPosition += totalStepsPerRev;
    }

    return -steps;  // Negative = move backward
}

// ============================================================================
// Position queries
// ============================================================================
int indexer_get_current_division() {
    return currentDivision;
}

int indexer_get_total_divisions() {
    return numDivisions;
}

float indexer_get_degrees() {
    return indexer_steps_to_degrees(currentPosition);
}

long indexer_get_position_steps() {
    return currentPosition;
}

// ============================================================================
// Home / zero
// ============================================================================
long indexer_steps_to_home() {
    long steps = -currentPosition;
    // Take the shorter path
    if (steps < -(totalStepsPerRev / 2)) {
        steps += totalStepsPerRev;
    }
    return steps;
}

void indexer_reset_home() {
    currentDivision = 0;
    currentPosition = 0;
    bresenhamError  = 0;
    Serial.println(F("[INDEXER] Home position reset"));
}

// ============================================================================
// Move to specific division
// ============================================================================
long indexer_steps_to_division(int divisionIndex) {
    if (divisionIndex < 0 || divisionIndex >= numDivisions) return 0;

    // Calculate absolute position of target division
    long targetPosition = 0;
    long err = 0;
    for (int i = 0; i < divisionIndex; i++) {
        targetPosition += baseSteps;
        err += remainder;
        if (err >= numDivisions) {
            err -= numDivisions;
            targetPosition += 1;
        }
    }

    long steps = targetPosition - currentPosition;

    // Take shorter path around the circle
    if (steps > totalStepsPerRev / 2) {
        steps -= totalStepsPerRev;
    } else if (steps < -(totalStepsPerRev / 2)) {
        steps += totalStepsPerRev;
    }

    // Update state
    currentDivision = divisionIndex;
    currentPosition = targetPosition;
    bresenhamError  = err;

    return steps;
}

// ============================================================================
// Unit conversions
// ============================================================================
long indexer_degrees_to_steps(float degrees) {
    return (long)((degrees / 360.0f) * (float)totalStepsPerRev + 0.5f);
}

float indexer_steps_to_degrees(long steps) {
    return ((float)steps / (float)totalStepsPerRev) * 360.0f;
}

long indexer_jog_steps(float jogDegrees) {
    return indexer_degrees_to_steps(jogDegrees);
}
