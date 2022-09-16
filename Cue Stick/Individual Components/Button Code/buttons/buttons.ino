/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-button-toggle-led
 */

#define UP_PIN 19
#define DOWN_PIN 18
#define LEFT_PIN 17
#define RIGHT_PIN 16

struct Button{
  int pin_;
  int button_state_;       // the current state of button
  int last_button_state_;  // the previous state of button
};

Button buttonUp = {19, 0, 0};
Button buttonDown = {18, 0, 0};
Button buttonLeft = {17, 0, 0};
Button buttonRight = {16, 0, 0};

void setup() {
  Serial.begin(9600);                // initialize serial

  // Set pin mode
  pinMode(buttonUp.pin_, INPUT_PULLUP);
  pinMode(buttonDown.pin_, INPUT_PULLUP);
  pinMode(buttonLeft.pin_, INPUT_PULLUP);
  pinMode(buttonRight.pin_, INPUT_PULLUP);


  // Set button state
  buttonUp.button_state_ = digitalRead(buttonUp.pin_);
  buttonDown.button_state_ = digitalRead(buttonDown.pin_);
  buttonLeft.button_state_ = digitalRead(buttonLeft.pin_);
  buttonRight.button_state_ = digitalRead(buttonRight.pin_);
  
}

void loop() {
  buttonUp.last_button_state_ = buttonUp.button_state_;      // save the last state
  buttonUp.button_state_ = digitalRead(buttonUp.pin_); // read new state
  
  buttonDown.last_button_state_ = buttonDown.button_state_;      // save the last state
  buttonDown.button_state_ = digitalRead(buttonDown.pin_); // read new state

  buttonLeft.last_button_state_ = buttonLeft.button_state_;      // save the last state
  buttonLeft.button_state_ = digitalRead(buttonLeft.pin_); // read new state
  
  buttonRight.last_button_state_ = buttonRight.button_state_;      // save the last state
  buttonRight.button_state_ = digitalRead(buttonRight.pin_); // read new state

  if (buttonUp.last_button_state_ == HIGH && buttonUp.button_state_ == LOW) {
    Serial.println("Up is pressed");
  }
  if (buttonDown.last_button_state_ == HIGH && buttonDown.button_state_ == LOW) {
    Serial.println("Down is pressed");
  }
  if (buttonLeft.last_button_state_ == HIGH && buttonLeft.button_state_ == LOW) {
    Serial.println("Left is pressed");
  }
  if (buttonRight.last_button_state_ == HIGH && buttonRight.button_state_ == LOW) {
    Serial.println("Right is pressed");
  }
}
