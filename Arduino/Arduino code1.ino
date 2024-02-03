#include <Servo.h>
#include <Wire.h>
#include "paj7620.h" // Ensure the correct capitalization

#define GES_REACTION_TIME 500
#define GES_ENTRY_TIME 800
#define GES_QUIT_TIME 1000

bool faceDetected = false;
bool gestureDetected = false;
int ledPin = 13;      // Pin for the LED
int servoPin = 9;     // Change to an available PWM pin for the servo motor
Servo myServo;         // Create a servo object

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  myServo.attach(servoPin);
  
  uint8_t error = paj7620Init();
  
  if (error) {
    Serial.print("INIT ERROR, CODE:");
    Serial.println(error);
  } else {
    Serial.println("INIT OK");
  }
  Serial.println("Please input your gestures:\n");
}

void loop() {
  if (Serial.available() > 0) {
    char signal = Serial.read();

    if (signal == '1') {
      faceDetected = true;
    } else if (signal == '0') {
      faceDetected = false;
    }
    
    uint8_t data = 0, error;
    error = paj7620ReadReg(0x43, 1, &data);

    if (!error) {
      handleGesture(data);
      delay(GES_QUIT_TIME);
    }

    if (faceDetected && gestureDetected) {
      digitalWrite(ledPin, HIGH);
      myServo.write(90); // Rotate servo by 90 degrees
      delay(5000);       // Add a 5-second delay for the servo
      myServo.write(0);  // Rotate servo back to 0 degrees
      gestureDetected = false; // Reset the gesture flag
    } else {
      digitalWrite(ledPin, LOW);
    }
  }
}

void handleGesture(int gesture) {
  switch (gesture) {
    case GES_RIGHT_FLAG:
    case GES_LEFT_FLAG:
    case GES_UP_FLAG:
    case GES_DOWN_FLAG:
    case GES_FORWARD_FLAG:
    case GES_BACKWARD_FLAG:
      gestureDetected = true;
      break;
    default:
      gestureDetected = false;
      break;
  }
}
