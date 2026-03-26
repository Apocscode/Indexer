// ============================================================================
// Presets Module — Implementation
// Common indexing patterns for machining, bolt circles, gears, etc.
// ============================================================================

#include "presets.h"

// ============================================================================
// Preset Table
// Organized by category for easy browsing
// ============================================================================
static const IndexPreset presetTable[] = {
    // --- Basic Geometry ---
    { "Half",               "Geometry", 2   },
    { "Triangle",           "Geometry", 3   },
    { "Square",             "Geometry", 4   },
    { "Pentagon",           "Geometry", 5   },
    { "Hexagon",            "Geometry", 6   },
    { "Octagon",            "Geometry", 8   },
    { "Decagon",            "Geometry", 10  },
    { "Dodecagon",          "Geometry", 12  },

    // --- Common Bolt Circles ---
    { "3-Bolt Circle",      "Bolts",    3   },
    { "4-Bolt Circle",      "Bolts",    4   },
    { "5-Bolt Circle",      "Bolts",    5   },
    { "6-Bolt Circle",      "Bolts",    6   },
    { "8-Bolt Circle",      "Bolts",    8   },
    { "10-Bolt Circle",     "Bolts",    10  },
    { "12-Bolt Circle",     "Bolts",    12  },

    // --- Flutes / Milling ---
    { "2-Flute",            "Flutes",   2   },
    { "3-Flute",            "Flutes",   3   },
    { "4-Flute",            "Flutes",   4   },
    { "5-Flute",            "Flutes",   5   },
    { "6-Flute",            "Flutes",   6   },
    { "7-Flute",            "Flutes",   7   },
    { "8-Flute",            "Flutes",   8   },

    // --- Gear Teeth (Common Tooth Counts) ---
    { "12-Tooth Gear",      "Gears",    12  },
    { "14-Tooth Gear",      "Gears",    14  },
    { "16-Tooth Gear",      "Gears",    16  },
    { "18-Tooth Gear",      "Gears",    18  },
    { "20-Tooth Gear",      "Gears",    20  },
    { "24-Tooth Gear",      "Gears",    24  },
    { "28-Tooth Gear",      "Gears",    28  },
    { "32-Tooth Gear",      "Gears",    32  },
    { "36-Tooth Gear",      "Gears",    36  },
    { "40-Tooth Gear",      "Gears",    40  },
    { "48-Tooth Gear",      "Gears",    48  },
    { "60-Tooth Gear",      "Gears",    60  },
    { "72-Tooth Gear",      "Gears",    72  },

    // --- Splines ---
    { "4-Spline",           "Splines",  4   },
    { "6-Spline",           "Splines",  6   },
    { "8-Spline",           "Splines",  8   },
    { "10-Spline",          "Splines",  10  },
    { "12-Spline",          "Splines",  12  },
    { "16-Spline",          "Splines",  16  },
    { "24-Spline",          "Splines",  24  },

    // --- Degree Increments ---
    { "Every 90\xF8",       "Degrees",  4   },
    { "Every 60\xF8",       "Degrees",  6   },
    { "Every 45\xF8",       "Degrees",  8   },
    { "Every 30\xF8",       "Degrees",  12  },
    { "Every 15\xF8",       "Degrees",  24  },
    { "Every 10\xF8",       "Degrees",  36  },
    { "Every 5\xF8",        "Degrees",  72  },
    { "Every 1\xF8",        "Degrees",  360 },

    // --- Knurling Patterns ---
    { "Coarse Knurl",       "Knurl",    14  },
    { "Medium Knurl",       "Knurl",    21  },
    { "Fine Knurl",         "Knurl",    33  },

    // --- Clock / Timing ---
    { "Clock Hours",        "Timing",   12  },
    { "Clock Minutes",      "Timing",   60  },

    // --- Wrenches / Flats ---
    { "Hex Flats",          "Wrench",   6   },
    { "Square Drive",       "Wrench",   4   },
    { "12-Point Socket",    "Wrench",   12  },
};

static const int PRESET_COUNT = sizeof(presetTable) / sizeof(presetTable[0]);

// ============================================================================
// API
// ============================================================================
int presets_get_count() {
    return PRESET_COUNT;
}

const IndexPreset& presets_get(int index) {
    if (index < 0) index = 0;
    if (index >= PRESET_COUNT) index = PRESET_COUNT - 1;
    return presetTable[index];
}

int presets_next(int currentIndex) {
    return (currentIndex + 1) % PRESET_COUNT;
}

int presets_prev(int currentIndex) {
    currentIndex--;
    if (currentIndex < 0) currentIndex = PRESET_COUNT - 1;
    return currentIndex;
}

int presets_find_by_divisions(int divisions) {
    for (int i = 0; i < PRESET_COUNT; i++) {
        if (presetTable[i].divisions == divisions) {
            return i;
        }
    }
    return -1;
}
