#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <typeinfo>
#include <Vector.h>

#include "buttons.h"
#include "BLE_server.h"

#define BNO055_SAMPLERATE_DELAY_MS 100
#define MIN_ACCELERATION -1000
#define MAX_ACCELERATION 1000
#define ACC_MARGIN 1

const int ELEMENT_COUNT_MAX = 30;
Adafruit_BNO055 bno = Adafruit_BNO055(-1, 0x28);

// Global storage variables
double storage_array[ELEMENT_COUNT_MAX];
Vector<double> accelerationValues(storage_array);
double stationaryValues[20];
double calibrationData[4];
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

// Operation mode variables
bool speedCheckMode;
bool isRunning = true;

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
String stateMap[] = {"NOT_READY", "READY", "WAITING", "TAKING_SHOT", "SHOT_TAKEN", "PAUSED"};

// Supplementary functions
void checkStationary(double avgAcceleration);
double findGlobalMinima(Vector<double> accelerationValues);
int mapAcceleration(double acceleration);
void floodStationary();
void floodStationary(int floodValue);
void zeroOut();
void configurePrint();
void basicPrint(imu::Vector<3> eulerVector);
void graphPrint(imu::Vector<3> eulerVector);

void initBNO() {
    if(!bno.begin()) {
        /* There was a problem detecting the BNO055 ... check your connections */
        Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
        while(1);
    }
}

// Configures the simulation
void setup() {
    Serial.begin(115200);
    Serial.println("Cue Stick IMU Test\n");
    
    // Initialise the sensor
    initBNO(); 
    delay(1000);
    bno.setExtCrystalUse(true);
    Serial.println("Calibration status values: 0=uncalibrated, 3=fully calibrated");

    // Setup Laser
    pinMode(LASER, OUTPUT);
    digitalWrite(LASER, HIGH);

    // Initialize BLE connection
    setupBLE(); 
    //* Block operation until connection is detected
    while (!deviceConnected) {
        Serial.println("No connection detected");
        digitalWrite(LASER, !digitalRead(LASER));
        delay(250);
    }
    digitalWrite(LASER, HIGH);
    
    // Setup Button Inputs
    setupButtons();
    delay(5);
    
    // Setup Orientation Measurements
    zeroOut(); // Get baseline orientation of stick
    configureOperation();
    configurePrint();
    floodStationary(-100);   
}

// Main functionality of simulation
void loop() {
    // * Check if BLE connection is on
    while (!deviceConnected) {
        Serial.println("No connection detected");
        digitalWrite(LASER, !digitalRead(LASER));
        delay(250);
    }

    digitalWrite(LASER, HIGH);
    
    // * Check if loop is paused
    while (!isRunning) {
        Serial.println("Program is paused");
        
        if (checkButton(buttonA)) {
            isRunning = true;
            fmsState = 0;
            delay(3000); // Add additional 3s wait
            break;
        }
        
        delay(2000);
    }
    
    //* Get accleration and orientation vectors
    imu::Vector<3> accelerationVector = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    imu::Quaternion quaternionVector = bno.getQuat();
    quaternionVector.normalize();
    imu::Vector<3> eulerVector = quaternionVector.toEuler();

    if (!zeroedOut) { // If not zeroedOut
        if (zeroCount < 20) { // If zeroCount < 20
            double roll = -180/M_PI * eulerVector.z();
            double pitch = 180/M_PI * eulerVector.y();
            double yaw = 180/M_PI * eulerVector.x();
            Serial.printf("Roll = %lf\n", roll);
            if (!isnan(roll)) {
                calibrationData[0] += accelerationVector.x();
                calibrationData[1] += roll;
                calibrationData[2] += pitch;
                calibrationData[3] += yaw;
                Serial.printf("zeroCount = %d\n", zeroCount);
                zeroCount++;
            }
        }

        if (zeroCount == 20) { // If zeroCount == 20
            for (int i = 0; i < 4; i++) calibrationData[i] /= 20; // Divide calibrationData values by 20
            Serial.printf("Roll: %lf, Pitch: %lf, Yaw: %lf\n", calibrationData[1], calibrationData[2], calibrationData[3]);
            zeroedOut = true; // Set zeroedOut to true
        }
    }
   
    if (zeroedOut) { // If zeroedOut
        avgAcceleration = ((accelerationVector.x() - calibrationData[0]) + oldAcceleration) / 2; //  Smooth accleration value
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
            double pushedValue = avgAcceleration - accelerationBase;
            accelerationValues.push_back(pushedValue);
            fmsState = 3;
        } else if (isStationary && shotReady && !accelerationValues.empty()) {  // State 4: Stationary, ready to take shot (done taking shot) -> reset
            for (int i = 0; i < 9; i++) accelerationValues.pop_back();
            floodStationary();
            shotAttempt = true;
            shotReady = false;
            fmsState = 4;
        }

        // Button press overrides FMS
        if (checkButton(buttonA)) {
            isRunning = false;
            fmsState = 5;
        }
        
    }

    // Print data
    if (printGraphForm)
        graphPrint(eulerVector);
    else basicPrint(eulerVector);
    
    if (shotAttempt) {
        minima = findGlobalMinima(accelerationValues);
        accelerationValues.clear();
        mapped = mapAcceleration(minima);
        if (printMappedValue) {
            Serial.printf("Minima: %.3f, Mapped: %s\n\n", minima, ballSpeed[mapped]);
            if (speedCheckMode) while (!checkButton(buttonA)) {} // blocking statement
        }
        shotAttempt = false;
    }

    oldAcceleration = avgAcceleration;

    delay(BNO055_SAMPLERATE_DELAY_MS);
}

