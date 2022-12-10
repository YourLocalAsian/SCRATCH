#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <typeinfo>
#include <Vector.h>

#include "buttons.h"

#define BNO055_SAMPLERATE_DELAY_MS 100
#define MIN_ACC -1000
#define MAX_ACC 1000
#define ACC_MARGIN 1
const int ELEMENT_COUNT_MAX = 30;
Adafruit_BNO055 bno = Adafruit_BNO055(-1, 0x28);

// Global storage variables
double storage_array[ELEMENT_COUNT_MAX];
Vector<double> accelerationValues(storage_array);
double stationaryValues[10];
double calData[4];
int stationaryIndex = 0;
double oldAcceleration;
double avgAcceleration;
double minima;
int mapped;

// Global status variables
int zeroCount;
bool zeroedOut = false;
bool isStationary;
bool shotReady;
double accelerationBase;
double globalMinima = 0;
bool shotAttempt;
int fmsState = 0;

// Print variables
bool printGraphForm;
bool printFmsState;
bool printStationary;
bool printShotReady;
bool printShotAttempt;
bool printVectorSize;
bool printMappedValue;
bool printAcceleration;
bool printRoll;
bool printPitch;
bool printYaw;

// Mapping arrays
const int mapArray[7] = {-1, -3, -5, -7, -9, -11, -13};
String ballSpeed[] = {"SOFT_TOUCH", "SLOW", "MEDIUM", 
                            "FAST", "POWER", "BREAK", "POWER_BREAK"};
String stateMap[] = {"NOT_READY", "READY", "WAITING", "TAKING_SHOT", "SHOT_TAKEN"};

// Supplementary functions
void checkStationary(double avgAcceleration);
double findGlobalMinima(Vector<double> accelerationValues);
int mapAcceleration(double acceleration);
void floodStationary(int val);
void zeroOut();
void configurePrint();
void basicPrint(imu::Vector<3> euler);
void graphPrint(imu::Vector<3> euler);

// Configures the simulation
void setup() {
    Serial.begin(115200);
    Serial.println("Cue Stick IMU Test\n");

    // Initialise the sensor
    if(!bno.begin()) {
        /* There was a problem detecting the BNO055 ... check your connections */
        Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
        while(1);
    }

    delay(1000);
    bno.setExtCrystalUse(true);
    Serial.println("Calibration status values: 0=uncalibrated, 3=fully calibrated");
    setupButtons();

    delay(5);
    zeroOut(); // Get baseline orientation of stick
    configurePrint();
    floodStationary(-100);
}

// Main functionality of simulation
void loop() {
    // Get accleration and orientation vectors
    imu::Vector<3> acc = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    imu::Vector<3> grav = bno.getVector(Adafruit_BNO055::VECTOR_GRAVITY);
  
    imu::Quaternion quat = bno.getQuat();
    quat.normalize();
    imu::Vector<3> euler = quat.toEuler();

    if (!zeroedOut) { // If not zeroedOut
        if (zeroCount < 20) { // If zeroCount < 20
            double roll = -180/M_PI * euler.z();
            double pitch = 180/M_PI * euler.y();
            double yaw = 180/M_PI * euler.x();
            Serial.printf("Roll = %lf\n", roll);
            if (!isnan(roll)) {
                calData[0] += acc.x();
                calData[1] += roll;
                calData[2] += pitch;
                calData[3] += yaw;
                Serial.printf("zeroCount = %d\n", zeroCount);
                zeroCount++;
            }
        }

        if (zeroCount == 20) { // If zeroCount == 20
            for (int i = 0; i < 4; i++) calData[i] /= 20; // Divide calData values by 20
            Serial.printf("Roll: %lf, Pitch: %lf, Yaw: %lf\n", calData[1], calData[2], calData[3]);
            zeroedOut = true; // Set zeroedOut to true
        }
    }
   
    if (zeroedOut) { // If zeroedOut
        avgAcceleration = ((acc[0] - calData[0]) + oldAcceleration) / 2; //  Smooth accleration value

        checkStationary(avgAcceleration); // Check if stick is stationary

        // FSM 
        if (!isStationary && !shotReady) { // State 0: Not stationary, not ready to take shot
            fmsState = 0;
        } else if (isStationary && !shotReady) { // State 1: Stationary, not ready to take shot -> ready to take shot
            accelerationBase = avgAcceleration;
            floodStationary(avgAcceleration);
            globalMinima = avgAcceleration;
            shotReady = true;
            fmsState = 1;
        } else if (isStationary && shotReady && accelerationValues.empty()) { // State 2: Stationary, ready to take shot, hasn't moved -> wait for shot
            fmsState = 2;
        } else if (!isStationary && shotReady) { // State 3: Not stationary, ready to take shot (taking shot) -> self
            //Serial.println("Taking a shot");
            double pushedValue = avgAcceleration - accelerationBase;
            accelerationValues.push_back(pushedValue);
            //Serial.printf("\tPushed %f\n", pushedValue);
            fmsState = 3;
        } else if (isStationary && shotReady && !accelerationValues.empty()) {  // State 4: Stationary, ready to take shot (done taking shot) -> reset
            for (int i = 0; i < 9; i++) accelerationValues.pop_back();
            floodStationary(avgAcceleration);
            shotAttempt = true;
            shotReady = false;
            fmsState = 4;
        }
    }

    // Print data
    if (printGraphForm)
        graphPrint(euler);
    else basicPrint(euler);
    
    if (shotAttempt) {
        minima = findGlobalMinima(accelerationValues);
        accelerationValues.clear();
        mapped = mapAcceleration(minima);
        if (printMappedValue) Serial.printf("Minima: %.3f, Mapped: %s\n\n", minima, ballSpeed[mapped]);
        shotAttempt = false;
    }

    oldAcceleration = avgAcceleration;

    delay(BNO055_SAMPLERATE_DELAY_MS);
}

