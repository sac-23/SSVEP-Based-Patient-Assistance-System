#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <base64.h>

// --- 1. Configuration: Define your LED pins ---

const int LED_FREQ_1 = 23;   // For 6.66 Hz
const int LED_FREQ_2 = 22;   // For 7.5 Hz
const int LED_FREQ_3 = 21;   // For 8.57 Hz
const int LED_FREQ_4 = 19;  // For 10.0 Hz
const int LED_FREQ_5 = 18;  // For 12.0 Hz

const int Buzzer = 4;
// Array to easily manage all LED pins
const int ledPins[] = {LED_FREQ_1, LED_FREQ_2, LED_FREQ_3, LED_FREQ_4, LED_FREQ_5};
const int numLeds = 5;

WiFiClient client;

const String account_sid = " "; // Account Sid
const String auth_token = " "; // Auth Token
const String twilio_phone_number = " ";
const String to_phone_number = " "; // Receipten Phone Number

const char *ssid = " "; // WiFi ssid
const char *password = " "; // WiFi Password

// --- 2. Setup Function (runs once) ---

void setup() {
  
  Serial.begin(115200); 
  
  WiFiSetup();

  pinMode(Buzzer, OUTPUT);
  digitalWrite(Buzzer, LOW);

  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW); // Turn all off
  }

  Serial.println("ESP32_Ready");
}

// --- 3. Main Loop ---

void loop() {

  if (Serial.available() > 0) {

    String incomingFrequency = Serial.readStringUntil('\n');
    incomingFrequency.trim();

    turnAllLedsOff();

    // --- 4. Process the Command ---

    if (incomingFrequency == "6.66") {
      triggerAction(LED_FREQ_1, "ALERT: Patient needs WATER.");
      Serial.println("Received data as 6.66");
      
    } 
    else if (incomingFrequency == "7.5") {
      triggerAction(LED_FREQ_2, "ALERT: Patient needs FOOD.");
      Serial.println("Received data as 7.5");
      
    }
    else if (incomingFrequency == "8.57") {
      triggerAction(LED_FREQ_3, "ALERT: Patient is in PAIN.");
      Serial.println("Received data as 8.57");

    } 
    else if (incomingFrequency == "10.0") {
      triggerAction(LED_FREQ_4, "ALERT: Patient needs to be REPOSITIONED.");
      Serial.println("Received data as 10.0"); 

    }
    else if (incomingFrequency == "12.0") {
      triggerAction(LED_FREQ_5, "ALERT: Patient needs HELP.");
      Serial.println("Received data as 12.0");
      digitalWrite(Buzzer, HIGH);
      delay(2000);
      digitalWrite(Buzzer, LOW);
      
    } 
    else {
      Serial.println("Received unknown command.");
    }
  }
}

// --- 5. Helper Functions ---

void triggerAction(int ledPin, String alertMessage) {
 
  Serial.println(alertMessage);
  sendSMS(alertMessage);
  
  digitalWrite(ledPin, HIGH);
  delay(3000); 
  digitalWrite(ledPin, LOW); 
  Serial.println("Action complete. Waiting for next command...");
}

void turnAllLedsOff() {
  for (int i = 0; i < numLeds; i++) {
    digitalWrite(ledPins[i], LOW);
  }
}

void sendSMS(String message) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;

        String url = "https://api.twilio.com/2010-04-01/Accounts/" + account_sid + "/Messages.json";
        String auth = account_sid + ":" + auth_token;
        String encoded_auth = base64::encode(auth);

        String postData = "To=" + to_phone_number + "&From=" + twilio_phone_number + "&Body=" + message;

        http.begin(url);
        http.addHeader("Authorization", "Basic " + encoded_auth);
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");

        int httpResponseCode = http.POST(postData);

        if (httpResponseCode > 0) {
            Serial.print("SMS Sent! Response Code: ");
            Serial.println(httpResponseCode);

            // <-- Notify Python script that SMS was sent
            Serial.println("PYTHON_ALERT:SMS_SENT");
        } else {
            Serial.print("Error sending SMS: ");
            Serial.println(http.errorToString(httpResponseCode));

            // Optional: notify Python script of failure
            Serial.println("PYTHON_ALERT:SMS_FAILED");
        }

        http.end();
    } else {
        Serial.println("WiFi not connected!");
        Serial.println("PYTHON_ALERT:SMS_FAILED");
    }
}

void WiFiSetup() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    Serial.print("Connecting to WiFi...");
    unsigned long startTime = millis();
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
        
        if (millis() - startTime > 20000) {  // Timeout after 20 seconds
            Serial.println("\nWiFi connection failed! Restarting...");
            ESP.restart();
        }
    }
    Serial.println("\nWiFi Connected!");
}