#include "BLEDevice.h"
#include <Wire.h>

//BLE Server name (the other ESP32 name running the server sketch)
#define bleServerName "Number_Sender"

/* UUID's of the service, characteristic that we want to read*/
// BLE Service
static BLEUUID serviceUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b"); //CHANGE the X to b *******************************************

// BLE Characteristics
static BLEUUID numberCharacteristicUUID("beb5483e-36e1-4688-b7f5-ea07361b26a8"); //CHANGE

//Flags stating if should begin connecting and if the connection is up
static boolean doConnect = false;
static boolean connected = false;

//Address of the peripheral device. Address will be found during scanning...
static BLEAddress *pServerAddress;
 
//Characteristicd that we want to read
static BLERemoteCharacteristic* numberCharacteristic;

//Activate notify
const uint8_t notificationOn[] = {0x1, 0x0};
const uint8_t notificationOff[] = {0x0, 0x0};

int* number_received;

//Flags to check whether new temperature and humidity readings are available
boolean newNumber = false;
BLEClient* pClient;

BLEScan* pBLEScan;
//Callback function that gets called, when another device's advertisement has been received
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    Serial.println("We are in the onResult Function");
    if (advertisedDevice.getName() == bleServerName) { //Check if the name of the advertiser matches
      Serial.println("Before Stoppping, semaphore is: ");
      Serial.println(uxSemaphoreGetCount(pBLEScan->m_semaphoreScanEnd.m_semaphore));
     advertisedDevice.getScan()->stop(); //Scan can be stopped, we found what we are looking for
      Serial.println("After stopping, semaphore is: ");
      //Serial.println(pBLEScan->m_semaphoreScanEnd.value());//TEST check the semaphore
      Serial.println(uxSemaphoreGetCount(pBLEScan->m_semaphoreScanEnd.m_semaphore));//TEST check the semaphore
      pServerAddress = new BLEAddress(advertisedDevice.getAddress()); //Address of advertiser is the one we need
      doConnect = true; //Set indicator, stating that we are ready to connect
      Serial.println("Device found. Connecting!");
    }
  }
};

class MyClientCallbacks: public BLEClientCallbacks {
  void onConnect(BLEClient *pClient){
    Serial.println("Client connected");
  }
  void onDisconnect(BLEClient *pClient) {
    
    Serial.println("Client Disconnected *****");
    /*free(pClient);
    doConnect = true;//idea is that we already have the right address WORKS
    delay(2000);*/

   // pBLEScan->erase(*pServerAddress);
    //pBLEScan->clearResults();
   // Serial.println("test");
   // free(pClient);
    //BLEDevice::m_pClient = null;
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true);
    Serial.println("Starting scan");
    //Serial.println(uxSemaphoreGetCount(pBLEScan->m_semaphoreScanEnd.m_semaphore));//TEST check the semaphore
    pBLEScan->start(10); //PROBLEM 
    Serial.println("We re out!!!");
  }
};

//Connect to the BLE Server that has the name, Service, and Characteristics
bool connectToServer(BLEAddress pAddress) {
  // Connect to the remove BLE Server.
  if(!pClient)//SATURDAY added if statement
  {
    pClient = BLEDevice::createClient();
    pClient->setClientCallbacks(new MyClientCallbacks());
  }
  
  if(pClient->connect(pAddress))
  {  
      Serial.println(" - Connected to server");
 
      // Obtain a reference to the service we are after in the remote BLE server.
      BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
      if (pRemoteService == nullptr) {
        Serial.print("Failed to find our service UUID: ");
        Serial.println(serviceUUID.toString().c_str());
        return (false);
      }
 
      // Obtain a reference to the characteristics in the service of the remote BLE server.
      numberCharacteristic = pRemoteService->getCharacteristic(numberCharacteristicUUID);

      if (numberCharacteristic == nullptr) {
        Serial.print("Failed to find our characteristic UUID");
        return false;
      }
      Serial.println(" - Found our characteristics");
 
      //Assign callback functions for the Characteristics
      numberCharacteristic->registerForNotify(numberNotifyCallback);
      return true;
  }
  return false;
}


 
//When the BLE Server sends a new number reading with the notify property
static void numberNotifyCallback(BLERemoteCharacteristic* pBLERemoteCharacteristic, 
                                        uint8_t* pData, size_t length, bool isNotify) {
  //store number value
  number_received = (int*)pData;
  newNumber = true;
}

void setup() {
  //Start serial communication
  Serial.begin(115200);
  Serial.println("Starting Arduino BLE Client application...");

  //Init BLE device
  BLEDevice::init("");
 
  // Retrieve a Scanner and set the callback we want to use to be informed when we
  // have detected a new device.  Specify that we want active scanning and start the
  // scan to run for 30 seconds.
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  Serial.println("Scanning in the SETUP function. Semaphore is:");
  //Serial.println(pBLEScan->m_semaphoreScanEnd.value());//TEST check the semaphore
  Serial.println(uxSemaphoreGetCount(pBLEScan->m_semaphoreScanEnd.m_semaphore));//TEST check the semaphore
  pBLEScan->start(5); //*************************** change 4 to 30
  //pBLEScan->setActiveScan(false); **singelton object
}

void loop() {

//  if(pClient){ //if client is not null check if not connected
//      connected = pClient->isConnected();  
 // }
 
  // If the flag "doConnect" is true then we have scanned for and found the desired
  // BLE Server with which we wish to connect.  Now we connect to it.  Once we are
  // connected we set the connected flag to be true.
  while (doConnect == true) {
    if (connectToServer(*pServerAddress)) {
      Serial.println("We are now connected to the BLE Server.");
      //Activate the Notify property of each Characteristic
      numberCharacteristic->getDescriptor(BLEUUID((uint16_t)0x2902))->writeValue((uint8_t*)notificationOn, 2, true);
      connected = true;
      doConnect = false;
    } 
    else {
          Serial.println("Will try to reconnect in 2s");
          delay(1000);
    }
  }
  
  if (newNumber){
    newNumber = false;
    Serial.println("Number received is ");
    Serial.println(*number_received);
    //delay(6000);
    //pBLEScan->start(5);
  }
  delay(1000); // Delay a second between loops.

 //This actually works (i.e I can scan again fine even after connecting), which means that the issue that stops the scanning occurs on disconnect!
  /*if(connected){
    Serial.println("Preparing to RESCAN");
    pBLEScan->start(5);
  }*/ 
  
}
