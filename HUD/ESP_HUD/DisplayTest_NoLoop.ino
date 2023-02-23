/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com
*********/

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Setting I2C pins for not default
#define DISPLAY_SDA 33
#define DISPLAY_SCL 32

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire1, -1);


void setup() {
  Serial.begin(115200);
  Wire1.begin(DISPLAY_SDA, DISPLAY_SCL);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  } 
}

//***************************************************************************//
// Draw Ball Function (ALWAYS THE SAME) (CenterX,CenterY,Radius,Color)
void DrawBall() {
  display.drawCircle(55, 32, 30, SSD1306_WHITE);
}
//***************************************************************************//
//Draw Triangle on ball based on target value (VERTICAL ONLY)
//Print "Target" at top left
void DrawBallTarget(int poi_valuey, int poi_valuex) {
//Offset 0,0 to center of ball 
  poi_valuex = poi_valuex + 50;
  poi_valuey = poi_valuey + 27;
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Target:"); 
  display.drawTriangle(poi_valuex, poi_valuey, (poi_valuex + 5), (poi_valuey + 10), (poi_valuex + 10), poi_valuey, SSD1306_WHITE);
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

void loop() {

  int poi_valuey = 0;
  int poi_valuex = 0;
  int power_value = 2;
  display.clearDisplay();
  DrawBall();
  DrawBallTarget(poi_valuey, poi_valuex);
  DrawPowerMeter(power_value);
  display.display();
}


////Draw Triangle on ball based on Actual value (VERTICAL ONLY (CURRENTLY))
////Print "Actual" at top left
//void DrawBallActual(int actualY) {
//  display.setTextSize(1);
//  display.setTextColor(WHITE);
//  display.setCursor(0, 0);
//  display.println("Actual:");
//  display.drawTriangle(50, actualY, 55, (actualY + 10), 60, actualY, SSD1306_WHITE);
