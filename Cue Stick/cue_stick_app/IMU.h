// Header file for reading from the IMU

#ifndef IMU_h
#define IMU_h

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <Math.h>

#define X 0
#define Y 1
#define Z 2

#define ACCELEROMETER_SENSITIVITY 16384
#define GYROSCOPE_SENSITIVITY 131
#define dt 0.0

Adafruit_MPU6050 mpu;
float calibrationOffsets[3];
float correctedAcceleration[3];
uint32_t calibrated;

float pitch = 0;
float roll = 0;
float gyrData[3];

double accRot[3];
double gyrRot[3];
double rotation[3];
double timeStep, time, timePrev;
uint32_t i = 0;

void calibrateMPU(Adafruit_MPU6050 mpu);
void complementaryFilter(short accData[3], short gyrData[3], float *pitch, float *roll);
void compFilter(float accData[3], float gyrData[3], double * rotation);

#endif // IMU_h