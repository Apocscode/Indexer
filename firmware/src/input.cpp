// ============================================================================
// Input Module — Implementation
// Interrupt-driven encoder + debounced buttons
// ============================================================================

#include "input.h"
#include "config.h"

// --- Encoder state (ISR-safe) ---
static volatile long encoderCount    = 0;
static volatile bool encoderChanged  = false;
static uint8_t       lastEncState    = 0;

// --- Button state ---
struct ButtonState {
    uint8_t  pin;
    bool     lastState;
    bool     pressed;
    bool     longFired;
    uint32_t lastDebounceTime;
    uint32_t pressStartTime;
};

static ButtonState buttons[4]; // Encoder SW, MODE, PRESET, GO
#define BTN_IDX_ENC    0
#define BTN_IDX_MODE   1
#define BTN_IDX_PRESET 2
#define BTN_IDX_GO     3

// --- Event queue (simple ring buffer) ---
#define EVENT_QUEUE_SIZE 16
static InputEvent eventQueue[EVENT_QUEUE_SIZE];
static volatile uint8_t eventHead = 0;
static volatile uint8_t eventTail = 0;

static void pushEvent(InputEvent evt) {
    uint8_t nextHead = (eventHead + 1) % EVENT_QUEUE_SIZE;
    if (nextHead != eventTail) {  // Don't overflow
        eventQueue[eventHead] = evt;
        eventHead = nextHead;
    }
}

static InputEvent popEvent() {
    if (eventTail == eventHead) return InputEvent::NONE;
    InputEvent evt = eventQueue[eventTail];
    eventTail = (eventTail + 1) % EVENT_QUEUE_SIZE;
    return evt;
}

// ============================================================================
// Encoder ISR
// ============================================================================
static void IRAM_ATTR encoderISR() {
    uint8_t a = digitalRead(PIN_ENC_CLK);
    uint8_t b = digitalRead(PIN_ENC_DT);
    uint8_t encState = (a << 1) | b;

    // State machine for quadrature decoding
    // Valid transitions: 00→01→11→10→00 (CW) or 00→10→11→01→00 (CCW)
    static const int8_t encTable[16] = {
         0, -1,  1,  0,
         1,  0,  0, -1,
        -1,  0,  0,  1,
         0,  1, -1,  0
    };

    uint8_t idx = (lastEncState << 2) | encState;
    int8_t delta = encTable[idx & 0x0F];
    lastEncState = encState;

    if (delta != 0) {
        encoderCount += delta;
        encoderChanged = true;
    }
}

// ============================================================================
// Init
// ============================================================================
void input_init() {
    // Configure encoder pins
    pinMode(PIN_ENC_CLK, INPUT_PULLUP);
    pinMode(PIN_ENC_DT, INPUT_PULLUP);
    pinMode(PIN_ENC_SW, INPUT_PULLUP);

    // Configure button pins
    pinMode(PIN_BTN_MODE, INPUT_PULLUP);
    pinMode(PIN_BTN_PRESET, INPUT_PULLUP);
    pinMode(PIN_BTN_GO, INPUT_PULLUP);

    // Initialize button states
    buttons[BTN_IDX_ENC]    = { PIN_ENC_SW,     true, false, false, 0, 0 };
    buttons[BTN_IDX_MODE]   = { PIN_BTN_MODE,   true, false, false, 0, 0 };
    buttons[BTN_IDX_PRESET] = { PIN_BTN_PRESET, true, false, false, 0, 0 };
    buttons[BTN_IDX_GO]     = { PIN_BTN_GO,     true, false, false, 0, 0 };

    // Init encoder state
    lastEncState = (digitalRead(PIN_ENC_CLK) << 1) | digitalRead(PIN_ENC_DT);
    encoderCount = 0;
    encoderChanged = false;

    // Attach encoder interrupts
    attachInterrupt(digitalPinToInterrupt(PIN_ENC_CLK), encoderISR, CHANGE);
    attachInterrupt(digitalPinToInterrupt(PIN_ENC_DT), encoderISR, CHANGE);

    // Clear event queue
    eventHead = 0;
    eventTail = 0;

    Serial.println(F("[INPUT] Initialized: encoder + 4 buttons"));
}

// ============================================================================
// Button debounce and press detection
// ============================================================================
static void processButton(uint8_t idx, InputEvent shortEvt, InputEvent longEvt) {
    ButtonState &btn = buttons[idx];
    bool reading = digitalRead(btn.pin);
    uint32_t now = millis();

    if (reading != btn.lastState) {
        btn.lastDebounceTime = now;
    }

    if ((now - btn.lastDebounceTime) > DEBOUNCE_MS) {
        // State is stable
        if (!reading && !btn.pressed) {
            // Button just pressed (active LOW)
            btn.pressed = true;
            btn.longFired = false;
            btn.pressStartTime = now;
        }
        else if (!reading && btn.pressed && !btn.longFired) {
            // Still held — check for long press
            if ((now - btn.pressStartTime) >= LONG_PRESS_MS) {
                pushEvent(longEvt);
                btn.longFired = true;
            }
        }
        else if (reading && btn.pressed) {
            // Button released
            if (!btn.longFired) {
                pushEvent(shortEvt);  // Short press
            }
            btn.pressed = false;
        }
    }

    btn.lastState = reading;
}

// ============================================================================
// Poll — call every loop()
// ============================================================================
InputEvent input_poll() {
    // Process encoder rotation
    if (encoderChanged) {
        noInterrupts();
        long count = encoderCount;
        encoderCount = 0;
        encoderChanged = false;
        interrupts();

        // Generate one event per detent
        while (count > 0) {
            pushEvent(InputEvent::ENC_CW);
            count--;
        }
        while (count < 0) {
            pushEvent(InputEvent::ENC_CCW);
            count++;
        }
    }

    // Process buttons
    processButton(BTN_IDX_ENC,    InputEvent::ENC_PRESS,     InputEvent::ENC_LONG_PRESS);
    processButton(BTN_IDX_MODE,   InputEvent::BTN_MODE,      InputEvent::BTN_MODE_LONG);
    processButton(BTN_IDX_PRESET, InputEvent::BTN_PRESET,    InputEvent::BTN_PRESET_LONG);
    processButton(BTN_IDX_GO,     InputEvent::BTN_GO,        InputEvent::BTN_GO_LONG);

    // Return next event from queue
    return popEvent();
}

// ============================================================================
// Utility
// ============================================================================
bool input_is_held(uint8_t pin) {
    return !digitalRead(pin);  // Active LOW
}

long input_get_encoder_raw() {
    noInterrupts();
    long val = encoderCount;
    interrupts();
    return val;
}

void input_reset_encoder() {
    noInterrupts();
    encoderCount = 0;
    interrupts();
}
