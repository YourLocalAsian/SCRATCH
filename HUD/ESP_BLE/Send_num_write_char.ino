#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a9"

boolean deviceConnected = false;
 class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer){
      Serial.println("Connection established");
      deviceConnected = true;
    }
    void onDisconnect(BLEServer* pServer) {
      Serial.println("Re-advertising due to disconnect");
      deviceConnected = false;
      pServer->startAdvertising(); // restart advertising
    }
};

 BLEServer *pServer;
 BLEService *pService;
 BLECharacteristic *pCharacteristic;
 BLEDescriptor numberDescriptor(BLEUUID((uint16_t)0x2902));

 class MyCharacteristicCallbacks: public BLECharacteristicCallbacks {
     void onWrite(BLECharacteristic* pCharacteristic) {
         Serial.print("Client write detected. Value is ");
         uint8_t * Data = pCharacteristic->getData();
         for (int i = 0; i < pCharacteristic->getValue().length(); i++)
             Serial.println(*(Data + i));

         //generate random char
          int num = random(1,10);

          Serial.println("Number is ");
          Serial.println(num);
  
         //set the characteristic to that char & start service
         pCharacteristic->setValue(num);
         pCharacteristic->notify();
     }
 };
 
void setup() {
  // put your setup code here, to run once:
  BLEDevice:: init("Number_Sender");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID,
                                                   BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE_NR);
  pCharacteristic->setCallbacks(new MyCharacteristicCallbacks());
  numberDescriptor.setValue("Number Descriptor");
  pCharacteristic->addDescriptor(&numberDescriptor);
  pService->start();
  
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  BLEDevice::startAdvertising();
  
  Serial.begin(9600);
  Serial.println("Setup complete!");
}

void loop() {
   while(!deviceConnected){
            Serial.println("No connection detected");
            delay(1000);
        }
  // put your main code here, to run repeatedly:
  //generate random char
 // int num = random(1,10);

 // Serial.println("Number is ");
 // Serial.println(num);
  
  //set the characteristic to that char & start service
 // pCharacteristic->setValue(num);
 // pCharacteristic->notify();

  //uint8_t * Data = pCharacteristic->getData();
  //for (int i = 0; i < pCharacteristic->getValue().length(); i++)
  //     Serial.println(*(Data + i));
             
  //Serial.println("Value notified");
  Serial.println("Waiting for 6s");
  //wait 2 seconds
  delay(6000);

}
