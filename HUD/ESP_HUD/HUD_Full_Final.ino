#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include "Arduino.h"
#include "Audio.h"
#include "SD.h"
#include "FS.h"
#include "BLEDevice.h"
#include <Wire.h>
#include <ArduCAM.h>
#include <SPI.h>
#include "memorysaver.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

//pins for display
#define DISP_SDA 33
#define DISP_SCL 32
//IO pins used for Audio SD
//SD gets HSPI
#define SD_CS   15
#define SD_MOSI  13
#define SD_MISO  34
#define SD_SCK   14
#define I2S_DOUT 25
#define I2S_BCLK 27
#define I2S_LRC 26
//camera gets VSPI 
#define CAM_CS 5
#define CAM_MOSI  23
#define CAM_MISO  19
#define CAM_SCK  18

bool send_picture = false;
//state variables
bool mode_detected = false;
int blind_mode = 0;
int power_value = 0;
int poi_value_x = 0;
int poi_value_y = 0;
int state = 0;

//For the speaker
Audio audio;

//for the camera
bool is_header = false;
#if defined (OV2640_MINI_2MP)
  ArduCAM myCAM( OV2640, CAM_CS );
#else
  ArduCAM myCAM( OV5642, CAM_CS );
#endif

//For the display
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire1, -1);
//Adafruit_SSD1306* pdisplay; // change WIRE

//BLE Service and Characteristic UUIDs
#define SERVICE_UUID "843b4b1e-a8e9-11ed-afa1-0242ac120002"
#define MODE_CHAR_UUID "10c4bfee-a8e9-11ed-afa1-0242ac120002"
#define POWER_CHAR_UUID "10c4c44e-a8e9-11ed-afa1-0242ac120002"
#define POI_CHAR_X_UUID "10c4c69c-a8e9-11ed-afa1-0242ac120002"
#define POI_CHAR_Y_UUID "10c4c696-a8e9-11ed-afa1-0242ac120002"
#define ANGLE_CHAR_UUID "10c4c886-a8e9-11ed-afa1-0242ac120002"
#define AUDIO_CHAR_UUID "10c4ce76-a8e9-11ed-afa1-0242ac120002"
#define IMAGE_CHAR_UUID "10c4d3a8-a8e9-11ed-afa1-0242ac120002"
#define FSM_CHAR_UUID "10c4d3a9-a8e9-11ed-afa1-0242ac120002"

//BLE server and characteristics
BLEServer *pServer;
BLEService *pService;
BLECharacteristic *mode_char;
BLECharacteristic *power_char;
BLECharacteristic *poi_x_char;
BLECharacteristic *poi_y_char;
BLECharacteristic *angle_char;
BLECharacteristic *audio_char;
BLECharacteristic *image_char;
BLECharacteristic *fsm_char;
BLEDescriptor mode_descriptor(BLEUUID((uint16_t)0x2902));
BLEDescriptor power_descriptor(BLEUUID((uint16_t)0x2902));
BLEDescriptor poi_x_descriptor(BLEUUID((uint16_t)0x2902));
BLEDescriptor poi_y_descriptor(BLEUUID((uint16_t)0x2902));
BLEDescriptor angle_descriptor(BLEUUID((uint16_t)0x2902));
BLEDescriptor audio_descriptor(BLEUUID((uint16_t)0x2902));
BLEDescriptor image_descriptor(BLEUUID((uint16_t)0x2902));
BLEDescriptor fsm_descriptor(BLEUUID((uint16_t)0x2902));

//create these objects to save memory space in onWrite callback
BLEUUID* mode_uuid_obj = new BLEUUID(MODE_CHAR_UUID);
BLEUUID* power_uuid_obj = new BLEUUID(POWER_CHAR_UUID);
BLEUUID* angle_uuid_obj = new BLEUUID(ANGLE_CHAR_UUID);
BLEUUID* poi_x_uuid_obj = new BLEUUID(POI_CHAR_X_UUID);
BLEUUID* poi_y_uuid_obj = new BLEUUID(POI_CHAR_Y_UUID);
BLEUUID* image_uuid_obj = new BLEUUID(IMAGE_CHAR_UUID);
BLEUUID* audio_uuid_obj = new BLEUUID(AUDIO_CHAR_UUID);
BLEUUID* fsm_uuid_obj = new BLEUUID(FSM_CHAR_UUID);

