// Cue Stick Application

#include <stdint.h>
#include "shot_fms.h"

#define STANDBY_MODE 0
#define SHOT_MODE 1
#define DEBUG_MODE 2
#define KONAMI_CODE 87

// * Global Variables 
int cueStickState;
int buttonHistoryArray[10];
int buttonHistoryIndex;
bool konamiCodeInput;

// Main Functions
void connectToCCU(); // TODO
void storeButtonHistory();
void checkForKonami();

void setup() {
    // Configure serial (console)
    Serial.begin(115200);

    // Configure cue stick hardware
    setupHardware(); // * call modified version of ported_simulation's setup

     // Setup Bluetooth connection to CCU
    connectToCCU(); // TODO: figure out with Mena

    // Set stick to standby mode
    cueStickState = STANDBY_MODE;
}

void loop() {
    switch(cueStickState) {
        case STANDBY_MODE: {
            int numOfButtonsPressed = readAllButtons(); // wait for button input
            // * Printing happens in readAllButtons()
            storeButtonHistory(); // store button inputs for checking for input codes
            checkForKonami();
        } 
        
        case SHOT_MODE: {
            fmsLoop();
        } 
        
        case KONAMI_CODE: {
            Serial.println("You typed the Konami code. You get 30 lives");
            cueStickState = STANDBY_MODE;
        }

        default: {

        }
    }   
}

// TODO: Figure out how to connect cue stick to CCU
void connectToCCU() { 

}

void storeButtonHistory() {
    for (int index = 0; index < 6; index++) { // Iterate through pressedArray 
        if (pressedArray[index]) { // if button is pressed
            buttonHistoryArray[buttonHistoryIndex] = index; // Store button at current buttonHistoryIndex in buttonHistoryArray
            buttonHistoryIndex = (buttonHistoryIndex + 1) % 10; // buttonHistoryIndex index
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
    
    if (possibleCode) cueStickState = KONAMI_CODE;
}
