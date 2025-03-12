/* Four-pairs button LED version
 * 
 */
//unsigned long theTime;    // function as a stopwatch.
const int numButtons = 4; // Number of buttons and LEDs
int ButtonPins[numButtons] = {2, 4, 6, 8};  // Button Pin numbers
int LEDPins[numButtons] = {3, 5, 7, 9};     // LED Pin numbers

void setup() {
  // put your setup code here, to run once:
  for (int i = 0; i < numButtons; i++) {
    pinMode(ButtonPins[i], INPUT_PULLUP);  // Buttons as INPUT_PULLUP
    pinMode(LEDPins[i], OUTPUT);           // LEDs as OUTPUT
  }
    Serial.begin(9600);
}

void loop() {
  // SECTION 2: BUTTON LED CONTROL LOOP
  for (int i = 0; i < numButtons; i++) {
    handleButtonLED(i);
  }

  // SECTION 3: Create timestamp and print button & LED status
  //theTime = millis(); 
  //Serial.print(theTime);  // Print current time
  for (int i = 0; i < numButtons; i++) {
    Serial.print(" ");
    //Serial.print(digitalRead(ButtonPins[i]));  // Print button state
    //Serial.print(" ");
    Serial.print(digitalRead(LEDPins[i]));    // Print LED state
  }
    Serial.print(" ");
  Serial.println();
  delay(10);  
}

// Function to handle individual button and LED pair
void handleButtonLED(int index) {
  if (digitalRead(ButtonPins[index]) == LOW) {
    delay(80); // Debouncing delay
    if (digitalRead(ButtonPins[index]) == LOW) {
      digitalWrite(LEDPins[index], HIGH);  // Turn on LED
    }
  } else {
    digitalWrite(LEDPins[index], LOW);    // Turn off LED
  }
}

