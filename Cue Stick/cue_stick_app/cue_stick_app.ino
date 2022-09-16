#include <stdint.h>
#include "IMU.h"

// definitions for operating modes
#define STANDBY_MODE 0
#define SHOT_MODE 1

// definitions for IMU
#define X 0
#define Y 1
#define Z 2
#define ACCELEROMETER_SENSITIVITY 16384
#define GYROSCOPE_SENSITIVITY 131
#define dt 0.01

// struct for button
struct Button
{
  const uint8_t PIN;
  bool pressed;
  bool held;
};

// instantiate buttons
Button buttonU = {1, false, false};
Button buttonD = {2, false, false};
Button buttonL = {3, false, false};
Button buttonR = {4, false, false};
Button buttonA = {5, false, false};
Button buttonB = {6, false, false};

void setup() {
  // Configure serial (console)
  Serial.begin(9600);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  // Setup Bluetooth connection to CCU

  // Configure IMU

  // Verify IMU connection

  // Calibrate IMU

  // Configure buttons
    // Set pin modes
    // Attach interrupt

  // Set stick to standby mode
//

}

void loop() {
  // if in standby mode
    // wait for button input
  //
}
