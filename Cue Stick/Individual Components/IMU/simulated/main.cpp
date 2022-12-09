#include <iostream>
#include <string>
#include <cstdio>
#include <vector>
#include <sstream>
#include <math.h>
#include <algorithm>
#include <chrono>
#include <vector>
#include <thread>

#define MIN_ACC -1000
#define MAX_ACC 1000
#define ACC_MARGIN 1

using namespace std;

class BNO055 {
    private:
        double acceleration[3];
        double orientation[3];
    public:
        BNO055();
        void setAcceleration(double);
        void setOrientation();
        double readAccelerationX();
        double readAccelerationY();
        double readAccelerationZ();
        double readOrientationX();
        double readOrientationY();
        double readOrientationZ();
};

BNO055::BNO055() {
    for (int i = 0; i < 3; i++) {
        acceleration[i] = 1;
        orientation[i] = 2;
    }
}

void BNO055::setAcceleration(double accInput) {
    acceleration[0] = accInput;
    std::cout << "SET ACC TO " << accInput << std::endl;
}

void BNO055::setOrientation() {
    // Ask for orientation value
    // If blank, don't change
}

double BNO055::readAccelerationX() {
    return acceleration[0];
}

double BNO055::readAccelerationY() {
    return acceleration[1];
}

double BNO055::readAccelerationZ() {
    return acceleration[2];
}

double BNO055::readOrientationX() {
    return orientation[0];
}

double BNO055::readOrientationY() {
    return orientation[1];
}

double BNO055::readOrientationZ() {
    return orientation[2];
}

std::vector<double> accelerationValues;
double stationaryValues[10];
double calData[4];
int stationaryIndex = 0;

// Global status variables
int zeroCount;
bool zeroedOut = false;
bool isStationary;
bool shotReady = false;
double accelerationBase;
double globalMinima = 0;
bool shotAttempt = false;
int fmsState = 0;

const int mapArray[7] = {-1, -3, -5, -7, -9, -11, -13};
std::string ballSpeed[] = {"SOFT_TOUCH", "SLOW", "MEDIUM", 
                            "FAST", "POWER", "BREAK", "POWER_BREAK"};

unsigned long newTime = 0;
unsigned long oldTime = 0;
unsigned long deltaTime = 0;
double oldAcceleration = 0;
double oldSpeed = 0;

void checkStationary(double avgAcceleration);
double findGlobalMinima(std::vector<double> accelerationValues);
int mapAcceleration(double acceleration);
void loop(BNO055 imu);
void floodStationary(int val);
void setup();
void loop();

int main() {
    BNO055 fakeIMU;
    setup();
    for (int i = 0; i < 50; i++) {
        std::cout << "Iteration: " << i << std::endl;
        if (i == 12) fakeIMU.setAcceleration(5);
        else if (i == 13) fakeIMU.setAcceleration(7);
        else if (i == 13) fakeIMU.setAcceleration(5);
        else if (i == 14) fakeIMU.setAcceleration(-3);
        else if (i == 15) fakeIMU.setAcceleration(1);

        else if (i == 28) fakeIMU.setAcceleration(3);
        else if (i == 29) fakeIMU.setAcceleration(5);
        else if (i == 30) fakeIMU.setAcceleration(3);
        else if (i == 31) fakeIMU.setAcceleration(1);
        else if (i == 32) fakeIMU.setAcceleration(-3);
        else if (i == 33) fakeIMU.setAcceleration(-100);
        else if (i == 34) fakeIMU.setAcceleration(1);
        loop(fakeIMU);
    }
    return 0;
}

void setup() {
    zeroedOut = true;
    isStationary = false;
    floodStationary(-100);
}

void loop(BNO055 imu) {
    // Get accleration and orientation vectors
    double acc[3];
    double ori[3];

    acc[0] = imu.readAccelerationX();
    acc[1] = imu.readAccelerationY();
    acc[2] = imu.readAccelerationZ();

    ori[0] = imu.readOrientationX();
    ori[1] = imu.readOrientationY();
    ori[2] = imu.readOrientationZ();

    if (!zeroedOut) { // If not zeroedOut
        if (zeroCount < 20) { // If zeroCount < 20
            calData[0] += acc[0];
            calData[1] += ori[0];
            calData[2] += ori[1];
            calData[3] += ori[2];
            zeroCount++;
        }

        if (zeroCount == 20) { // If zeroCount == 20
            for (int i = 0; i < 4; i++) 
                calData[i] /= 20; // Divide calData values by 20
            zeroedOut = true; // Set zeroedOut to true
        }
    }
   
    if (zeroedOut) { // If zeroedOut
        //double avgAcceleration = (-(acc[0] - calData[0]) + oldAcceleration) / 2; //  Smooth accleration value
        double avgAcceleration = acc[0] - calData[0];

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
            accelerationValues.push_back(avgAcceleration - accelerationBase);  
            //cout << "Pushed: " << avgAcceleration - accelerationBase << " (" << accelerationValues.size() << ")" << endl;
            fmsState = 3;
        } else if (isStationary && shotReady && !accelerationValues.empty()) {  // State 4: Stationary, ready to take shot (done taking shot) -> reset
            for (int i = 0; i < 9; i++) {
                //cout << "Popping: " << accelerationValues.back() << endl;
                accelerationValues.pop_back();
            }
            floodStationary(avgAcceleration);
            shotAttempt = true;
            shotReady = false;
            fmsState = 4;
        }
    }
    
    // Print status variables
    std::cout << "State: " << fmsState << std::endl;
    std::cout << "Stationary: " << (isStationary ? "True" : "False")  << std::endl;
    std::cout << "Shot Ready: " << (shotReady ? "True" : "False" )<< std::endl;

    // Print stick data
    if (shotAttempt) {
        double minima = findGlobalMinima(accelerationValues);
        accelerationValues.clear();
        int mapped = mapAcceleration(minima);
        std::cout << "Minima: " << minima << ", Mapped: " << ballSpeed[mapped] << endl;
        shotAttempt = false;
    }

    std::cout << "A: " << acc[0];
    std::cout << ", R: " << ori[0];
    std::cout << ", P: " << ori[1];
    std::cout << ", Y: " << ori[2] << std::endl;
    std::cout << std::endl;

    std::this_thread::sleep_for(0.1s);
}

double findGlobalMinima(std::vector<double> accelerationValues) {
    double minimum = 0;
    for (int s : accelerationValues) {
        //cout << s << ", ";
        minimum = (s < minimum) ? s : minimum;
    }
    //cout << endl;
    
    return minimum;
}

int mapAcceleration(double acceleration) {
    int mapped = 0;
    for (int i = 0; i < 7; i++)
        if ((int) acceleration <= mapArray[i]) mapped = i;
    
    return mapped;
}

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

void floodStationary(int val) {
    for (int i = 0; i < 10; i++) stationaryValues[i] = val;    
}