//display functions
// Draw Ball Function (ALWAYS THE SAME) (CenterX,CenterY,Radius,Color)
void DrawBall() {
  display.drawCircle(55, 32, 30, SSD1306_WHITE);
}
//***************************************************************************//
//Draw Triangle on ball based on target value (VERTICAL ONLY)
//Print "Target" at top left
void DrawBallTarget(int poi_valuey, int poi_valuex) {
//Offset 0,0 to center of ball 
//  Serial.print("[Display Function]: The following are the x,y coordinates to be displayed: ");
//  Serial.print(poi_valuex);
//  Serial.print(", ");
//  Serial.println(poi_valuey);
  
  poi_valuex = poi_valuex + 50;
  poi_valuey = -1* poi_valuey + 27;
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println((state == 4) ? "Actual:" : "Target:"); 
//  Serial.print("State is ");
//  Serial.println(state);
//  Serial.println((state == 4) ? "Actual:" : "Target:"); 
  if(poi_valuex < 67){
     display.drawTriangle(poi_valuex, poi_valuey, (poi_valuex + 5), (poi_valuey + 10), (poi_valuex + 10), poi_valuey, SSD1306_WHITE);
  }
  else {
      display.setCursor(50, 27);
      display.println("?");
  }
  
}
//***************************************************************************//
//Power Meter, fills based on given power 1 - 5
void DrawPowerMeter(int power_value) {
  for (int i = 0; i < 5; i++) {
    if (i < power_value) {
      display.fillRect(90, (44 - (8 * i)), 30, 7, SSD1306_WHITE);
    } else {
      display.drawRect(90, (44 - (8 * i)), 30, 7, SSD1306_WHITE);
    }
  }
}
//***************************************************************************//

