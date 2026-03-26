// ============================================================================
// Display Module — Implementation
// SSD1306 128x64 OLED rendering
// ============================================================================

#include "display.h"
#include "config.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// --- OLED display instance ---
static Adafruit_SSD1306 oled(OLED_WIDTH, OLED_HEIGHT, &Wire, -1);

// --- Helper: draw centered text ---
static void drawCentered(int16_t y, const char* text, uint8_t textSize = 1) {
    oled.setTextSize(textSize);
    int16_t x1, y1;
    uint16_t w, h;
    oled.getTextBounds(text, 0, 0, &x1, &y1, &w, &h);
    oled.setCursor((OLED_WIDTH - w) / 2, y);
    oled.print(text);
}

// --- Helper: draw right-aligned text ---
static void drawRight(int16_t y, const char* text, uint8_t textSize = 1) {
    oled.setTextSize(textSize);
    int16_t x1, y1;
    uint16_t w, h;
    oled.getTextBounds(text, 0, 0, &x1, &y1, &w, &h);
    oled.setCursor(OLED_WIDTH - w - 2, y);
    oled.print(text);
}

// --- Helper: draw a horizontal divider line ---
static void drawDivider(int16_t y) {
    oled.drawFastHLine(0, y, OLED_WIDTH, SSD1306_WHITE);
}

// ============================================================================
// Init
// ============================================================================
void display_init() {
    Wire.begin(PIN_SDA, PIN_SCL);

    if (!oled.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS)) {
        Serial.println(F("[DISPLAY] SSD1306 init FAILED"));
        return;
    }

    oled.clearDisplay();
    oled.setTextColor(SSD1306_WHITE);
    oled.setTextWrap(false);
    oled.display();

    Serial.println(F("[DISPLAY] SSD1306 initialized OK"));
}

// ============================================================================
// Splash Screen
// ============================================================================
void display_splash() {
    oled.clearDisplay();

    drawCentered(4, "5C INDEX", 2);
    drawDivider(22);
    drawCentered(26, "CONTROLLER", 1);
    drawCentered(40, "HHIP 3900-1604", 1);

    char buf[32];
    snprintf(buf, sizeof(buf), "Ratio %d:%d  %duS",
             GEAR_RATIO_NUMERATOR, GEAR_RATIO_DENOMINATOR, MICROSTEPS);
    drawCentered(54, buf, 1);

    oled.display();
}

// ============================================================================
// Main Indexing View
// ============================================================================
void display_main(int currentDivision, int totalDivisions,
                  float degrees, bool isMoving) {
    oled.clearDisplay();

    // Top bar: mode label
    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.print(F("INDEX"));
    if (isMoving) {
        drawRight(0, "MOVING");
    }
    drawDivider(10);

    // Large division display:  "3 / 6"
    char buf[32];
    snprintf(buf, sizeof(buf), "%d/%d", currentDivision + 1, totalDivisions);
    drawCentered(14, buf, 2);

    // Degrees display
    drawDivider(32);
    char degBuf[16];
    dtostrf(degrees, 7, 3, degBuf);
    strcat(degBuf, "\xF8");  // degree symbol
    drawCentered(36, degBuf, 2);

    // Bottom bar: instructions
    drawDivider(54);
    oled.setTextSize(1);
    oled.setCursor(0, 56);
    oled.print(F("GO:Next  M:Mode  P:Pre"));

    oled.display();
}

// ============================================================================
// Division Edit Screen
// ============================================================================
void display_division_edit(int divisions, long stepsPerDiv,
                           float degreesPerDiv, bool isExact) {
    oled.clearDisplay();

    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.print(F("SET DIVISIONS"));
    drawDivider(10);

    // Large division number
    char buf[16];
    snprintf(buf, sizeof(buf), "%d", divisions);
    drawCentered(14, buf, 3);

    drawDivider(38);

    // Details
    oled.setTextSize(1);
    oled.setCursor(0, 41);
    char degBuf[16];
    dtostrf(degreesPerDiv, 7, 4, degBuf);
    oled.print(degBuf);
    oled.print(F("\xF8/div"));

    oled.setCursor(0, 51);
    oled.print(stepsPerDiv);
    oled.print(F(" stp/div"));

    // Exact indicator
    if (isExact) {
        drawRight(41, "EXACT");
    } else {
        drawRight(41, "BRES");  // Bresenham distribution
    }

    // Encoder instruction
    drawRight(51, "<ENC>");

    oled.display();
}

