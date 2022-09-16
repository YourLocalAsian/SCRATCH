// Implementation of IMU functions
#include "IMU.h"

void calibrateMPU(Adafruit_MPU6050 mpu) {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Clear previous offsets
  for (int i = 0; i < 3; i++)
    calibrationOffsets[i] = 0;

  // Take 100 stationary samples of acceleration
  for (int i = 0; i < 100; i++) {
    calibrationOffsets[X] += a.acceleration.x;
    calibrationOffsets[Y] += a.acceleration.y;
    calibrationOffsets[Z] += a.acceleration.z;
    delay(10);
  }
  
  // Take the average of readings for later use
  for (int i = 0; i < 3; i++)
    calibrationOffsets[i] /= 100;

  // Fix Z-Axis
  calibrationOffsets[Z] = calibrationOffsets[Z] - 9.81;

  delay(500);
  Serial.println("IMU calibrated");
  delay(5000);
}

void complementaryFilter(short accData[3], short gyrData[3], float *pitch, float *roll)
{
    float pitchAcc, rollAcc;               
 
    // Integrate the gyroscope data -> int(angularSpeed) = angle
    *pitch += ((float)gyrData[0] / GYROSCOPE_SENSITIVITY) * dt; // Angle around the X-axis
    *roll -= ((float)gyrData[1] / GYROSCOPE_SENSITIVITY) * dt;    // Angle around the Y-axis
 
    // Compensate for drift with accelerometer data if !bullshit
    // Sensitivity = -2 to 2 G at 16Bit -> 2G = 32768 && 0.5G = 8192
    int forceMagnitudeApprox = abs(accData[0]) + abs(accData[1]) + abs(accData[2]);
    if (forceMagnitudeApprox > 8192 && forceMagnitudeApprox < 32768)
    {
	// Turning around the X axis results in a vector on the Y-axis
        pitchAcc = atan2f((float)accData[1], (float)accData[2]) * 180 / M_PI;
        *pitch = *pitch * 0.98 + pitchAcc * 0.02;
 
	// Turning around the Y axis results in a vector on the X-axis
        rollAcc = atan2f((float)accData[0], (float)accData[2]) * 180 / M_PI;
        *roll = *roll * 0.98 + rollAcc * 0.02;
    }
} 

void compFilter(float accData[3], float gyrData[3], double * rotation) 
{
  // Create array for scaling
  double gyroScaled[3];

  // Set up time for integration
  timePrev = time;
  time = millis();
  timeStep = (time - timePrev) / 1000; // time-step in s

  // apply gyro scale from datasheet
  gyroScaled[X] = gyrData[X] / GYROSCOPE_SENSITIVITY;   
  gyroScaled[Y] = gyrData[Y] / GYROSCOPE_SENSITIVITY;
  gyroScaled[Z] = gyrData[Z] / GYROSCOPE_SENSITIVITY;   

  // calculate accelerometer angles
  accRot[X] = (180/PI) * atan(accRot[X] / sqrt(pow(accRot[Y], 2) + pow(accRot[Z], 2))); 
  accRot[Y] = (180/PI) * atan(accRot[Y] / sqrt(pow(accRot[X], 2) + pow(accRot[Z], 2)));
  accRot[Z] = (180/PI) * atan(sqrt(pow(accRot[Y], 2) + pow(accRot[X], 2)) / accRot[Z]);

  // Set initial values equal to accel values
  if (i == 1) {
    gyrRot[X] = accRot[X];
    gyrRot[Y] = accRot[Y];
    gyrRot[Z] = accRot[Z];
  }
  // Integrate to find the gyro angle
  else {
    gyrRot[X] = gyrRot[X] + (timeStep * gyrRot[X]);
    gyrRot[Y] = gyrRot[Y] + (timeStep * gyrRot[Y]);
    gyrRot[Z] = gyrRot[Z] + (timeStep * gyrRot[Z]);
  }  

  // apply filter
  rotation[X] = (0.96 * accRot[X]) + (0.04 * gyrRot[X]);
  rotation[Y] = (0.96 * accRot[Y]) + (0.04 * gyrRot[Y]);
  rotation[Z] = (0.96 * accRot[Z]) + (0.04 * gyrRot[Z]);
  
  i++;
}