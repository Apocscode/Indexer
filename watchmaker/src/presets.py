"""
Watchmaker's Lathe Controller — Preset Library
Extensive presets for watchmaking, horology, and precision machining.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Preset:
    """A named indexing preset."""
    name: str
    category: str
    divisions: int
    description: str = ""


# ============================================================================
# Preset Database
# ============================================================================

PRESETS: List[Preset] = [
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ESCAPE WHEELS — the most critical wheel in any watch
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Swiss Lever Escape", "Escape Wheels", 15,
           "Standard Swiss lever escapement — 15 teeth"),
    Preset("English Lever Escape", "Escape Wheels", 15,
           "English lever escapement — 15 teeth"),
    Preset("Club-Tooth Escape", "Escape Wheels", 15,
           "Club-tooth lever escapement — 15 teeth"),
    Preset("Cylinder Escape", "Escape Wheels", 15,
           "Cylinder escapement — 15 teeth"),
    Preset("Duplex Escape", "Escape Wheels", 15,
           "Duplex escapement — 15 teeth"),
    Preset("Chronometer Detent", "Escape Wheels", 15,
           "Detent/chronometer escapement — 15 teeth"),
    Preset("Verge Escape (13T)", "Escape Wheels", 13,
           "Verge/crown wheel — 13 teeth (small)"),
    Preset("Verge Escape (15T)", "Escape Wheels", 15,
           "Verge escapement — 15 teeth"),
    Preset("Co-Axial Escape", "Escape Wheels", 15,
           "Omega Co-Axial escapement — 15 teeth"),
    Preset("Escape 20T", "Escape Wheels", 20,
           "20-tooth escape wheel (clock)"),
    Preset("Escape 21T", "Escape Wheels", 21,
           "21-tooth escape wheel"),
    Preset("Escape 30T (Clock)", "Escape Wheels", 30,
           "30-tooth escape wheel for clocks"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WATCH TRAIN WHEELS — standard ETA/generic movement wheels
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Great wheel / barrel
    Preset("Mainspring Barrel", "Train Wheels", 80,
           "Mainspring barrel teeth — 80T (common)"),
    Preset("Barrel 76T", "Train Wheels", 76,
           "Mainspring barrel — 76 teeth"),
    Preset("Barrel 84T", "Train Wheels", 84,
           "Mainspring barrel — 84 teeth"),
    Preset("Barrel 96T", "Train Wheels", 96,
           "Large barrel — 96 teeth (8-day)"),

    # Center wheel
    Preset("Center Wheel 75T", "Train Wheels", 75,
           "Center wheel — 75 teeth (ETA common)"),
    Preset("Center Wheel 80T", "Train Wheels", 80,
           "Center wheel — 80 teeth"),
    Preset("Center Wheel 64T", "Train Wheels", 64,
           "Center wheel — 64 teeth"),

    # Third wheel
    Preset("Third Wheel 75T", "Train Wheels", 75,
           "Third wheel — 75 teeth"),
    Preset("Third Wheel 70T", "Train Wheels", 70,
           "Third wheel — 70 teeth"),
    Preset("Third Wheel 80T", "Train Wheels", 80,
           "Third wheel — 80 teeth"),
    Preset("Third Wheel 60T", "Train Wheels", 60,
           "Third wheel — 60 teeth"),

    # Fourth wheel (seconds)
    Preset("Fourth Wheel 80T", "Train Wheels", 80,
           "Fourth (seconds) wheel — 80 teeth"),
    Preset("Fourth Wheel 75T", "Train Wheels", 75,
           "Fourth wheel — 75 teeth"),
    Preset("Fourth Wheel 70T", "Train Wheels", 70,
           "Fourth wheel — 70 teeth"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PINIONS — small driving gears
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Pinion 6-leaf", "Pinions", 6,
           "6-leaf pinion (escape pinion, 4th wheel pinion)"),
    Preset("Pinion 7-leaf", "Pinions", 7,
           "7-leaf pinion"),
    Preset("Pinion 8-leaf", "Pinions", 8,
           "8-leaf pinion (center pinion, 3rd wheel pinion)"),
    Preset("Pinion 9-leaf", "Pinions", 9,
           "9-leaf pinion"),
    Preset("Pinion 10-leaf", "Pinions", 10,
           "10-leaf pinion (center wheel pinion)"),
    Preset("Pinion 12-leaf", "Pinions", 12,
           "12-leaf pinion (winding)"),
    Preset("Pinion 14-leaf", "Pinions", 14,
           "14-leaf pinion"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # WINDING & KEYLESS — setting/winding mechanism
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Crown Wheel", "Winding", 30,
           "Crown wheel — 30 teeth"),
    Preset("Ratchet Wheel", "Winding", 30,
           "Ratchet wheel / click — 30 teeth"),
    Preset("Ratchet 40T", "Winding", 40,
           "Ratchet wheel — 40 teeth"),
    Preset("Setting Wheel 32T", "Winding", 32,
           "Setting wheel / minute wheel — 32 teeth"),
    Preset("Setting Wheel 36T", "Winding", 36,
           "Setting wheel — 36 teeth"),
    Preset("Sliding Pinion", "Winding", 14,
           "Sliding pinion — 14 teeth"),
    Preset("Castle Wheel", "Winding", 12,
           "Castle wheel — 12 teeth"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MOTION WORK — hour/minute display
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Minute Wheel 36T", "Motion Work", 36,
           "Minute wheel — 36 teeth"),
    Preset("Minute Wheel 30T", "Motion Work", 30,
           "Minute wheel — 30 teeth"),
    Preset("Hour Wheel 36T", "Motion Work", 36,
           "Hour wheel — 36 teeth"),
    Preset("Hour Wheel 32T", "Motion Work", 32,
           "Hour wheel — 32 teeth"),
    Preset("Hour Wheel 40T", "Motion Work", 40,
           "Hour wheel — 40 teeth"),
    Preset("Cannon Pinion 12T", "Motion Work", 12,
           "Cannon pinion — 12 teeth/leaves"),
    Preset("Cannon Pinion 10T", "Motion Work", 10,
           "Cannon pinion — 10 teeth"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CHRONOGRAPH
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Chrono Runner 60T", "Chronograph", 60,
           "Chronograph runner wheel — 60 teeth (seconds)"),
    Preset("Chrono Minute 30T", "Chronograph", 30,
           "Chronograph minute counter — 30 teeth"),
    Preset("Chrono Hour 12T", "Chronograph", 12,
           "Chronograph hour counter — 12 teeth"),
    Preset("Column Wheel 8T", "Chronograph", 8,
           "Column wheel — 8 columns"),
    Preset("Column Wheel 9T", "Chronograph", 9,
           "Column wheel — 9 columns"),
    Preset("Heart Cam", "Chronograph", 2,
           "Heart-shaped cam (2 lobes) for flyback reset"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CLOCK WHEELS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Clock Great Wheel 96T", "Clock", 96,
           "Clock great wheel — 96 teeth"),
    Preset("Clock Great Wheel 144T", "Clock", 144,
           "8-day clock great wheel — 144 teeth"),
    Preset("Clock Center 64T", "Clock", 64,
           "Clock center wheel — 64 teeth"),
    Preset("Clock Third 60T", "Clock", 60,
           "Clock third wheel — 60 teeth"),
    Preset("Clock Escape 30T", "Clock", 30,
           "Clock escape wheel — 30 teeth"),
    Preset("Clock Escape 40T", "Clock", 40,
           "Clock escape wheel — 40 teeth"),
    Preset("Clock Pinion 8T", "Clock", 8,
           "Clock pinion — 8 leaves"),
    Preset("Clock Pinion 12T", "Clock", 12,
           "Clock pinion — 12 leaves"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DIAL & DECORATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Hour Markers", "Dial", 12,
           "12 hour markers / indices"),
    Preset("Minute Markers", "Dial", 60,
           "60 minute markers / hash marks"),
    Preset("5-Min Markers", "Dial", 12,
           "5-minute markers (=hours)"),
    Preset("Roman Numerals", "Dial", 12,
           "12 positions for Roman numeral dial"),
    Preset("Guilloche 6-Arm", "Dial", 6,
           "6-arm engine turning / guilloche"),
    Preset("Guilloche 8-Arm", "Dial", 8,
           "8-arm engine turning pattern"),
    Preset("Guilloche 12-Arm", "Dial", 12,
           "12-arm engine turning pattern"),
    Preset("Guilloche 16-Arm", "Dial", 16,
           "16-arm engine turning pattern"),
    Preset("Snailing 5-Arm", "Dial", 5,
           "5-arm snailing pattern (mainplate)"),
    Preset("Geneva Stripes", "Dial", 1,
           "Linear côtes de Genève — single pass, jog for spacing"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STANDARD GEOMETRY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Half", "Geometry", 2, "180° — 2 divisions"),
    Preset("Triangle", "Geometry", 3, "120° — 3 divisions"),
    Preset("Square", "Geometry", 4, "90° — 4 divisions"),
    Preset("Pentagon", "Geometry", 5, "72° — 5 divisions"),
    Preset("Hexagon", "Geometry", 6, "60° — 6 divisions"),
    Preset("Octagon", "Geometry", 8, "45° — 8 divisions"),
    Preset("Decagon", "Geometry", 10, "36° — 10 divisions"),
    Preset("Dodecagon", "Geometry", 12, "30° — 12 divisions"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DEGREE INCREMENTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Every 90°", "Degrees", 4, "Quarter turns"),
    Preset("Every 60°", "Degrees", 6, "Sextant divisions"),
    Preset("Every 45°", "Degrees", 8, "Eighth turns"),
    Preset("Every 30°", "Degrees", 12, "Twelfth turns"),
    Preset("Every 15°", "Degrees", 24, "24 divisions"),
    Preset("Every 10°", "Degrees", 36, "36 divisions"),
    Preset("Every 5°", "Degrees", 72, "72 divisions"),
    Preset("Every 2°", "Degrees", 180, "180 divisions"),
    Preset("Every 1°", "Degrees", 360, "360 divisions"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # BOLT CIRCLES / SCREWS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("2-Screw", "Fasteners", 2, "2-screw pattern"),
    Preset("3-Screw", "Fasteners", 3, "3-screw pattern (case back)"),
    Preset("4-Screw", "Fasteners", 4, "4-screw pattern"),
    Preset("5-Screw (Caseback)", "Fasteners", 5, "5-screw watch case back"),
    Preset("6-Screw (Caseback)", "Fasteners", 6, "6-screw case back"),
    Preset("8-Screw", "Fasteners", 8, "8-screw pattern"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # GENERAL MACHINING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("2-Flute", "Flutes", 2, "180° — end mill, drill"),
    Preset("3-Flute", "Flutes", 3, "120° — end mill"),
    Preset("4-Flute", "Flutes", 4, "90° — end mill, tap"),
    Preset("6-Flute", "Flutes", 6, "60° — reamer"),
    Preset("Hex Flats", "Wrench", 6, "6 flats for hex head/nut"),
    Preset("Square Drive", "Wrench", 4, "4 flats for square drive"),
    Preset("12-Point", "Wrench", 12, "12-point socket pattern"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SPLINES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("4-Spline", "Splines", 4, "4-spline shaft"),
    Preset("6-Spline", "Splines", 6, "6-spline shaft"),
    Preset("8-Spline", "Splines", 8, "8-spline shaft"),
    Preset("12-Spline", "Splines", 12, "12-spline shaft"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # KNURLING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Preset("Coarse Knurl", "Knurl", 14, "14-tooth coarse diamond"),
    Preset("Medium Knurl", "Knurl", 21, "21-tooth medium diamond"),
    Preset("Fine Knurl", "Knurl", 33, "33-tooth fine diamond"),
    Preset("Crown Knurl", "Knurl", 24, "24-tooth crown (watch crown grip)"),
    Preset("Watch Crown Fine", "Knurl", 40, "40-tooth fine crown knurl"),
    Preset("Watch Crown X-Fine", "Knurl", 60, "60-tooth extra-fine crown"),
]


# ============================================================================
# Access Functions
# ============================================================================

def get_all() -> List[Preset]:
    """Return all presets."""
    return PRESETS


def get_count() -> int:
    return len(PRESETS)


def get(index: int) -> Preset:
    """Get preset by index (clamped)."""
    return PRESETS[max(0, min(index, len(PRESETS) - 1))]


def get_categories() -> List[str]:
    """Get sorted unique category names."""
    cats = sorted(set(p.category for p in PRESETS))
    return cats


def get_by_category(category: str) -> List[Preset]:
    """Get all presets in a given category."""
    return [p for p in PRESETS if p.category == category]


def find_by_divisions(n: int) -> Optional[Preset]:
    """Find the first preset matching a division count."""
    for p in PRESETS:
        if p.divisions == n:
            return p
    return None


def search(query: str) -> List[Preset]:
    """Search presets by name, category, or description (case-insensitive)."""
    q = query.lower()
    return [p for p in PRESETS
            if q in p.name.lower() or q in p.category.lower() or q in p.description.lower()]
