#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <typeinfo>

#define BNO055_SAMPLERATE_DELAY_MS (100)
Adafruit_BNO055 bno = Adafruit_BNO055(-1, 0x28);

double calData[4];
uint8_t zeroedOut;

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
  zeroedOut = 0;
  //formatPrint(0,1,-1,2);
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

  if (zeroedOut < 20)
  {
    double roll = -180/M_PI * euler.z();
    double pitch = 180/M_PI * euler.y();
    double yaw = 180/M_PI * euler.x();
    Serial.printf("Roll = %lf\n", roll);
    if (!isnan(roll))
    {
      calData[0] += acc.x();
      calData[1] += roll;
      calData[2] += pitch;
      calData[3] += yaw;
      Serial.printf("zeroedOut = %d\n", zeroedOut);
      zeroedOut++;
    }
  }
  else if (zeroedOut == 20)
  {
    calData[0] /= 20;
    calData[1] /= 20;
    calData[2] /= 20;
    calData[3] /= 20;
    Serial.printf("Roll: %lf, Pitch: %lf, Yaw: %lf\n", calData[1], calData[2], calData[3]);
    zeroedOut++;
  }
  else
  {
     /* Display the floating point data */
    Serial.print("Acceleration: ");
    Serial.print(-(acc.x() - calData[0]));
    Serial.print(" Roll: ");
    Serial.print(-180/M_PI * (double) euler.z() - calData[1], 0);
    Serial.print(" Pitch: ");
    Serial.print(180/M_PI * (double) euler.y() - calData[2], 0);
    Serial.print(" Yaw: ");
    Serial.print(-(180/M_PI * (double) euler.x() - calData[3]), 0);
    Serial.println("\t\t");
  }

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
    Serial.printf("Acc add: %lf\n", calData[1]);
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

void formatPrint(double acceleration, double roll, double pitch, double yaw)
{
  // Print orientation
    // Convert doubles to integer
    int rollInteger = (int) roll;
    int pitchInteger = (int) pitch;
    int yawInteger = (int) yaw;

    uint32_t output1 = 0x1 << 31;
    output1 = output1 | (rollInteger & 0x1FF) << 21; // store roll
    output1 = output1 | (pitchInteger & 0x1FF) << 12; // store pitch
    output1 = output1 | (yawInteger & 0x1FF) << 3; // store yaw
    output1 = output1 | 0x1;

    Serial.printf("Output: %32b", output1);
    
  // Print acceleration data
}
