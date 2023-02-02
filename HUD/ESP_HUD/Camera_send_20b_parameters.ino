//IMPORTANT : I went to ArduCAM.h and commented out all lines defining 'swap'
#include <Wire.h>
#include <ArduCAM.h>
#include <SPI.h>
#include "memorysaver.h"
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h> 

#include <esp_bt.h>
#include <esp_bt_main.h>
#include "GeneralUtils.h"
#include "esp32-hal-log.h"
#include "BLEService.h"
#include <string.h>
#include <string>
#include <unordered_set>
#include "sdkconfig.h"
#include <esp_gap_ble_api.h>

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define BMPIMAGEOFFSET 66
const char bmp_header[BMPIMAGEOFFSET] PROGMEM =
{
  0x42, 0x4D, 0x36, 0x58, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x42, 0x00, 0x00, 0x00, 0x28, 0x00,
  0x00, 0x00, 0x40, 0x01, 0x00, 0x00, 0xF0, 0x00, 0x00, 0x00, 0x01, 0x00, 0x10, 0x00, 0x03, 0x00,
  0x00, 0x00, 0x00, 0x58, 0x02, 0x00, 0xC4, 0x0E, 0x00, 0x00, 0xC4, 0x0E, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0x00, 0x00, 0xE0, 0x07, 0x00, 0x00, 0x1F, 0x00,
  0x00, 0x00
};

// set pin 5 as the slave select for the digital pot:
const int CS = 5; //Mena changed from 7 to 5

bool is_header = false;
#if defined (OV2640_MINI_2MP)
  ArduCAM myCAM( OV2640, CS );
#else
  ArduCAM myCAM( OV5642, CS );
#endif
uint8_t read_fifo_burst_BLE(ArduCAM myCAM);

//BLE STUFF
boolean deviceConnected = false;
/*typedef struct {
  uint16_t interval;
  uint16_t latency;
  uint16_t timeout;
} esp_gap_conn_params_t;*/
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer, esp_ble_gatts_cb_param_t* param){
      Serial.println("Connection established");
      deviceConnected = true;
      /*esp_gap_conn_params_t *current_params;
      esp_ble_get_current_conn_params(param->connect.remote_bda,current_params);
      Serial.println("The current connection parameters are: ");
      Serial.println(current_params->interval);
      Serial.println(current_params->latency);
      Serial.println(current_params->timeout);*/
      pServer->updateConnParams(param->connect.remote_bda,0x0F ,0x10 ,0,0x000A);//0x0A80 ->5.83,0B80->5.5 , 00A0 ->4.78, 000A->4.85 but bigger pic
    }

    /*
     max result                            throughoput
     07  5s/12KB                           2.4, 2.24
     09  5.35s/16K                         3.0
     10  5/16kB **                         3.2, 2.66, 2.5
     15 4.42/12                            2.7, 2.5,2.45
     19 2.25/10 and 4.47s/10K ****         4.44 and 2.24
     1B  error
     1D  error
     1E  5.37s/12kB
     20  error
     */
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
 
void setup() {
// put your setup code here, to run once:
//Setup bluetooth server, characteristic and descriptor
BLEDevice:: init("Number_Sender");
pServer = BLEDevice::createServer();
pServer->setCallbacks(new MyServerCallbacks());
pService = pServer->createService(SERVICE_UUID);
pCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID,
                                                 BLECharacteristic::PROPERTY_NOTIFY);
numberDescriptor.setValue("Number Descriptor");
pCharacteristic->addDescriptor(&numberDescriptor);
pService->start();
 
BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
pAdvertising->addServiceUUID(SERVICE_UUID);
BLEDevice::startAdvertising();

uint8_t vid, pid;
uint8_t temp;

Wire.begin();
Serial.begin(115200);//921600);
Serial.println(F("ACK CMD ArduCAM Start! END"));

// set the CS as an output:
pinMode(CS, OUTPUT);
digitalWrite(CS, HIGH);
// initialize SPI:
SPI.begin(SCK, MISO, MOSI, CS);
Serial.println(MOSI);
Serial.println(MISO);
Serial.println(SCK);
Serial.println(CS);
//Reset the CPLD
myCAM.write_reg(0x07, 0x80);
delay(100);
myCAM.write_reg(0x07, 0x00);
delay(100);
while(1){
  //Check if the ArduCAM SPI bus is OK
  myCAM.write_reg(ARDUCHIP_TEST1, 0x55);
  temp = myCAM.read_reg(ARDUCHIP_TEST1);
  if (temp != 0x55){
    Serial.println(F("ACK CMD SPI interface Error! END"));
    delay(1000);continue;
  }else{
    Serial.println(F("ACK CMD SPI interface OK. END"));break;
  }
}

while(1){
  //Check if the camera module type is OV2640
  myCAM.wrSensorReg8_8(0xff, 0x01);
  myCAM.rdSensorReg8_8(OV2640_CHIPID_HIGH, &vid);
  myCAM.rdSensorReg8_8(OV2640_CHIPID_LOW, &pid);
  if ((vid != 0x26 ) && (( pid != 0x41 ) || ( pid != 0x42 ))){
    Serial.println(F("ACK CMD Can't find OV2640 module! END"));
    delay(1000);continue;
  }
  else{
    Serial.println(F("ACK CMD OV2640 detected. END"));break;
  } 
}

