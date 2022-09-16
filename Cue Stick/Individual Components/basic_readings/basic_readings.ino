// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <Math.h>

#define X 0
#define Y 1
#define Z 2

#define ACCELEROMETER_SENSITIVITY 16384
#define GYROSCOPE_SENSITIVITY 131
#define dt 0.01

Adafruit_MPU6050 mpu;
float calibrationOffsets[3];
float correctedAcceleration[3];
int calibrated;

float pitch = 0;
float roll = 0;
float gyrData[3];

double accRot[3];
double gyrRot[3];
double rotation[3];
double timeStep, time, timePrev;
int i = 0;

void calibrateMPU(Adafruit_MPU6050 mpu);
void complementaryFilter(short accData[3], short gyrData[3], float *pitch, float *roll);
void compFilter(float accData[3], float gyrData[3], double * rotation);

void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("Adafruit MPU6050 test!");

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }

  Serial.println("Calibrating IMU");
  calibrateMPU(mpu);
  i = 0;

  Serial.println("");
  delay(2000);

}

void loop() {

  // Get new sensor events with the readings
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  /*
  // Clear previous offsets
  for (int i = 0; i < 3; i++)
    calibrationOffsets[i] = 0;
  */
  
  // Correct acceleration readings
  correctedAcceleration[X] = a.acceleration.x - calibrationOffsets[X];
  correctedAcceleration[Y] = a.acceleration.y - calibrationOffsets[Y];
  correctedAcceleration[Z] = a.acceleration.z - calibrationOffsets[Z];

  // Read gyroscope values
  gyrData[X] = g.gyro.x;
  gyrData[Y] = g.gyro.y;
  gyrData[Z] = g.gyro.z;

  compFilter(correctedAcceleration, gyrData, rotation);

  // Print out the values
  Serial.print("Acceleration X: ");
  Serial.print(correctedAcceleration[X]);
  Serial.print(", Y: ");
  Serial.print(correctedAcceleration[Y]);
  Serial.print(", Z: ");
  Serial.print(correctedAcceleration[Z]);
  
  Serial.print(", Gyro X: ");
  Serial.print(g.gyro.x);
  Serial.print(", Y: ");
  Serial.print(g.gyro.y);
  Serial.print(", Z: ");
  Serial.print(g.gyro.z);

  roll = atan2(correctedAcceleration[Y], correctedAcceleration[Z]) * 180/PI;
  pitch = atan2(-correctedAcceleration[X], sqrt(correctedAcceleration[Y] * correctedAcceleration[Y] + correctedAcceleration[Z] * correctedAcceleration[Z])) * 180/PI;   

  Serial.print(", Roll: ");
  Serial.print(roll);
  Serial.print(", Pitch: ");
  Serial.print(pitch);

  Serial.print(", Rx: ");
  Serial.print(rotation[X]);
  Serial.print(", Ry: ");
  Serial.print(rotation[Y]);
  Serial.print(", Rz: ");
  Serial.print(rotation[Z]);

  Serial.println("");
  delay(50);
}

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
  else{
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