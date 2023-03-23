// Cue Stick Application
#include <stdint.h>
#include "shot_fsm.h"

// * Global Variables 
int buttonHistoryArray[10];
int buttonHistoryIndex;
bool konamiCodeInput;
uint8_t operationMode;
enum opStates   {SHOT_MODE, BLIND_MODE, DEBUG_MODE, KONAMI_CODE};


// Main Functions
void connectToCCU(); // TODO
void storeButtonHistory();
void checkForKonami();

void setup() {
    // Configure serial (console)
    Serial.begin(115200);

    // Configure cue stick hardware
    setupHardware(); // * call modified version of ported_simulation's setup

    // Set stick to NOT_READY, STANDBY_MODE
    fsmState = NOT_READY;
    operationMode = STANDBY_MODE;
}

void loop() {
    // Check if CCU updated characteristics
    fsmState = *(fsmCharacteristic->getData());

    if (fsmState == SET_NON)
        operationMode = SHOT_MODE;
    else if (fsmState == SET_BLD)
        operationMode = BLIND_MODE;
    
    switch(operationMode) {
        case SHOT_MODE: {
            fsmLoop();
            break;
        }

        case BLIND_MODE: {
            blindFsmLoop();
            break;
        }
        
        case DEBUG_MODE: {
            Serial.println("TBD");
            break;
        }

        default: {
            Serial.println("IDK HOW YOU GOT HERE");
            fsmState = DEBUG_MODE;
            break;
        }
    }   
}