// Finds the strongest deceleration
double findGlobalMinima(Vector<double> accelerationValues) {
    double minimum = MAX_ACC;
    for (double s : accelerationValues) {
        minimum = (s < minimum) ? s : minimum;
    }

    return minimum;
}

// Maps acceleration to meaningful value
int mapAcceleration(double acceleration) {
    int mapped = 0;
    for (int i = 0; i < 7; i++)
        if ((int) acceleration <= mapArray[i]) mapped = i;
    
    return mapped;
}

// Checks if cue stick is stationary
void checkStationary(double avgAcceleration) {
    stationaryValues[stationaryIndex] = avgAcceleration; // Store queue of 10 acceleration values
    double minAcc = MAX_ACC;
    double maxAcc = MIN_ACC;
    
    for (int i = 0; i < 10; i++){
        if (stationaryValues[i] < minAcc) minAcc = stationaryValues[i];
        if (stationaryValues[i] > maxAcc) maxAcc = stationaryValues[i];
    }

    isStationary = (maxAcc - minAcc <= ACC_MARGIN) ? true : false; // if the min and max differenitate less than 0.5, set stationary to true
    stationaryIndex = (stationaryIndex + 1) % 10; // wrap around
}

// Resets stationary value array
void floodStationary(int val) {
    for (int i = 0; i < 10; i++) stationaryValues[i] = val;    
}

