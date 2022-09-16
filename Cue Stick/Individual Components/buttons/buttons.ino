// Code for testing button inputs
#include <stdint.h>

// struct for button
struct Button
{
  const uint8_t PIN_;
  bool pressed_;
  uint8_t secondsHeld_;
  uint64_t buttonTime_;
  uint64_t lastButtonTime_;
};

// instantiate buttons
Button ButtonUp = {1, false, 0 , 0, 0};
Button ButtonDown = {2, false, 0, 0, 0};
Button ButtonLeft = {3, false, 0, 0, 0};
Button ButtonRight = {4, false, 0, 0, 0};
Button ButtonA = {5, false, 0, 0, 0};
Button ButtonB = {6, false, 0, 0, 0};

void setup(void)
{
  // initialize buttons as inputs
  pinMode(ButtonUp.PIN_, INPUT_PULLUP);
  pinMode(ButtonDown.PIN_, INPUT_PULLUP);
  pinMode(ButtonLeft.PIN_, INPUT_PULLUP);
  pinMode(ButtonRight.PIN_, INPUT_PULLUP);
  pinMode(ButtonA.PIN_, INPUT_PULLUP);
  pinMode(ButtonB.PIN_, INPUT_PULLUP);

  // attach interrupt to button
  attachInterrupt(ButtonUp.PIN_, InterruptButtonUp, RISING);

  Serial.begin(9600);
}

void loop()
{
}

void InterruptButtonUp()
{
  ButtonUp.buttonTime_ = millis();
      
  // debounce
  if (ButtonUp.buttonTime_ - buttonUp.lastButtonTime_ > 250)
  {
    Serial.print("UP\n");
    buttonUp.lastButtonTime_ = ButtonUp.buttonTime_;
  }
}
