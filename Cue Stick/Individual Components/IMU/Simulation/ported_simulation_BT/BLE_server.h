// * Header file for BLE implementation
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// * BLE
#define bleServerName "CUE_ESP32" // BLE server name
bool deviceConnected = false;
#define SERVICE_UUID "91bad492-b950-4226-aa2b-4ede9fa42f59" // https://www.uuidgenerator.net/

// Cue Acceleration Characteristic and Descriptor
BLECharacteristic cueAccelerationCharacteristics("ca73b3ba-39f6-4ab3-91ae-186dc9577d99", BLECharacteristic::PROPERTY_NOTIFY);
BLEDescriptor cueAccelerationDescriptor(BLEUUID((uint16_t)0x2903));

// Setup callbacks onConnect and onDisconnect
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
    };
    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
    }
};

// Function to set up BLE connection
void setupBLE() {
    // Create the BLE Device
    BLEDevice::init(bleServerName);

    // Create the BLE Server
    BLEServer *pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    // Create the BLE Service
    BLEService *cueService = pServer->createService(SERVICE_UUID);
    
    // Create BLE Characteristics and Create a BLE Descriptor
    // Acceleration
    cueService->addCharacteristic(&cueAccelerationCharacteristics);
    cueAccelerationDescriptor.setValue("IMU acceleration");
    cueAccelerationCharacteristics.addDescriptor(new BLE2902());
    
    // Start the service
    cueService->start();

    // Start advertising
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pServer->getAdvertising()->start();
    Serial.println("Waiting a client connection to notify...");
}

// * Set characteristic value and notify client
void updateAccelerationCharacteristics(double accelerationValue) {
    // Update and notify
    cueAccelerationCharacteristics.setValue(accelerationValue);
    cueAccelerationCharacteristics.notify();
  
    // Print value
    Serial.print("Updated acceleration to: ");
    Serial.print(accelerationValue);
    Serial.println(" m/s^2");
}