//camera read and send function
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

  uint8_t *pbyte = (uint8_t*)(&to_send);
  uint8_t *pbyte_2 = (uint8_t*)(&to_send_2);
  uint8_t *pbyte_3 = (uint8_t*)(&to_send_3);
  
  while ( length-- )
  {
//    Serial.print("Starting loop. Length is ");
//    Serial.println(length);
//
//    Serial.print("Starting loop. Counter is ");
//    Serial.println(counter);
    
    if (counter == 20) {
        //SEND BLUETOOTH
        //Serial.println("B4 BLE");
        image_char->setValue(to_send, to_send_2, to_send_3);
        //Serial.println("Mid BLE");
        image_char->notify();
        //Serial.println("After BLE");
       /* for(int i = 7; i >= 0; i--){
          Serial.write(*(pbyte + i));
          //Serial.write(0x5c);
          //Serial.print("WTF");
        }
        for(int i = 7; i >= 0; i--){
          Serial.write(*(pbyte_2 + i));
        }
        for(int i = 3; i >= 0; i--){
          Serial.write(*(pbyte_3 + i));
        }*/
        //Serial.println(to_send, HEX);
        //Serial.println(to_send_2, HEX);
        //Serial.println();
       // Serial.println(to_send, HEX);
        counter = 0;
        to_send = 0;
        to_send_2 = 0;
        to_send_3 = 0;
        length++;
        delay(3); //was 3
        //Serial.println("Sending 20 bytes");
        //Serial.print("Length is ");
       // Serial.println(length);
        continue;
    }
    
    temp_last = temp;
    //Serial.println("b4 SPI");
    temp =  SPI.transfer(0x00);
   // Serial.println("After SPI");
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
      //image_char->setValue(int_temp);
      //image_char->notify();
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
      //image_char->setValue(int_temp_last);
      //image_char->notify();
      //delay(4);
      //image_char->setValue(int_temp);
      //image_char->notify();
    }
    if ( (temp == 0xD9) && (temp_last == 0xFF) ) //If find the end ,break while,
        break;
    delayMicroseconds(15);
  }
 // Serial.println("Exiting loop");
  if(to_send != 0){
      Serial.println("Sending last group");
      //Serial.print("Lastly, to_send is: ");
      if (to_send_3 != 0) {
         image_char->setValue(to_send, to_send_2);
         image_char->notify();
         delay(3);

         counter -= 16;
         for (int i = counter; i > 0 ; i--){
             image_char->setValue(*(pbyte_3 + i -1)); 
             image_char->notify();
             delay(3);
         }
         
         /*for(int i = 7; i >= 0; i--){
          Serial.write(*(pbyte + i));
        }
        for(int i = 7; i >= 0; i--){
          Serial.write(*(pbyte_2 + i));
        }
        for(int i = 3; i >= 0; i--){
          Serial.write(*(pbyte_3 + i));
        }*/
      }
      else if (to_send_2 != 0){
         image_char->setValue(to_send);
         image_char->notify();
         delay(3);

         counter -= 8;
         for (int i = counter; i > 0 ; i--){
             image_char->setValue(*(pbyte_2 + i -1)); 
             image_char->notify();
             delay(3);
         }
         
         /*for(int i = 7; i >= 0; i--){
          Serial.write(*(pbyte + i));
        }
        for(int i = 3; i >= 0; i--){
          Serial.write(*(pbyte_2 + i));
        }*/
      }
      else {
         for (int i = counter; i > 0 ; i--){
             image_char->setValue(*(pbyte + i -1)); 
             image_char->notify();
             delay(3);
         }
        /*for(int i = 7; i >= 0; i--){
          Serial.write(*(pbyte + i));
        }  */
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

//BLE write characteristics callback
//store the value based on the uuid of the characteristic
class MyCharacteristicCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* rx_char) {
        BLEUUID uuid = rx_char->getUUID();
        if(uuid.equals(*mode_uuid_obj)){
            mode_detected = true; 
            //TODO coordinate with Luke.
            blind_mode = *(rx_char->getData());
            Serial.print("blind mode value updated to ");
            Serial.println(blind_mode); 
        }
        else if(uuid.equals(*power_uuid_obj)) {
            power_value = *(rx_char->getData());
            Serial.print("power value updated to ");
            Serial.println(power_value);
        }
        else if(uuid.equals(*angle_uuid_obj)) {
            int x = 5;//Dummy for now TODO  
        }
        else if(uuid.equals(*poi_x_uuid_obj)) {
            uint8_t* pdata = rx_char->getData();
            poi_value_x = *pdata;
           // Serial.print("Intermediate poi_x value: ");
            //Serial.println(poi_value_x);
            for( int i = 1; i <= 3; i++)
            {
              //Serial.print("Intermediate pdata value: ");
              //Serial.println(pdata[i]);
              poi_value_x = poi_value_x <<8;
              poi_value_x += pdata[i];
              //Serial.print("Intermediate poi_x value: ");
              //Serial.println(poi_value_x);
            } 
            Serial.print("poi_x value updated to ");
            Serial.println(poi_value_x);
        }
        else if(uuid.equals(*poi_y_uuid_obj)) {
            uint8_t* pdata = rx_char->getData();
            poi_value_y = *pdata;
            for( int i = 1; i <= 3; i++)
            {
              poi_value_y = poi_value_y <<8;
              poi_value_y += pdata[i];
              //Serial.print("Intermediate poi_y value: ");
              //Serial.println(poi_value_y);
            } 
            Serial.print("poi_y value updated to ");
            Serial.println(poi_value_y);
        }
        else if(uuid.equals(*audio_uuid_obj)) {
            //coordinate with Luke
            int num = *(rx_char->getData());
            Serial.print("Received audio command ");
            Serial.println(num);
            if (num == 0){
              audio.connecttoFS(SD,"/Welcome to Scratch.mp3");
            }
            else if (num == 1){
              audio.connecttoFS(SD,"/Visually Impaired Prompt.mp3");
            }
            else if (num == 2){
              audio.connecttoFS(SD,"/Entering Blind Mode.mp3");
            }
            else if (num == 3){
              audio.connecttoFS(SD,"/Entering Non-Impaired Mode.mp3");
            }
            else if (num == 4){
              audio.connecttoFS(SD,"/Press for Training Mode.mp3");
            }
            else if (num == 5){
              audio.connecttoFS(SD,"/Entering Game Mode.mp3");
            }
            else if (num == 6){
              audio.connecttoFS(SD,"/Entering Training Mode.mp3");
            }
            else if (num == 7){
              audio.connecttoFS(SD,"/Move Glove for Calibration.mp3");
            }
            else if (num == 8){
              audio.connecttoFS(SD,"/Press Glove Button.mp3");
            }
            else if (num == 9){
              audio.connecttoFS(SD,"/Press Glove Button.mp3");
            }
            else if (num == 10){
              audio.connecttoFS(SD,"/Turn Left.mp3");
            }
            else if (num == 11){
              audio.connecttoFS(SD,"/Turn Right.mp3");
            }
            else if (num == 12){
              audio.connecttoFS(SD,"/Move Hand Forward.mp3");
            }
            else if (num == 13){
              audio.connecttoFS(SD,"/Move Hand Backward.mp3");
            }
            else if (num == 14){
              audio.connecttoFS(SD,"/Aim Higher.mp3");
            }
            else if (num == 15){
              audio.connecttoFS(SD,"/Aim Lower.mp3");
            }
            else if (num == 16){
              audio.connecttoFS(SD,"/Checking Glove Angle.mp3");
            }
            else if (num == 17){
              audio.connecttoFS(SD,"/Glove Angle Correct.mp3");
            }
            else if (num == 18){
              audio.connecttoFS(SD,"/Checking Glove Distance.mp3");
            }
            else if (num == 19){
              audio.connecttoFS(SD,"/Glove Distance Correct.mp3");
            }
            else if (num == 20){
              audio.connecttoFS(SD,"/Checking Cue Pitch.mp3");
            }
            else if (num == 21){
              audio.connecttoFS(SD,"/Cue Stick Level.mp3");
            }
            else if (num == 22){
              audio.connecttoFS(SD,"/Shoot.mp3");
            }
            else if (num == 23){
              audio.connecttoFS(SD,"/Nice Shot.mp3");
            }
            else if (num == 24){
              audio.connecttoFS(SD,"/You Suck.mp3");
            }
            else if (num == 25){
              audio.connecttoFS(SD,"/You're Blind.mp3");
            }
            else {
              Serial.println("Invalid audio input");
            }
        }
        else if(uuid.equals(*fsm_uuid_obj)) {
            state = *(rx_char->getData());
            Serial.print("Recevied the state ");
            Serial.print(state);
            if(state == 3){ //this can be too early. Is there a way to optimize when we take the shot?
                send_picture = true;
                
            }
                     
        }
        else {
          Serial.println("Invalid UUID received");
        }
    }
};

