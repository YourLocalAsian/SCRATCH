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
 
int trigPinA = 2;    // Trigger
int echoPinA = 3;    // Echo
int trigPinB = 4;    // Trigger
int echoPinB = 5;    // Echo

double durationA, cmA, inchesA;
double durationB, cmB, inchesB;
double oldInchesA, oldInchesB;
unsigned long timeA, timeB;
bool seenBallA = false;
bool seenBallB = false;
 
void setup() {
    //Serial Port begin
    Serial.begin(9600);
    
    //Define inputs and outputs
    pinMode(trigPinA, OUTPUT);
    pinMode(echoPinA, INPUT);
    pinMode(trigPinB, OUTPUT);
    pinMode(echoPinB, INPUT);

    oldInchesA = -100.00;
    oldInchesB = -100.00;
}
 
void loop() {
    // Check if both sensors saw the ball
    if (seenBallA && seenBallB) {
        double deltaTime = (timeB - timeA) / 1000.0;
        double speed = 12.0 / deltaTime;
        Serial.print("Speed: ");
        Serial.print(speed);
        Serial.print(" in/s ");
        Serial.print(speed / 17.6);
        Serial.println(" mph");
        delay(10000);
        oldInchesA = -100.00;
        oldInchesB = -100.00;
        seenBallA = false;
        seenBallB = false;
    }

    // Check sensor A
    digitalWrite(trigPinA, LOW);
    delayMicroseconds(5);
    digitalWrite(trigPinA, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPinA, LOW);
    pinMode(echoPinA, INPUT);
    durationA = pulseIn(echoPinA, HIGH);

    inchesA = (durationA/2) / 74;   // Divide by 74 or multiply by 0.0135

    Serial.print("Sensor A: ");
    Serial.print(inchesA);

    // Check if distance changed
    if (!seenBallA) {
        if (inchesA < 15 && oldInchesA != -100.00) {
            seenBallA = true;
            timeA = millis();
        }
    }

    // Check sensor B
    digitalWrite(trigPinB, LOW);
    delayMicroseconds(5);
    digitalWrite(trigPinB, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPinB, LOW);
    pinMode(echoPinB, INPUT);
    durationB = pulseIn(echoPinB, HIGH);

    inchesB = (durationB/2) / 74;   // Divide by 74 or multiply by 0.0135

    Serial.print(" Sensor B: ");
    Serial.print(inchesB);
    Serial.println("\t\t");
        
    if (!seenBallB) {
        if (inchesB < 15 && oldInchesB != -100.00) {
            seenBallB = true;
            timeB = millis();
        }
    }

    oldInchesA = inchesA;
    oldInchesB = inchesB;

    // Timeout & reset
    if (millis() - timeA > 10000) seenBallA = false;
    if (millis() - timeB > 10000) seenBallB = false;
    
    delay(25);
}