// ============================================================================
// Preset Selection Screen
// ============================================================================
void display_preset_select(const char* presetName, int divisions,
                           int index, int total) {
    oled.clearDisplay();

    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.print(F("PRESETS"));

    char idxBuf[12];
    snprintf(idxBuf, sizeof(idxBuf), "%d/%d", index + 1, total);
    drawRight(0, idxBuf);
    drawDivider(10);

    // Preset name
    drawCentered(16, presetName, 1);

    // Division count (large)
    char buf[16];
    snprintf(buf, sizeof(buf), "%d", divisions);
    drawCentered(28, buf, 3);

    // Degrees per division
    drawDivider(52);
    char degBuf[16];
    float deg = 360.0f / divisions;
    dtostrf(deg, 7, 3, degBuf);
    oled.setTextSize(1);
    oled.setCursor(0, 56);
    oled.print(degBuf);
    oled.print(F("\xF8/div"));

    drawRight(56, "GO:Sel");

    oled.display();
}

// ============================================================================
// Jog Mode
// ============================================================================
void display_jog(float degrees, float jogIncrement) {
    oled.clearDisplay();

    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.print(F("JOG MODE"));
    drawDivider(10);

    // Current position degrees (large)
    char degBuf[16];
    dtostrf(degrees, 7, 3, degBuf);
    strcat(degBuf, "\xF8");
    drawCentered(16, degBuf, 2);

    drawDivider(34);

    // Jog increment
    oled.setTextSize(1);
    oled.setCursor(0, 38);
    oled.print(F("Increment:"));
    char incBuf[12];
    dtostrf(jogIncrement, 5, 1, incBuf);
    strcat(incBuf, "\xF8");
    drawRight(38, incBuf);

    // Instructions
    drawDivider(54);
    oled.setCursor(0, 56);
    oled.print(F("ENC:Jog  SW:Inc  M:Bk"));

    oled.display();
}

// ============================================================================
// Status Overlay
// ============================================================================
void display_status(const char* message) {
    // Draw a centered box with the message
    int16_t x1, y1;
    uint16_t w, h;
    oled.setTextSize(2);
    oled.getTextBounds(message, 0, 0, &x1, &y1, &w, &h);

    int16_t bx = (OLED_WIDTH - w - 12) / 2;
    int16_t by = (OLED_HEIGHT - h - 8) / 2;

    oled.fillRect(bx, by, w + 12, h + 8, SSD1306_BLACK);
    oled.drawRect(bx, by, w + 12, h + 8, SSD1306_WHITE);
    oled.setCursor(bx + 6, by + 4);
    oled.print(message);

    oled.display();
}

// ============================================================================
// Error Display
// ============================================================================
void display_error(const char* message) {
    oled.clearDisplay();

    drawCentered(4, "ERROR", 2);
    drawDivider(22);
    oled.setTextSize(1);
    oled.setTextWrap(true);
    oled.setCursor(0, 28);
    oled.print(message);
    oled.setTextWrap(false);

    oled.display();
}

// ============================================================================
// Info / Calculation Detail Screen
// ============================================================================
void display_info(int divisions, long totalSteps, long stepsPerDiv,
                  float degreesPerDiv, float gearRatio, int microsteps) {
    oled.clearDisplay();

    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.print(F("CALC INFO"));
    drawDivider(10);

    char buf[32];

    oled.setCursor(0, 13);
    snprintf(buf, sizeof(buf), "Divs:  %d", divisions);
    oled.print(buf);

    oled.setCursor(0, 23);
    snprintf(buf, sizeof(buf), "Total: %ld stp/rev", totalSteps);
    oled.print(buf);

    oled.setCursor(0, 33);
    snprintf(buf, sizeof(buf), "Step:  %ld stp/div", stepsPerDiv);
    oled.print(buf);

    oled.setCursor(0, 43);
    char degBuf[12];
    dtostrf(degreesPerDiv, 7, 4, degBuf);
    snprintf(buf, sizeof(buf), "Angle: %s\xF8", degBuf);
    oled.print(buf);

    oled.setCursor(0, 53);
    char ratBuf[8];
    dtostrf(gearRatio, 4, 1, ratBuf);
    snprintf(buf, sizeof(buf), "Gear:%s  uS:%d", ratBuf, microsteps);
    oled.print(buf);

    oled.display();
}

// ============================================================================
// Utility
// ============================================================================
void display_clear() {
    oled.clearDisplay();
    oled.display();
}

void display_update() {
    oled.display();
}
