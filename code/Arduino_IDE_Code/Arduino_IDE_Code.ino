#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <Adafruit_BMP085_U.h>
#include <Adafruit_Sensor.h>

// Pin definitions
#define LDR 4
#define TH 5  
#define Rain 36
#define Soil 34
#define MOTOR 14      // D14 = GPIO 14 on ESP32
#define D27_PIN 27    // D27 pin for motor driver control

bool awaitingResponse = false;
bool motorActive = false;
unsigned long motorStartTime = 0;

// LCD
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Sensors
Adafruit_BMP085_Unified bmp = Adafruit_BMP085_Unified(10085);
DHT dht(TH, DHT11);

// Sensor values
float temp = 0, humidity = 0, pressureVal = 0, rainMM = 0, soilMM = 0;

// LDR tracking
int prevLDRState = -1;

// LCD display state
int displayState = 0;
unsigned long lastDisplayChange = 0;

void setup() {
  Serial.begin(115200);
  lcd.begin();
  lcd.backlight();

  if (!bmp.begin()) {
    lcd.setCursor(0, 0);
    lcd.print("BMP180 FAIL");
    while (1);
  }

  dht.begin();

  pinMode(LDR, INPUT);
  pinMode(Rain, INPUT);
  pinMode(Soil, INPUT);
  pinMode(MOTOR, OUTPUT);
  pinMode(D27_PIN, OUTPUT);  // ✅ FIX: Set D27 as OUTPUT to control motor driver
  analogReadResolution(12);

  lcd.setCursor(0, 0);
  lcd.print("System Starting");
  delay(2000);
  lcd.clear();

  prevLDRState = digitalRead(LDR);
}

void loop() {
  unsigned long currentMillis = millis();

  // 🌙 LDR CHANGE DETECTION
  int currentLDRState = digitalRead(LDR);
  if (currentLDRState != prevLDRState) {
    prevLDRState = currentLDRState;

    // 📡 Send JSON to PC only on LDR change
    Serial.print("{\"temp\":");
    Serial.print(temp);
    Serial.print(",\"humidity\":");
    Serial.print(humidity);
    Serial.print(",\"pressure\":");
    Serial.print(pressureVal);
    Serial.print(",\"windspeed\":");
    Serial.print(2.5);
    Serial.print(",\"winddir\":");
    Serial.print(180);
    Serial.print(",\"dew\":");
    Serial.print(23.4);
    Serial.print(",\"cloudcover\":");
    Serial.print(60);
    Serial.print(",\"visibility\":");
    Serial.print(2.8);
    Serial.println("}");

    awaitingResponse = true;
  }

  // ✅ Update sensor values every second
  static unsigned long lastSensorRead = 0;
  if (currentMillis - lastSensorRead >= 1000) {
    lastSensorRead = currentMillis;

    humidity = dht.readHumidity();
    temp = dht.readTemperature();
    if (isnan(humidity) || isnan(temp)) {
      lcd.setCursor(0, 1);
      lcd.print("DHT Read Fail");
    }

    int rainRaw = analogRead(Rain);
    float rainPct = map(rainRaw, 0, 4095, 0, 100);
    rainMM = (100 - rainPct) * 0.5;

    int soilRaw = analogRead(Soil);
    soilMM = map(soilRaw, 0, 4095, 0, 50);

    sensors_event_t event;
    bmp.getEvent(&event);
    if (event.pressure) {
      pressureVal = event.pressure;
    }
  }

  // 📺 LCD Display Update
  if (currentMillis - lastDisplayChange >= 3000) {
    lastDisplayChange = currentMillis;

    lcd.setCursor(0, 0);
    lcd.print("Device: ON ");

    lcd.setCursor(0, 1);
    switch (displayState) {
      case 0:
        lcd.print("T:");
        lcd.print(temp, 1);
        lcd.print(" H:");
        lcd.print(humidity, 1);
        lcd.print("%  ");
        break;
      case 1:
        lcd.print("Rain:");
        lcd.print(rainMM, 1);
        lcd.print("mm     ");
        break;
      case 2:
        lcd.print("Press:");
        lcd.print(pressureVal, 0);
        lcd.print("hPa   ");
        break;
      case 3:
        lcd.print("Soil:");
        lcd.print(soilMM, 1);
        lcd.print("mm     ");
        break;
    }

    displayState = (displayState + 1) % 4;
  }

  // 📥 Handle Python Response
  if (Serial.available() > 0 && awaitingResponse) {
    int received = Serial.parseInt(); // 0 or 1
    if (received == 1) {
      digitalWrite(MOTOR, HIGH);     // Turn on motor (D14)
      digitalWrite(D27_PIN, HIGH);   // Also turn on motor driver via D27
      motorStartTime = millis();
      motorActive = true;
    } else {
      digitalWrite(MOTOR, LOW);      // Turn off motor
      digitalWrite(D27_PIN, LOW);
      motorActive = false;
    }
    awaitingResponse = false;
  }

  // ⏱ Stop motor after 5 seconds
  if (motorActive && (millis() - motorStartTime >= 5000)) {
    digitalWrite(MOTOR, LOW);
    digitalWrite(D27_PIN, LOW);
    motorActive = false;
  }

  // 🔄 Synchronize D27 with MOTOR pin (if still active)
  if (motorActive) {
    int motorState = digitalRead(MOTOR);
    digitalWrite(D27_PIN, motorState);
  }
}

