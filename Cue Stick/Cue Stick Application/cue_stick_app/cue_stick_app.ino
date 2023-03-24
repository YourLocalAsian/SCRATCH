// Cue Stick Application
#include <stdint.h>
#include "shot_fsm.h"

// * Global Variables 
int buttonHistoryArray[10];
int buttonHistoryIndex;
bool konamiCodeInput;
uint8_t operationMode;
enum opStates   {STANDBY_MODE, SHOT_MODE, BLIND_MODE, DEBUG_MODE, KONAMI_CODE};


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

    if (fsmState == SET_NON) {
        operationMode = SHOT_MODE;
        Serial.println("Normal Mode");
    } else if (fsmState == SET_BLD) {
        operationMode = BLIND_MODE;
        Serial.println("Blind Mode");
    }
    
    switch(operationMode) {
        case STANDBY_MODE: {// CCU hasn't configured yet
            if (checkButton(buttonA)) {
                Serial.println("Y");
                updateCharacteristic(buttonCharacteristic, A); // Send CCU yes
            } 
            if (checkButton(buttonB)) {
                Serial.println("N");
                updateCharacteristic(buttonCharacteristic, B); // Send CCU no
            }
            break;
        }
        
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
