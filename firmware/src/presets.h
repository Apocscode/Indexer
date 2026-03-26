#pragma once
// ============================================================================
// Presets Module — Header
// Common indexing division presets for machining operations
// ============================================================================

#include <Arduino.h>

/// A named preset with a division count and category
struct IndexPreset {
    const char* name;       // Display name
    const char* category;   // Category group
    int         divisions;  // Number of equal divisions
};

/// Get the total number of presets
int presets_get_count();

/// Get a preset by index (0-based)
const IndexPreset& presets_get(int index);

/// Get the next preset index (wraps around)
int presets_next(int currentIndex);

/// Get the previous preset index (wraps around)
int presets_prev(int currentIndex);

/// Search presets by division count — returns index or -1
int presets_find_by_divisions(int divisions);
