#include "Arduino.h"
#include "Audio.h"
#include "SD.h"
#include "FS.h"
#include "BLEDevice.h"
#include <Wire.h>
 
// Digital I/O used
#define SD_CS          5
#define SPI_MOSI      23    // SD Card
#define SPI_MISO      19
#define SPI_SCK       18
 
#define I2S_DOUT      25
#define I2S_BCLK      27    // I2S
#define I2S_LRC       26
 
Audio audio;

//BLE Server name (the other ESP32 name running the server sketch)
#define bleServerName "Number_Sender"

/* UUID's of the service, characteristic that we want to read*/
// BLE Service
static BLEUUID serviceUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b"); //CHANGE the X to b *******************************************

// BLE Characteristics
static BLEUUID numberCharacteristicUUID("beb5483e-36e1-4688-b7f5-ea07361b26a8"); //CHANGE

//Flags stating if should begin connecting and if the connection is up
static volatile boolean doConnect = false;
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
    connected = false;
   // free(pClient);
    //doConnect = true;//idea is that we already have the right address WORKS
    //delay(2000);
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true);
    Serial.println("Starting scan");
    //Serial.println(uxSemaphoreGetCount(pBLEScan->m_semaphoreScanEnd.m_semaphore));//TEST check the semaphore
    pBLEScan->start(30); //PROBLEM 
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
  Serial.begin(115200);
    
    pinMode(SD_CS, OUTPUT);      
    digitalWrite(SD_CS, HIGH);
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    
    //Serial2.begin(9600,SERIAL_8N1,16,17);
    if(!SD.begin(SD_CS))
    {
      Serial.println("Error talking to SD card!");
      while(true);  // end program
    }
    audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
    audio.setVolume(21); // 0...21
    //audio.connecttoFS(SD,"/Trumpet.mp3");
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
  pBLEScan->start(300);
//audio.connecttoFS(SD,"/Heart.mp3");
    
}

 static boolean sound = true;
void loop()
{
    while (doConnect == true) {
    
    if(pServerAddress == NULL)
      Serial.println("pAddress is NULL!!??");
    else
      Serial.println("pAddress is good"); 
       
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
  
    if(newNumber){
        newNumber = false;
        //Serial.println("Hi");
        char* song;
        char inp = Serial.read();
       // Serial.println("Hi2");
        
       if(*number_received == 0)
            audio.connecttoFS(SD,"/Aim_Higher.mp3");
       else if(*number_received == 1) {
            audio.connecttoFS(SD,"/Aim_Lower.mp3"); 
            Serial.println("Hi 2.5"); 
        }
       else if (*number_received == 2)
            audio.connecttoFS(SD, "/Move_Hand_Backward.mp3");
       else if (*number_received == 3)
            audio.connecttoFS(SD, "/Move_Hand_Forward.mp3");
       else if (*number_received == 4)
            audio.connecttoFS(SD, "/Move_Hand_Left.mp3");
       else if (*number_received == 5)
            audio.connecttoFS(SD, "/Move_Hand_Right.mp3");
       else if (*number_received == 6)
            audio.connecttoFS(SD, "/Nice_Shot.mp3");
       else if (*number_received == 7)
            audio.connecttoFS(SD, "/Shoot.mp3");
       else if (*number_received == 8)
            audio.connecttoFS(SD, "/Turn_Left.mp3");
       else if (*number_received == 9)
            audio.connecttoFS(SD, "/Turn_Right.mp3");
          
    }
    if(connected)
    {
//     // if (sound)
//    //      digitalWrite(I2S_DOUT, HIGH);
//      else
//          digitalWrite(I2S_DOUT, LOW);
//
//     sound = !sound;
//     delay(1);
      audio.loop();  
    }
        
}
