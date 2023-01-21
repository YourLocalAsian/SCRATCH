/*
 * created by Rui Santos, https://randomnerdtutorials.com
 * 
 * Complete Guide for Ultrasonic Sensor HC-SR04
 *
    Ultrasonic sensor Pins:
        VCC: +5VDC
        Trig : Trigger (INPUT) - Pin11
        Echo: Echo (OUTPUT) - Pin 12
        GND: GND
 */
 
int trigPinA = 7;    // Trigger
int echoPinA = 12;    // Echo
int trigPinB = 2;    // Trigger
int echoPinB = 3;    // Echo
long durationA, cmA, inchesA;
long durationB, cmB, inchesB;
long oldInchesA, oldInchesB;
unsigned long timeA, timeB;
bool seenBallA = false, seenBallB = false;
 
void setup() {
    //Serial Port begin
    Serial.begin(9600);
    //Define inputs and outputs
    pinMode(trigPinA, OUTPUT);
    pinMode(echoPinA, INPUT);
    pinMode(trigPinB, OUTPUT);
    pinMode(echoPinB, INPUT);
}
 
void loop() {
    // Check if both sensors saw the ball
    if (seenBallA && seenBallB) {
        unsigned long deltaTime = seenBallB - seenBallA;
        double speed = deltaTime / 36.0;
        Serial.printf("Speed: %f in/s\n", speed);
        delay(5000);
        oldInchesA = 1000;
        oldInchesB = 1000;
        seenBallA = false;
        seenBallB = false;
    }

    // The sensor is triggered by a HIGH pulse of 10 or more microseconds.
    // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
    digitalWrite(trigPinA, LOW);
    digitalWrite(trigPinB, LOW);
    delayMicroseconds(5);
    digitalWrite(trigPinA, HIGH);
    digitalWrite(trigPinB, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPinA, LOW);
    digitalWrite(trigPinB, LOW);
    
    // Read the signal from the sensor: a HIGH pulse whose
    // duration is the time (in microseconds) from the sending
    // of the ping to the reception of its echo off of an object.
    pinMode(echoPinA, INPUT);
    pinMode(echoPinB, INPUT);
    durationA = pulseIn(echoPinA, HIGH);
    durationB = pulseIn(echoPinB, HIGH);
    
    // Convert the time into a distance
    cmA = (durationA/2) / 29.1;     // Divide by 29.1 or multiply by 0.0343
    inchesA = (durationA/2) / 74;   // Divide by 74 or multiply by 0.0135
    cmB = (durationB/2) / 29.1;     // Divide by 29.1 or multiply by 0.0343
    inchesB = (durationB/2) / 74;   // Divide by 74 or multiply by 0.0135

    // Check if distance changed
    if (!seenBallA) {
        if (abs(oldInchesA - inchesA) > 10 && oldInchesA < 100) {
            seenBallA = true;
            timeA = millis();
        }
        oldInchesA = inchesA;
    }

    if (!seenBallB) {
        if (abs(oldInchesB - inchesB) > 10 && oldInchesB < 100) {
            seenBallB = true;
            timeB = millis();
        }
        oldInchesB = inchesB;
    }
    
    delay(250);
}
