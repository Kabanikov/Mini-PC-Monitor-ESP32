#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

// Пины для Super Mini ESP32-C6
#define I2C_SDA 6 
#define I2C_SCL 7

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Данные ПК
unsigned long lastPacketTime = 0;
uint8_t cpu = 0, ram = 0, gpu = 0, gpuTemp = 0;

// Переменные скринсейвера
float msgX = 10;
float msgY = 10;
float dx = 0.8; 
float dy = 0.6; 
const int msgW = 80; 
const int msgH = 18; 

void setup() {
  // Важно: для C6 с USB CDC скорость 115200 оптимальна
  Serial.begin(115200);
  Wire.begin(I2C_SDA, I2C_SCL);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for(;;); // Остановка, если экран не найден
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(20, 25);
  display.print(F("SYSTEM READY"));
  display.display();
  delay(1500);
}

void loop() {
  // Ждем пакет из 4 байт
  if (Serial.available() >= 4) {
    cpu = Serial.read();
    ram = Serial.read();
    gpu = Serial.read();
    gpuTemp = Serial.read();
    
    lastPacketTime = millis();
    drawUI();
    
    // Очистка если прилетело лишнее (защита от десинхронизации)
    while(Serial.available() > 0) Serial.read(); 
  }

  // Если данных нет более 3 секунд
  if (millis() - lastPacketTime > 3000) {
    drawBurnInProtection();
    delay(30); 
  }
}

void drawBurnInProtection() {
  display.clearDisplay();
  msgX += dx;
  msgY += dy;

  if (msgX <= 0 || msgX + msgW >= SCREEN_WIDTH) dx = -dx;
  if (msgY <= 0 || msgY + msgH >= SCREEN_HEIGHT) dy = -dy;

  display.drawRoundRect((int)msgX, (int)msgY, msgW, msgH, 4, WHITE);
  display.setCursor((int)msgX + 8, (int)msgY + 5);
  display.print(F("IDLE MODE"));
  display.display();
}

void drawStat(int x, int y, String label, int val, String suffix) {
  display.setTextSize(1);
  display.setCursor(x + 2, y + 10); 
  display.print(label);

  display.setTextSize(2);
  // Авто-смещение если число стало трехзначным (100%)
  int valueOffset = (val < 100) ? 28 : 22;
  display.setCursor(x + valueOffset, y + 4); 
  display.print(val);

  display.setTextSize(1);
  if (suffix == "C") {
    display.drawCircle(display.getCursorX() + 2, y + 5, 1, WHITE); // Рисуем кружочек градуса
    display.setCursor(display.getCursorX() + 5, y + 4);
  }
  display.print(suffix);
}

void drawUI() {
  display.clearDisplay();
  display.setTextColor(WHITE);

  // Разделительные линии
  display.drawFastVLine(63, 0, 64, WHITE); 
  display.drawFastHLine(0, 31, 128, WHITE); 

  drawStat(0, 0, "CPU", cpu, "%");
  drawStat(64, 0, "RAM", ram, "%");
  drawStat(0, 32, "GPU", gpu, "%");
  drawStat(64, 32, "TMP", gpuTemp, "C");

  display.display();
}