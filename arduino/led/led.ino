#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecureBearSSL.h>


#define WIFI_SSID ""
#define WIFI_PASS ""

WiFiClientSecure client;

HTTPClient httpClient;

LiquidCrystal_I2C lcd(0x27, 16, 2); // 16x2 LCD, I2C cím 0x27

void setup() {
  Serial.begin(115200);

  Wire.begin(D2, D1); // NodeMCU SDA (D2), SCL (D1)

  lcd.begin(16, 2); // például: 16 oszlop, 2 sor
  lcd.backlight();     // háttérvilágítás ON

  lcd.setCursor(0, 0);
  
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { 
    Serial.print(".");
    delay(100); 
  }
  lcd.print("wifi kapcsolodva");

  Serial.print("Connected! IP adress: ");
  Serial.println(WiFi.localIP());
  lcd.clear();
}

void loop() {
  String szoveg = adatOlvasas();
   lcd.print(szoveg);
  delay(2000);
  lcd.clear();
}




String adatOlvasas() {
  const char *URL = "https://centrum.1percprogramozas.hu/api/olvasas";

  client.setInsecure(); // SSL cert ellenőrzés kihagyása

  httpClient.begin(client, URL);
  httpClient.addHeader("Content-Type", "application/x-www-form-urlencoded");
  String content = "";
  int httpCode = httpClient.GET();
  if (httpCode > 0) {
    content = httpClient.getString();
    Serial.println("Tartalom:");
    Serial.println(content);
  } else {
    Serial.print("HTTP hiba: ");
    Serial.println(httpCode);
  }

  httpClient.end();
  return content;
}

 