// Finds the strongest deceleration
double findGlobalMinima(Vector<double> accelerationValues) {
    double minimum = MAX_ACCELERATION;
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
    stationaryValues[stationaryIndex] = avgAcceleration; // Store queue of 100 acceleration values
    double minAcc = MAX_ACCELERATION;
    double maxAcc = MIN_ACCELERATION;
    
    for (int i = 0; i < 20; i++){
        if (stationaryValues[i] < minAcc) minAcc = stationaryValues[i];
        if (stationaryValues[i] > maxAcc) maxAcc = stationaryValues[i];
    }

    isStationary = (maxAcc - minAcc <= ACC_MARGIN) ? true : false; // if the min and max differenitate less than 0.5, set stationary to true
    stationaryIndex = (stationaryIndex + 1) % 20; // wrap around
}

// Resets stationary value array with non-stationary values
void floodStationary() {
    for (int i = 0; i < 20; i++) stationaryValues[i] = (i % 2 == 0) ? MIN_ACCELERATION : MAX_ACCELERATION;    
}

// Resets stationary value array
void floodStationary(int floodValue) {
    for (int i = 0; i < 20; i++) stationaryValues[i] = floodValue;    
}

void zeroOut() {
    for (int i = 0; i < 4; i++) 
        calibrationData[i] = 0;
    
    for (int i = 0; i < 20; i++) {
        imu::Vector<3> accelerationVector = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
        imu::Quaternion quaternionVector = bno.getQuat();
        quaternionVector.normalize();
        imu::Vector<3> eulerVector = quaternionVector.toEuler();

        double roll = -180/M_PI * eulerVector.z();
        if(isnan(roll)) 
            i--;
        else {
            calibrationData[0] += accelerationVector.x();
            calibrationData[1] += 180/M_PI * eulerVector.z();
            calibrationData[2] += 180/M_PI * eulerVector.y();
            calibrationData[3] += 180/M_PI * eulerVector.x();
        }
        delay(BNO055_SAMPLERATE_DELAY_MS);
    }

    for (int i = 0; i < 4; i++) {
        calibrationData[i] /= 20;
        Serial.printf("Offset #%d: %lf\n", i, calibrationData[i]);
    }

    zeroedOut = true;
    isStationary = false;
    shotReady = false;
    shotAttempt = false;
    oldAcceleration = calibrationData[0];
}

// Configure cue stick operation
void configureOperation() {
    uint8_t valuesConfigured = 0;

    if (valuesConfigured == 0) Serial.print("Speed check mode?: ");
    while (valuesConfigured == 0) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            speedCheckMode = true;
            valuesConfigured = 8;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            speedCheckMode = false;
            valuesConfigured++;
        }
    }
}