//BLE Server stuff
boolean deviceConnected = false;
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer, esp_ble_gatts_cb_param_t* param){
        Serial.println("Connection established");
        deviceConnected = true;
        pServer->updateConnParams(param->connect.remote_bda,0x0F ,0x10 ,0,0x000A);//0x0A80 ->5.83,0B80->5.5 , 00A0 ->4.78, 000A->4.85 but bigger pic
    }
    
    void onDisconnect(BLEServer* pServer) {
        Serial.println("Re-advertising due to disconnect");
        deviceConnected = false;
        pServer->startAdvertising(); // restart advertising
    }
};

void setup() {
    Serial.begin(115200);
    
    
    //create BLE server and characteristics
    BLEDevice::init("HUD_Server");
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());
    pService = pServer->createService(BLEUUID(SERVICE_UUID), 40, 0);
    mode_char = pService->createCharacteristic(MODE_CHAR_UUID, BLECharacteristic::PROPERTY_WRITE_NR);
    power_char = pService->createCharacteristic(POWER_CHAR_UUID, BLECharacteristic::PROPERTY_WRITE_NR);
    angle_char = pService->createCharacteristic(ANGLE_CHAR_UUID, BLECharacteristic::PROPERTY_WRITE_NR);
    poi_x_char = pService->createCharacteristic(POI_CHAR_X_UUID, BLECharacteristic::PROPERTY_WRITE_NR);
    poi_y_char = pService->createCharacteristic(POI_CHAR_Y_UUID, BLECharacteristic::PROPERTY_WRITE_NR);
    image_char = pService->createCharacteristic(IMAGE_CHAR_UUID, BLECharacteristic::PROPERTY_NOTIFY);
    audio_char = pService->createCharacteristic(AUDIO_CHAR_UUID, BLECharacteristic::PROPERTY_WRITE_NR);
    fsm_char = pService->createCharacteristic(FSM_CHAR_UUID, BLECharacteristic::PROPERTY_WRITE_NR);

    //Set BLE Charachteristics callbacks
    mode_char->setCallbacks(new MyCharacteristicCallbacks());
    power_char->setCallbacks(new MyCharacteristicCallbacks());
    angle_char->setCallbacks(new MyCharacteristicCallbacks());
    poi_x_char->setCallbacks(new MyCharacteristicCallbacks());
    poi_y_char->setCallbacks(new MyCharacteristicCallbacks());
    //image_char->setCallbacks(new MyCharacteristicCallbacks());
    audio_char->setCallbacks(new MyCharacteristicCallbacks());
    fsm_char->setCallbacks(new MyCharacteristicCallbacks());

    //Set Descriptors (TODO: Test if this is really needed)
    mode_descriptor.setValue("Mode Descriptor");
    poi_x_descriptor.setValue("POI_X Descriptor");
    poi_y_descriptor.setValue("POI_Y Descriptor");
    angle_descriptor.setValue("Angle Descriptor");
    power_descriptor.setValue("Power Descriptor");
    audio_descriptor.setValue("Audio Descriptor");
    image_descriptor.setValue("Image Descriptor");
    fsm_descriptor.setValue("FSM Descriptor");

    //Assign descriptors (TODO: Test if this is really needed)
    mode_char->addDescriptor(&mode_descriptor);
    power_char->addDescriptor(&power_descriptor);
    angle_char->addDescriptor(&angle_descriptor);
    poi_x_char->addDescriptor(&poi_x_descriptor);
    poi_y_char->addDescriptor(&poi_y_descriptor);
    image_char->addDescriptor(&image_descriptor);
    audio_char->addDescriptor(&audio_descriptor);
    fsm_char->addDescriptor(&fsm_descriptor);

    //start the service
    pService->start();
    
    //advertise the service
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    BLEDevice::startAdvertising();
    Serial.println("Bluetooth Setup complete!");
    delay(8000);
    Serial.println("Setting up SD card");
    //initial audio setup
    pinMode(SD_CS, OUTPUT);
    digitalWrite(SD_CS, HIGH);
    SPI.begin(SD_SCK, SD_MISO, SD_MOSI);
    if(!SD.begin(SD_CS))
    {
      Serial.println("Error talking to SD card!");
      //delay(800);
      while(true);  // end program
    }
    audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
    audio.setVolume(21); // 0...21
    audio.connecttoFS(SD,"/Nice Shot.mp3");
    
    //wait till connection to Pi
    while(!deviceConnected){
            Serial.println("No connection detected");
            delay(1000);
        }
    