void zeroOut() {
    for (int i = 0; i < 4; i++) 
        calData[i] = 0;

    
    
    for (int i = 0; i < 20; i++) {
        imu::Vector<3> acc = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
        imu::Vector<3> grav = bno.getVector(Adafruit_BNO055::VECTOR_GRAVITY);
    
        imu::Quaternion quat = bno.getQuat();
        quat.normalize();
        imu::Vector<3> euler = quat.toEuler();

        double roll = -180/M_PI * euler.z();
        if(isnan(roll)) 
            i--;
        else {
            calData[0] += acc.x();
            //Serial.printf("Acc add: %lf\n", calData[1]);
            calData[1] += 180/M_PI * euler.z();
            //Serial.printf("Roll add: %lf\n", calData[1]);
            calData[2] += 180/M_PI * euler.y();
            //Serial.printf("Pitch add: %lf\n", calData[2]);
            calData[3] += 180/M_PI * euler.x();
            //Serial.printf("Yaw add: %lf\n", calData[3]);
        }
        delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    for (int i = 0; i < 4; i++) {
        calData[i] /= 20;
        Serial.printf("Offset #%d: %lf\n", i, calData[i]);
    }

    zeroedOut = true;
    isStationary = false;
    shotReady = false;
    shotAttempt = false;
    oldAcceleration = calData[0];
}

// Configure which values are printed
void configurePrint() {
    uint8_t valuesConfigured = 0;

    // Print in graph form
    Serial.print("Print in graph form: ");
    while (valuesConfigured == 0) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printGraphForm = true;
            printFmsState = true;
            printAcceleration = true;
            printRoll = true;
            printPitch = true;
            printYaw = true;
            valuesConfigured = 8;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printGraphForm = false;
            valuesConfigured++;
        }
    }


    // Use default configuration
    if (valuesConfigured == 1) Serial.print("Use default (all printed): ");
    while (valuesConfigured == 1) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printFmsState = true;
            printStationary = true;
            printShotReady = true;
            printShotAttempt = true;
            printVectorSize = true;
            printMappedValue = true;
            printAcceleration = true;
            printRoll = true;
            printPitch = true;
            printYaw = true;
            valuesConfigured = 20;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            valuesConfigured++;
        }
    }

    // Set printFmsState
    if (valuesConfigured == 2) Serial.print("Print State?: ");
    while (valuesConfigured == 2) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printFmsState = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printFmsState = false;
            valuesConfigured++;
        }
    }
    
    // Set printStationary
    if (valuesConfigured == 3) Serial.print("Print isStationary?: ");
    while (valuesConfigured == 3) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printStationary = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printStationary = false;
            valuesConfigured++;
        }
    }
    
    // Set printShotReady
    if (valuesConfigured == 4) Serial.print("Print shotReady?: ");
    while (valuesConfigured == 4) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printShotReady = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printShotReady = false;
            valuesConfigured++;
        }
    }
    
    // Set printShotAttempt
    if (valuesConfigured == 5) Serial.print("Print FMS States?: ");
    while (valuesConfigured == 5) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printShotAttempt = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printShotAttempt = false;
            valuesConfigured++;
        }
    }
    
    // Set printVectorSize
    if (valuesConfigured == 6) Serial.print("Print vector size?: ");
    while (valuesConfigured == 6) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printVectorSize = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printVectorSize = false;
            valuesConfigured++;
        }    
    }

    // Set printMappedValue
    if (valuesConfigured == 7) Serial.print("Print mapped value?: ");
    while (valuesConfigured == 7) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printMappedValue = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printMappedValue = false;
            valuesConfigured++;
        }    
    }

    // Set printAcceleration
    if (valuesConfigured == 8) Serial.print("Print acceleration?: ");
    while (valuesConfigured == 8) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printAcceleration = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printAcceleration = false;
            valuesConfigured++;
        }
    }

    // Set printRoll
    if (valuesConfigured == 9) Serial.print("Print roll?: ");
    while (valuesConfigured == 9) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printRoll = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printRoll = false;
            valuesConfigured++;
        }    
    }

    // Set printPitch
    if (valuesConfigured == 10) Serial.print("Print pitch?: ");
    while (valuesConfigured == 10) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printPitch = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printPitch = false;
            valuesConfigured++;
        }   
    }

    // Set printYaw
    if (valuesConfigured == 11) Serial.print("Print yaw?: ");
    while (valuesConfigured == 11) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            printYaw = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            printYaw = false;
            valuesConfigured++;
        }    
    }

    Serial.println();
}

// Print for monitor
void basicPrint(imu::Vector<3> euler) {
    if (printFmsState) Serial.printf("State: %s\n", stateMap[fmsState]);
    if (printStationary) Serial.printf("Stationary: %s\n", isStationary ? "True" : "False");
    if (printShotReady) Serial.printf("Shot Ready: %s\n", shotReady ? "True" : "False");
    if (printShotAttempt) Serial.printf("Shot Attempt: %s\n", shotAttempt ? "True" : "False");
    if (printVectorSize) Serial.printf("Vector Size: %d\n", accelerationValues.size());
    if (printAcceleration) Serial.printf("Acceleration: %.3f\n", avgAcceleration);
    if (printRoll) Serial.printf("Roll: %.3f\n", -180/M_PI * (double) euler.z() - calData[1]);
    if (printPitch) Serial.printf("Pitch: %.3f\n", 180/M_PI * (double) euler.y() - calData[2]);
    if (printYaw) Serial.printf("Yaw: %.3f\n", -(180/M_PI * (double) euler.x() - calData[3]));
    Serial.println();
}

// Print for plotter
void graphPrint(imu::Vector<3> euler) {
    if (printFmsState) {
        Serial.print("State: ");
        Serial.print(fmsState);
    }
    if (printAcceleration) {
        Serial.print(" Acceleration: ");
        Serial.print(avgAcceleration, 3);
    }
    if (printRoll) {
        Serial.print(" Roll: ");
        Serial.print(-180/M_PI * (double) euler.z() - calData[1], 3);
    }
    if (printPitch) {
        Serial.print(" Pitch: ");
        Serial.print(180/M_PI * (double) euler.y() - calData[2], 3);
    }
    if (printYaw) {
        Serial.print(" Yaw: ");
        Serial.print(-(180/M_PI * (double) euler.x() - calData[3]), 3);
    }

    Serial.println("\t\t");
}