// Configure which values are printed
void configurePrint() {
    uint8_t valuesConfigured = 0;

    // Print in graph form
    Serial.print("Print in graph form: ");
    while (valuesConfigured == 0) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
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
            updateCharacteristic(buttonCharacteristic, B);
            printGraphForm = false;
            valuesConfigured++;
        }
    }

    // Use default configuration
    if (valuesConfigured == 1) Serial.print("Use default (all printed): ");
    while (valuesConfigured == 1) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
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
            updateCharacteristic(buttonCharacteristic, B);
            valuesConfigured++;
        }
    }

    // Set printFmsState
    if (valuesConfigured == 2) Serial.print("Print State?: ");
    while (valuesConfigured == 2) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printFmsState = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printFmsState = false;
            valuesConfigured++;
        }
    }
    
    // Set printStationary
    if (valuesConfigured == 3) Serial.print("Print isStationary?: ");
    while (valuesConfigured == 3) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printStationary = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printStationary = false;
            valuesConfigured++;
        }
    }
    
    // Set printShotReady
    if (valuesConfigured == 4) Serial.print("Print shotReady?: ");
    while (valuesConfigured == 4) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printShotReady = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printShotReady = false;
            valuesConfigured++;
        }
    }
    
    // Set printShotAttempt
    if (valuesConfigured == 5) Serial.print("Print FMS States?: ");
    while (valuesConfigured == 5) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printShotAttempt = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printShotAttempt = false;
            valuesConfigured++;
        }
    }
    
    // Set printVectorSize
    if (valuesConfigured == 6) Serial.print("Print vector size?: ");
    while (valuesConfigured == 6) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printVectorSize = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printVectorSize = false;
            valuesConfigured++;
        }    
    }

    // Set printMappedValue
    if (valuesConfigured == 7) Serial.print("Print mapped value?: ");
    while (valuesConfigured == 7) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printMappedValue = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printMappedValue = false;
            valuesConfigured++;
        }    
    }

    // Set printAcceleration
    if (valuesConfigured == 8) Serial.print("Print acceleration?: ");
    while (valuesConfigured == 8) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printAcceleration = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printAcceleration = false;
            valuesConfigured++;
        }
    }

    // Set printRoll
    if (valuesConfigured == 9) Serial.print("Print roll?: ");
    while (valuesConfigured == 9) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printRoll = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printRoll = false;
            valuesConfigured++;
        }    
    }

    // Set printPitch
    if (valuesConfigured == 10) Serial.print("Print pitch?: ");
    while (valuesConfigured == 10) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printPitch = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printPitch = false;
            valuesConfigured++;
        }   
    }

    // Set printYaw
    if (valuesConfigured == 11) Serial.print("Print yaw?: ");
    while (valuesConfigured == 11) {
        if (checkButton(buttonA)) {
            Serial.println("Y");
            updateCharacteristic(buttonCharacteristic, A);
            printYaw = true;
            valuesConfigured++;
        }
        if (checkButton(buttonB)) {
            Serial.println("N");
            updateCharacteristic(buttonCharacteristic, B);
            printYaw = false;
            valuesConfigured++;
        }    
    }

    Serial.println();
}

// Print for monitor
void basicPrint(imu::Vector<3> eulerVector) {
    if (printFmsState) {
        Serial.printf("State: %s\n", stateMap[fmsState]);
        updateCharacteristic(fmsCharacteristic, fmsState);
    }
    if (printStationary) Serial.printf("Stationary: %s\n", isStationary ? "True" : "False");
    if (printShotReady) Serial.printf("Shot Ready: %s\n", shotReady ? "True" : "False");
    if (printShotAttempt) Serial.printf("Shot Attempt: %s\n", shotAttempt ? "True" : "False");
    if (printVectorSize) Serial.printf("Vector Size: %d\n", accelerationValues.size());
    if (printAcceleration) {
        Serial.printf("Acceleration: %.3f\n", avgAcceleration);
        updateCharacteristic(accCharacteristic, avgAcceleration * 100);
    }
    if (printRoll) {
        Serial.printf("Roll: %.3f\n", -180/M_PI * (double) eulerVector.z() - calibrationData[1]);
        updateCharacteristic(rollCharacteristic, -180/M_PI * (double) eulerVector.z() - calibrationData[1]);
    }
    if (printPitch) {
        Serial.printf("Pitch: %.3f\n", 180/M_PI * (double) eulerVector.y() - calibrationData[2]);
        updateCharacteristic(pitchCharacteristic, 180/M_PI * (double) eulerVector.y() - calibrationData[2]);
    }
    if (printYaw) {
        Serial.printf("Yaw: %.3f\n", -(180/M_PI * (double) eulerVector.x() - calibrationData[3]));
        updateCharacteristic(yawCharacteristic, -(180/M_PI * (double) eulerVector.x() - calibrationData[3]));
    }
    Serial.println();
}

// Print for plotter
void graphPrint(imu::Vector<3> eulerVector) {
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
        Serial.print(-180/M_PI * (double) eulerVector.z() - calibrationData[1], 3);
    }
    if (printPitch) {
        Serial.print(" Pitch: ");
        Serial.print(180/M_PI * (double) eulerVector.y() - calibrationData[2], 3);
    }
    if (printYaw) {
        Serial.print(" Yaw: ");
        Serial.print(-(180/M_PI * (double) eulerVector.x() - calibrationData[3]), 3);
    }

    Serial.println("\t\t");
}