//    wait till we detect whether its blind mode or not
    Serial.println("Before Nice shot");
    Serial.println(audio.getAudioCurrentTime());
    Serial.println(audio.getAudioFileDuration());
    while(blind_mode == 0) {
         audio.loop();
    }
    Serial.println("After Nice shot");
    //delay(5000);//wait to see if button is pressed

    
    //delay(2000);
    
    if(blind_mode != 1) {
        //instruct the user to press stick buttons for game vs training mode (though from HUD perspective we dont care)
        audio.connecttoFS(SD,"/Aim Higher.mp3");
        Serial.println("Before shoot");
        while(blind_mode != 3 and blind_mode !=4) {
             audio.loop();
        }
         Serial.println("after shoot");
      
        //turn off audio and SD card
        digitalWrite(SD_CS, HIGH);
        SPI.end(); //may need to consult with https://forum.arduino.cc/t/spi-end-causes-spi-transfer-to-hang-even-after-a-new-spi-begin/161700
        //SPI.setSPINum(VSPI);
        SPI = *(new SPIClass(VSPI));
        
        //initialize camera
        Wire.begin();
        pinMode(CAM_CS, OUTPUT);
        digitalWrite(CAM_CS, HIGH);
        SPI.begin(CAM_SCK, CAM_MISO, CAM_MOSI, CAM_CS);
        SPI.setFrequency(2000000);
        uint8_t vid, pid, temp;
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
         myCAM.OV2640_set_JPEG_size(OV2640_640x480); //  OV2640_352x288 OV2640_1600x1200
         myCAM.OV2640_set_Light_Mode(Office);
         myCAM.OV2640_set_Color_Saturation(Saturation1);
         myCAM.OV2640_set_Brightness(Brightness_2);
         myCAM.OV2640_set_Special_effects(Normal);
         delay(1000);
         myCAM.clear_fifo_flag();
         
         //initialize display
         Wire1.begin(DISP_SDA, DISP_SCL);
         //pdisplay = &display;
         if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
             Serial.println(F("SSD1306 allocation failed"));
             for (;;);
         }
          display.clearDisplay();
    }
}

void loop() {
    //ensure connectivity
    while (!deviceConnected){
        Serial.println("No connection detected");
        delay(1000);  
    }    
    //blind mode: audio only
    if (blind_mode == 1) {
        audio.loop(); //Assuming the connectToFSD will be done in callback function
    }
    //non blind mode: camera and display
    else {
        //display
        display.clearDisplay();
        DrawBall();
        DrawPowerMeter(power_value);
        DrawBallTarget(poi_value_y, poi_value_x);
        display.display();

        //camera
        if(send_picture){
          send_picture = false;
          //take and send picture
                myCAM.flush_fifo();
                delay(100);
                myCAM.clear_fifo_flag();
                delay(100);
                
                //Start capture
                Serial.println("Capturing");
                myCAM.start_capture();
                delay(100);
                while (!myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK));
                
                //send pic and clear flag
                if (myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK)){
                    Serial.println("Reading fifo");
                    delay(50);
                    read_fifo_burst_BLE(myCAM);
                   //Clear the capture done flag
                   myCAM.clear_fifo_flag();
                   delay(100);
                }
                else
                    Serial.print("Capture end bit was 0");
        }
    }
}
