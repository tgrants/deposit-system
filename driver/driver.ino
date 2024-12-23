#include "Arduino.h"
#include <EEPROM.h>
#include <Stepper.h>
#include <Vrekrer_scpi_parser.h>

// Motor
const int dirPin = 8;
const int stepPin = 9;
const int stepsPerRevolution = 200;
Stepper stepper(stepsPerRevolution, dirPin, stepPin);
long stepDelay = 1000;

// Ultrasonic sensor
const int trigPin = 5;
const int echoPin = 6;

// Serial
#define BAUD 9600

// State
const int lockPositionAddress = 0;
const int lockLockedPosition = 800;
int lockPosition = 0;

// SCPI
SCPI_Parser scpi;

/* void setup()
 * Function setup()
 *   initializes serial communication, sets up the SCPI parser, and retrieves
 *   the saved motor position from EEPROM.
 */
void setup() {
	scpi.RegisterCommand("*IDN?", &identify);
	scpi.RegisterCommand("*OPC?", &operationComplete);
	scpi.SetCommandTreeBase(F("LED"));
		scpi.RegisterCommand(F(":ON"), &ledOn);
		scpi.RegisterCommand(F(":OFF"), &ledOff);
	scpi.SetCommandTreeBase(F("LOCK"));
		scpi.RegisterCommand(F(":ON"), &lockOn);
		scpi.RegisterCommand(F(":OFF"), &lockOff);
	scpi.SetCommandTreeBase(F("MEASure"));
		scpi.RegisterCommand(F(":DISTance?"), &measureDistance);
 
	Serial.begin(BAUD);
	pinMode(LED_BUILTIN, OUTPUT);
	pinMode(dirPin, OUTPUT);
	pinMode(stepPin, OUTPUT);
	pinMode(trigPin, OUTPUT);
	pinMode(echoPin, INPUT);
	EEPROM.get(lockPositionAddress, lockPosition);
}

/* void loop()
 * Function loop()
 *   checks for available serial input and processes SCPI commands.
 */
void loop() {
	if (Serial.available()) {
		scpi.ProcessInput(Serial, "\n");
	}
}

/* void pause(long ms)
 * Function pause(ms)
 *   delays the program by ms milliseconds.
 */
void pause(long ms) {
	delay(ms / 1000);
	delayMicroseconds(ms % 1000);
}

/* void moveMotor(int steps, int dir)
 * function moveMotor(steps, dir)
 *   Turns the stepper motor by the specified number of steps in the given
 *   direction dir. Updates lock position and stores it in EEPROM.
 */
void moveMotor(int steps, int dir) {
	for (int i = 0; i < steps; ++i) {
		stepper.step(dir);
		lockPosition += dir;
		pause(stepDelay);
	}
	EEPROM.put(lockPositionAddress, lockPosition);
}

/* int getDistance()
 * Function getDistance()
 *   returns the distance to an object in cm as an integer using an ultrasonic
 *   sensor.
 */
int getDistance() {
	// Clear trigPin
	digitalWrite(trigPin, LOW);
	delayMicroseconds(2);
	// Set trigPin to HIGH for 10 µs
	digitalWrite(trigPin, HIGH);
	delayMicroseconds(10);
	digitalWrite(trigPin, LOW);
	// Read echoPin, return sound wave travel time in µs
	long duration = pulseIn(echoPin, HIGH);
	return duration * 0.034 / 2; // Return distance, cm
}

/* void identify(SCPI_C commands, SCPI_P parameters, Stream& interface)
 * Function identify(commands, parameters, interface)
 *   responds to the SCPI *IDN? query by sending device identification
 *   information back over the interface.
 */
void identify(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	interface.println(F("DSDevs,DSDriver,#00," VREKRER_SCPI_VERSION));
	//*IDN? Suggested return string should be in the following format:
	// "<vendor>,<model>,<serial number>,<firmware>"
}

/* void operationComplete(SCPI_C commands, SCPI_P parameters, Stream& interface)
 * Function operationComplete(commands, parameters, interface)
 *   responds to the SCPI *OPC? query by sending 1 back over the interface after
 *   a command has been completed.
 */
void operationComplete(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	interface.println(1); // Always return 1 because the execution is concurrent
}

/* void ledOn(SCPI_C commands, SCPI_P parameters, Stream& interface)
 * Function ledOn(commands, parameters, interface)
 *   turns on the built-in LED in response to the SCPI LED:ON command.
 */
void ledOn(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	digitalWrite(LED_BUILTIN, HIGH);
}

/* void ledOff(SCPI_C commands, SCPI_P parameters, Stream& interface)
 * Function ledOff(commands, parameters, interface)
 *   turns off the built-in LED in response to the SCPI LED:OFF command.
 */
void ledOff(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	digitalWrite(LED_BUILTIN, LOW);
}

/* void lockOn(SCPI_C commands, SCPI_P parameters, Stream& interface)
 * Function lockOn(commands, parameters, interface)
 *   moves the motor to the locked position using the SCPI LOCK:ON command.
 */
void lockOn(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	moveMotor(lockLockedPosition - lockPosition, 1);
}

/* void lockOff(SCPI_C commands, SCPI_P parameters, Stream& interface)
 * Function lockOff(commands, parameters, interface)
 *   moves the motor to the unlocked position using the SCPI LOCK:OFF command.
 */
void lockOff(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	moveMotor(lockPosition, -1);
}

/* void measureDistance(SCPI_C commands, SCPI_P parameters, Stream& interface)
 * Function measureDistance(commands, parameters, interface)
 *   responds to the SCPI MEASure:DISTance? command by measuring and sending
 *   the distance to the nearest object using the interface.
 */
void measureDistance(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	interface.println(getDistance());
}
