/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com  
*********/

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);


void setup() {
  Serial.begin(115200);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
    
  
}

void loop() {

  display.clearDisplay();
  DrawBall();
  DrawBallTarget(27);
  PowerMeter(4);
  display.display();
  delay(5000);
  display.clearDisplay();
  DrawBall();
  DrawBallActual(40);
  PowerMeter(1);
  display.display();
  delay(5000);

}
// Draw Ball Function (ALWAYS THE SAME) (CenterX,CenterY,Radius,Color)
void DrawBall(){
  display.drawCircle(55, 32, 30, SSD1306_WHITE);
}
//Draw Triangle on ball based on target value (VERTICAL ONLY)
//Print "Target" at top left
void DrawBallTarget(int targetY){
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0, 0);    
    display.println("Target:");
    display.drawTriangle(50, targetY, 55, (targetY+10), 60, targetY, SSD1306_WHITE);
}
//Draw Triangle on ball based on Actual value (VERTICAL ONLY (CURRENTLY))
//Print "Actual" at top left
void DrawBallActual(int actualY){
display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0, 0);    
    display.println("Actual:");
    display.drawTriangle(50, actualY, 55, (actualY+10), 60, actualY, SSD1306_WHITE);

}
//Power Meter, fills based on given power 1 - 7
void PowerMeter(int power){
  for(int i=0; i<=7; i++){
    if(i <= power){
      display.fillRect(90, (60-(7*i)), 30, 7, SSD1306_WHITE);
    }else{
      display.drawRect(90, (60-(7*i)), 30, 7, SSD1306_WHITE);
    }
  } 
}
