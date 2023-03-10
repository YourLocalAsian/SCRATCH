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
    operationMode = *(operationCharacteristic->getData());
    
    switch(operationMode) {
        case STANDBY_MODE: {
            int numOfButtonsPressed = readAllButtons(); // wait for button input
            // * Printing happens in readAllButtons()
            storeButtonHistory(); // store button inputs for checking for input codes & notify is pressed
            checkForKonami();
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
        
        case KONAMI_CODE: {
            Serial.println("You typed the Konami code. You get 30 lives");
            fsmState = STANDBY_MODE;
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

void storeButtonHistory() {
    for (int index = 0; index < 6; index++) { // Iterate through pressedArray 
        if (pressedArray[index]) { // if button is pressed
            buttonHistoryArray[buttonHistoryIndex] = index; // Store button at current buttonHistoryIndex in buttonHistoryArray
            buttonHistoryIndex = (buttonHistoryIndex + 1) % 10; // buttonHistoryIndex index
            updateCharacteristic(buttonCharacteristic, index); // notify CCU of button press
        }
    }
}

void checkForKonami() { // check for Konami code in reverse
    bool possibleCode = true;
    int tempIndex = (buttonHistoryIndex + 1) % 10;
    
    if (buttonHistoryArray[tempIndex] == UP) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == UP && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == DOWN && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == DOWN && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == LEFT && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == RIGHT && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == LEFT && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == RIGHT && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == B && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    if (buttonHistoryArray[tempIndex] == A && possibleCode) {
        tempIndex = (tempIndex + 1) % 10;
    }
    
    if (possibleCode) fsmState = KONAMI_CODE;
}
