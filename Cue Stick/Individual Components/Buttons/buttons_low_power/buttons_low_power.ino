#include <string>
#include "driver/rtc_io.h"

// Definitions for low-power modes
#define uS_TO_S_FACTOR 1000000ULL  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  5        /* Time ESP32 will go to sleep (in seconds) */
#define BUTTON_PIN_BITMASK 0xE007000

// Button pin definitions
#define UP_PIN 14
#define DOWN_PIN 12
#define LEFT_PIN 13
#define RIGHT_PIN 25
#define A_PIN 27
#define B_PIN 26

struct Button{
  const uint8_t pin_;
  const String name_;
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

// Declare function prototype
void ButtonUp_ISR();
void ButtonDown_ISR();
void ButtonLeft_ISR();
void ButtonRight_ISR();
void ButtonA_ISR();
void ButtonB_ISR();
void (* buttonISR[])() = {ButtonUp_ISR, ButtonDown_ISR, ButtonLeft_ISR, ButtonRight_ISR, ButtonA_ISR, ButtonB_ISR};

void print_wake_up();
void print_wakeup_reason();


void setup() {
  Serial.begin(9600);
  
  // Configure buttons
  for (int i = 0; i < 6; ++i)
  {
    pinMode(buttonArray[i].pin_, INPUT_PULLUP); // set pin mode
    attachInterrupt(buttonArray[i].pin_, buttonISR[i], FALLING);
  }

  esp_sleep_enable_ext1_wakeup(BUTTON_PIN_BITMASK,ESP_EXT1_WAKEUP_ANY_HIGH);
}

void loop() {
  print_wakeup_reason();
  print_wake_up();
  esp_sleep_enable_ext1_wakeup(BUTTON_PIN_BITMASK,ESP_EXT1_WAKEUP_ANY_HIGH);
  
  // Check if buttons are pressed
  uint8_t buttonsPressed = 0;

  for (int i = 0; i < 10; ++i)
  {
    if (buttonUp.pressed_) 
    {
          Serial.printf("%s ", buttonUp.name_);
          buttonsPressed++;
          buttonUp.pressed_= false;
    }
  
    if (buttonDown.pressed_) 
    {
          Serial.printf("%s ", buttonDown.name_);
          buttonsPressed++;
          buttonDown.pressed_= false;
    }
  
    if (buttonLeft.pressed_) 
    {
          Serial.printf("%s ", buttonLeft.name_);
          buttonsPressed++;
          buttonLeft.pressed_= false;
    }
  
    if (buttonRight.pressed_) 
    {
          Serial.printf("%s ", buttonRight.name_);
          buttonsPressed++;
          buttonRight.pressed_= false;
    }
  
    if (buttonA.pressed_) 
    {
          Serial.printf("%s ", buttonA.name_);
          buttonsPressed++;
          buttonA.pressed_= false;
    }
  
    if (buttonB.pressed_) 
    {
          Serial.printf("%s ", buttonB.name_);
          buttonsPressed++;
          buttonB.pressed_= false;
    }
    
    delay(10);
  }
  
  if (buttonsPressed > 0)
    Serial.printf("was pressed\n");

  // Reset number of buttons pressed
  buttonsPressed = 0;

  esp_deep_sleep_start();
  Serial.print("KENNY IS ALIVE");
}


// ISR Implementations
void ButtonUp_ISR()
{
  buttonUp.button_time_ = millis();
  if (buttonUp.button_time_ - buttonUp.last_button_time_ > 250)
  {
       buttonUp.pressed_ = true;
       buttonUp.last_button_time_ = buttonUp.button_time_;
  }
}

void ButtonDown_ISR()
{
  buttonDown.button_time_ = millis();
  if (buttonDown.button_time_ - buttonDown.last_button_time_ > 250)
  {
       buttonDown.pressed_ = true;
       buttonDown.last_button_time_ = buttonDown.button_time_;
  }
}

void ButtonLeft_ISR()
{
  buttonLeft.button_time_ = millis();
  if (buttonLeft.button_time_ - buttonLeft.last_button_time_ > 250)
  {
       buttonLeft.pressed_ = true;
       buttonLeft.last_button_time_ = buttonLeft.button_time_;
  }
}


void ButtonRight_ISR()
{
  buttonRight.button_time_ = millis();
  if (buttonRight.button_time_ - buttonRight.last_button_time_ > 250)
  {
       buttonRight.pressed_ = true;
       buttonRight.last_button_time_ = buttonRight.button_time_;
  }
}

void ButtonA_ISR()
{
  buttonA.button_time_ = millis();
  if (buttonA.button_time_ - buttonA.last_button_time_ > 250)
  {
       buttonA.pressed_ = true;
       buttonA.last_button_time_ = buttonA.button_time_;
  }
}

void ButtonB_ISR()
{
  buttonB.button_time_ = millis();
  if (buttonB.button_time_ - buttonB.last_button_time_ > 250)
  {
       buttonB.pressed_ = true;
       buttonB.last_button_time_ = buttonB.button_time_;
  }
}

void print_wake_up(){
  int GPIO_reason = esp_sleep_get_ext1_wakeup_status();
  Serial.print("GPIO that triggered the wake up: GPIO ");
  Serial.println((log(GPIO_reason))/log(2), 0);
}

void print_wakeup_reason(){
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason){
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n",wakeup_reason); break;
  }
}
