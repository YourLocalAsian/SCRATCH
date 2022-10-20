#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define BNO055_SAMPLERATE_DELAY_MS (100)
Adafruit_BNO055 bno = Adafruit_BNO055(-1, 0x28);

double calData[4];

void setup(void)
{
  Serial.begin(115200);
  Serial.println("Orientation Sensor Raw Data Test"); Serial.println("");

  /* Initialise the sensor */
  if(!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }

  delay(1000);

  /* Display the current temperature */
  int8_t temp = bno.getTemp();
  Serial.print("Current Temperature: ");
  Serial.print(temp);
  Serial.println(" C");
  Serial.println("");

  bno.setExtCrystalUse(true);

  
  Serial.println("Calibration status values: 0=uncalibrated, 3=fully calibrated");

  delay(5);
  zeroOut();
}

void loop(void)
{
  // Possible vector values can be:
  // - VECTOR_ACCELEROMETER - m/s^2
  // - VECTOR_MAGNETOMETER  - uT
  // - VECTOR_GYROSCOPE     - rad/s
  // - VECTOR_EULER         - degrees
  // - VECTOR_LINEARACCEL   - m/s^2
  // - VECTOR_GRAVITY       - m/s^2
  
  imu::Vector<3> acc = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  imu::Vector<3> grav = bno.getVector(Adafruit_BNO055::VECTOR_GRAVITY);
  
  imu::Quaternion quat = bno.getQuat();
  quat.normalize();
  imu::Vector<3> euler = quat.toEuler();

  double yy = quat.y() * quat.y(); // 2 Uses below
  double roll = atan2(2 * (quat.w() * quat.x() + quat.y() * quat.z()), 1 - 2*(quat.x() * quat.x() + yy));
  double pitch = asin(2 * quat.w() * quat.y() - quat.x() * quat.z());
  double yaw = atan2(2 * (quat.w() * quat.z() + quat.x() * quat.y()), 1 - 2*(yy+quat.z() * quat.z()));

  /* Display the floating point data */
  Serial.print("Acceleration: ");
  Serial.print(acc.x() - calData[0]);
  Serial.print(" Roll: ");
  Serial.print(-180/M_PI * euler.z(), 0);
  Serial.print(" Pitch: ");
  Serial.print(180/M_PI * euler.y(), 0);
  Serial.print(" Yaw: ");
  Serial.print(180/M_PI * euler.x(), 0);

  /*
  // Quaternion data
  imu::Quaternion quat = bno.getQuat();
  Serial.print("qW: ");
  Serial.print(quat.w(), 4);
  Serial.print(" qX: ");
  Serial.print(quat.x(), 4);
  Serial.print(" qY: ");
  Serial.print(quat.y(), 4);
  Serial.print(" qZ: ");
  Serial.print(quat.z(), 4);
  */
  Serial.println("\t\t");
  
  /*
  // Display calibration status for each sensor.
  uint8_t system, gyro, accel, mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);
  Serial.print("CALIBRATION: Sys=");
  Serial.print(system, DEC);
  Serial.print(" Gyro=");
  Serial.print(gyro, DEC);
  Serial.print(" Accel=");
  Serial.print(accel, DEC);
  Serial.print(" Mag=");
  Serial.println(mag, DEC);
  */

  delay(BNO055_SAMPLERATE_DELAY_MS);
}

void zeroOut()
{
  for (int i = 0; i < 4; i++)
    calData[i] = 0;
  
  for (int i = 0; i < 20; i++)
  {
    imu::Vector<3> acc = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    imu::Vector<3> grav = bno.getVector(Adafruit_BNO055::VECTOR_GRAVITY);
  
    imu::Quaternion quat = bno.getQuat();
    quat.normalize();
    imu::Vector<3> euler = quat.toEuler();
    

    calData[0] += acc.x();
    calData[1] += 180/M_PI * euler.z();
    Serial.printf("Roll add: %lf\n", calData[1]);
    calData[2] += 180/M_PI * euler.y();
    Serial.printf("Pitch add: %lf\n", calData[2]);
    calData[3] += 180/M_PI * euler.x();
    Serial.printf("Yaw add: %lf\n", calData[3]);
    delay(BNO055_SAMPLERATE_DELAY_MS);
  }

  for (int i = 0; i < 4; i++)
  {
    calData[i] /= 20;
    Serial.printf("Offset #%d: %lf\n", i, calData[i]);
  }
    
}
