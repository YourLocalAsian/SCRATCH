#define UP_PIN 32
#define DOWN_PIN 16
#define LEFT_PIN 33
#define RIGHT_PIN 19
#define A_PIN 17
#define B_PIN 18
#define BOOT 0
#define LASER 23

#define UP 0
#define DOWN 1
#define LEFT 2
#define RIGHT 3
#define A 4
#define B 5

struct Button{
    const uint8_t pin_;
    const char * name_;
    bool pressed_;
    uint64_t button_time_;
    uint64_t last_button_time_;
};

// Instantiate buttons
Button buttonUp = {UP_PIN, "Up", false, 0, 0};
Button buttonDown = {DOWN_PIN, "Down", false, 0, 0};
Button buttonLeft = {LEFT_PIN, "Left", false, 0, 0};
Button buttonRight = {RIGHT_PIN, "Right", false, 0, 0};
Button buttonA = {A_PIN, "A", false, 0, 0};
Button buttonB = {B_PIN, "B", false, 0, 0};
Button buttonArray[] = {buttonUp, buttonDown, buttonLeft, buttonRight, buttonA, buttonB};
bool pressedArray[6];
uint8_t buttonsPressed = 0;

// Declare function prototype
void ButtonUp_ISR();
void ButtonDown_ISR();
void ButtonLeft_ISR();
void ButtonRight_ISR();
void ButtonA_ISR();
void ButtonB_ISR();
void (* buttonISR[])() = {ButtonUp_ISR, ButtonDown_ISR, ButtonLeft_ISR, ButtonRight_ISR, ButtonA_ISR, ButtonB_ISR};
bool checkButton(Button &button);

// Configure buttons
void setupButtons() {
    for (int i = 0; i < 6; ++i) {
        pinMode(buttonArray[i].pin_, INPUT_PULLUP); // set pin mode
        attachInterrupt(buttonArray[i].pin_, buttonISR[i], FALLING);
    }
}

void loopButton() {
    // Check if buttons are pressed
    uint8_t buttonsPressed = 0;

    for (int i = 0; i < 20; ++i) {
        if (buttonUp.pressed_) {
          Serial.printf("%s ", buttonUp.name_);
          buttonsPressed++;
          buttonUp.pressed_= false;
        }
  
        if (buttonDown.pressed_) {
            Serial.printf("%s ", buttonDown.name_);
            buttonsPressed++;
            buttonDown.pressed_= false;
        }
  
        if (buttonLeft.pressed_) {
            Serial.printf("%s ", buttonLeft.name_);
            buttonsPressed++;
            buttonLeft.pressed_= false;
        }
  
        if (buttonRight.pressed_) {
            Serial.printf("%s ", buttonRight.name_);
            buttonsPressed++;
            buttonRight.pressed_= false;
        }
  
        if (buttonA.pressed_) {
            Serial.printf("%s ", buttonA.name_);
            buttonsPressed++;
            buttonA.pressed_= false;
        }
  
        if (buttonB.pressed_) {
            Serial.printf("%s ", buttonB.name_);
            buttonsPressed++;
            buttonB.pressed_= false;
        }
    
        delay(10);
    }
  
    if (buttonsPressed > 0) Serial.printf("was pressed\n");

    // Reset number of buttons pressed
    buttonsPressed = 0;
}

int readAllButtons() {
    // Check if buttons are pressed
    uint8_t buttonsPressed = 0;

    for (int i = 0; i < 20; ++i) { // * loop is to detect "simultaneous" presses
        if (buttonUp.pressed_) {
            Serial.printf("%s ", buttonUp.name_);
            buttonsPressed++;
            buttonUp.pressed_= false;
            pressedArray[0] = true;
        }
  
        if (buttonDown.pressed_) {
            Serial.printf("%s ", buttonDown.name_);
            buttonsPressed++;
            buttonDown.pressed_= false;
            pressedArray[1] = true;
        }
  
        if (buttonLeft.pressed_) {
            Serial.printf("%s ", buttonLeft.name_);
            buttonsPressed++;
            buttonLeft.pressed_= false;
            pressedArray[2] = true;
        }
  
        if (buttonRight.pressed_) {
            Serial.printf("%s ", buttonRight.name_);
            buttonsPressed++;
            buttonRight.pressed_= false;
            pressedArray[3] = true;
        }
  
        if (buttonA.pressed_) {
            Serial.printf("%s ", buttonA.name_);
            buttonsPressed++;
            buttonA.pressed_= false;
            pressedArray[4] = true;
        }
  
        if (buttonB.pressed_) {
            Serial.printf("%s ", buttonB.name_);
            buttonsPressed++;
            buttonB.pressed_= false;
            pressedArray[5] = true;
        }
    
        delay(10);
    }

    if (buttonsPressed > 0) Serial.printf("was pressed\n");

    return buttonsPressed;
}

// ISR Implementations
void ButtonUp_ISR() {
    buttonUp.button_time_ = millis();
    if (buttonUp.button_time_ - buttonUp.last_button_time_ > 250) {
        buttonUp.pressed_ = true;
        buttonUp.last_button_time_ = buttonUp.button_time_;
    }
}

void ButtonDown_ISR() {
    buttonDown.button_time_ = millis();
    if (buttonDown.button_time_ - buttonDown.last_button_time_ > 250) {
        buttonDown.pressed_ = true;
        buttonDown.last_button_time_ = buttonDown.button_time_;
    }
}

void ButtonLeft_ISR() {
    buttonLeft.button_time_ = millis();
    if (buttonLeft.button_time_ - buttonLeft.last_button_time_ > 250) {
        buttonLeft.pressed_ = true;
        buttonLeft.last_button_time_ = buttonLeft.button_time_;
    }
}

void ButtonRight_ISR() {
    buttonRight.button_time_ = millis();
    if (buttonRight.button_time_ - buttonRight.last_button_time_ > 250) {
        buttonRight.pressed_ = true;
        buttonRight.last_button_time_ = buttonRight.button_time_;
    }
}

void ButtonA_ISR() {
    buttonA.button_time_ = millis();
    if (buttonA.button_time_ - buttonA.last_button_time_ > 250) {
        buttonA.pressed_ = true;
        buttonA.last_button_time_ = buttonA.button_time_;
    }
}

void ButtonB_ISR() {
    buttonB.button_time_ = millis();
    if (buttonB.button_time_ - buttonB.last_button_time_ > 250) {
        buttonB.pressed_ = true;
        buttonB.last_button_time_ = buttonB.button_time_;
    }
}

bool checkButton(Button &button) {
    bool ret = false;
    if (button.pressed_) {
        ret = true;
        button.pressed_= false;
        delay(100);
    }
    
    
    return ret;
}
