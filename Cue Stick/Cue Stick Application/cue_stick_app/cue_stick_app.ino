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
    } else if (fsmState == SET_STANDBY) {
        operationMode = STANDBY_MODE;
        Serial.println("Standby Mode");
    } else if (fsmState == 16) {
        ccuReady = true;
        //Serial.println("CCU READY");
        //Serial.println("CCU READY");
        //Serial.println("CCU READY");
        //Serial.println("CCU READY");
        //Serial.println("CCU READY");
        fsmState = READY;
    }
    
    switch(operationMode) {
        case STANDBY_MODE: {// CCU hasn't configured yet
            if (checkButton(buttonUp)) {
                Serial.println("User pressed Up");
                updateCharacteristic(buttonCharacteristic, UP); // Send CCU yes
            }
            if (checkButton(buttonDown)) {
                Serial.println("User pressed Down");
                updateCharacteristic(buttonCharacteristic, DOWN); // Send CCU yes
            }
            if (checkButton(buttonLeft)) {
                Serial.println("User pressed Left");
                updateCharacteristic(buttonCharacteristic, LEFT); // Send CCU yes
            }
            if (checkButton(buttonRight)) {
                Serial.println("User pressed Right");
                updateCharacteristic(buttonCharacteristic, RIGHT); // Send CCU yes
            }
            if (checkButton(buttonA)) {
                Serial.println("User pressed A");
                updateCharacteristic(buttonCharacteristic, A); // Send CCU yes
            } 
            if (checkButton(buttonB)) {
                Serial.println("User pressed B");
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
        
        default: {
            Serial.println("ERROR - IDK HOW YOU GOT HERE");
            operationMode = STANDBY_MODE;
            break;
        }
    }   
}