//Change to JPEG capture mode and initialize the OV5642 module
myCAM.set_format(JPEG);
myCAM.InitCAM();
myCAM.OV2640_set_JPEG_size(OV2640_352x288);
myCAM.OV2640_set_Light_Mode(Office);
myCAM.OV2640_set_Color_Saturation(Saturation2);
delay(1000);
myCAM.clear_fifo_flag();
Serial.println("All setup complete!");
}

void loop() {
  // put your main code here, to run repeatedly:
  //wait for connection
  while(!deviceConnected){
            Serial.println("No connection detected");
            delay(1000);
        }
  
  //wait for serial monitor input, then capture and send
  if (Serial.available()){
      char temp = Serial.read();
      if (temp == '0') {   
          myCAM.flush_fifo();
          myCAM.clear_fifo_flag();
          //Start capture
          Serial.println("Capturing");
          myCAM.start_capture();
          delay(1);
          while (!myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK));
          if (myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK)){
              Serial.println("Reading fifo");
              delay(50);
              read_fifo_burst_BLE(myCAM);
             //Clear the capture done flag
             myCAM.clear_fifo_flag();
          }
          else
              Serial.print("Capture end bit was 0");
      }
      else {
        Serial.println("Invalid input detected");
      }
  }
}

uint8_t read_fifo_burst_BLE(ArduCAM myCAM)
{
  uint8_t temp = 0, temp_last = 0;
  uint32_t length = 0;
  length = myCAM.read_fifo_length();
  //Serial.println(length, DEC); MENA FOR NOW COMMENT OUT
  if (length >= MAX_FIFO_SIZE) //512 kb
  {
    Serial.println(F("ACK CMD Over size. END"));
    return 0;
  }
  if (length == 0 ) //0 kb
  {
    Serial.println(F("ACK CMD Size is 0. END"));
    return 0;
  }
  myCAM.CS_LOW();
  myCAM.set_fifo_burst();//Set fifo burst mode
  temp =  SPI.transfer(0x00);
  length --;
  Serial.println("Before loop");
  int counter = 0;
  uint64_t to_send = 0;
  uint64_t to_send_2 = 0;
  uint32_t to_send_3 = 0;
  while ( length-- )
  {
    if (counter == 20) {
        //SEND BLUETOOTH
        pCharacteristic->setValue(to_send, to_send_2, to_send_3);
        pCharacteristic->notify();
        //Serial.println(to_send, HEX);
        //Serial.println(to_send_2, HEX);
        //Serial.println();
       // Serial.println(to_send, HEX);
        counter = 0;
        to_send = 0;
        to_send_2 = 0;
        to_send_3 = 0;
        length++;
        delay(1);
        continue;
    }
    
    temp_last = temp;
    temp =  SPI.transfer(0x00);
    int int_temp = (int) temp;
    int int_temp_last = (int) temp_last;

    if (is_header == true)
    {
      //Serial.print("to_send is: ");
      //Serial.println(to_send, HEX);
      if (counter >= 8 && counter < 16){
        to_send_2 = to_send_2 <<8;
        to_send_2 += temp;
      }
      else if (counter < 8){
        to_send = to_send <<8;
        to_send += temp;
      }
      else {
        to_send_3 = to_send_3 <<8;
        to_send_3 += temp;
      }
      
      //Serial.print("Now shifting the following in: ");
      //Serial.println(temp, HEX);
      //Serial.print("To send is now: ");
      //Serial.println(to_send, HEX);
      counter ++;
      //Serial.write(temp);
      //pCharacteristic->setValue(int_temp);
      //pCharacteristic->notify();
    }
    else if ((temp == 0xD8) & (temp_last == 0xFF))
    {
      //Serial.print("to_send is: ");
      //Serial.println(to_send, HEX);
      is_header = true;
      if (counter >= 8 and counter < 16) {
        to_send_2 = int_temp_last << 8;
        to_send_2 += int_temp;
      }
      else if (counter < 8) {
        to_send = int_temp_last << 8;
        to_send += int_temp;
      }
      else {
        to_send_3 = int_temp_last << 8;
        to_send_3 += int_temp;      
      }
      counter += 2;
      //Serial.print("Now shifting the following in: ");
      //Serial.println(int_temp_last, HEX);
      //Serial.print("Now shifting the following in: ");
      //Serial.println(int_temp, HEX);
      //Serial.print("To send is now: ");
      //Serial.println(to_send, HEX);
      //Serial.println(F("ACK IMG END")); MENA FOR NOW COMMENT OUT
     // Serial.write(temp_last);
      //Serial.write(temp);
      //pCharacteristic->setValue(int_temp_last);
      //pCharacteristic->notify();
      //delay(4);
      //pCharacteristic->setValue(int_temp);
      //pCharacteristic->notify();
    }
    if ( (temp == 0xD9) && (temp_last == 0xFF) ) //If find the end ,break while,
        break;
    delayMicroseconds(15);
  }
  if(to_send != 0){
      //Serial.print("Lastly, to_send is: ");
      if (to_send_3 != 0) {
         pCharacteristic->setValue(to_send, to_send_2, to_send_3);
         pCharacteristic->notify();
      }
      else if (to_send_2 != 0){
         pCharacteristic->setValue(to_send, to_send_2);
         pCharacteristic->notify();
      }
      else {
         pCharacteristic->setValue(to_send);
         pCharacteristic->notify();
      }
     
      //Serial.println(to_send, HEX);
      to_send = 0;
      to_send_2 = 0;
      to_send_3 = 0;
      counter = 0;
  }
  Serial.println("After loop");
  myCAM.CS_HIGH();
  is_header = false;
  return 1;
}
