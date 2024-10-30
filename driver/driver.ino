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

// Serial
#define BAUD 9600

// State
const int lockPositionAddress = 0;
const int lockLockedPosition = 800;
int lockPosition = 0;

// SCPI
SCPI_Parser scpi;

void setup() {
	scpi.RegisterCommand("*IDN?", &identify);
	scpi.SetCommandTreeBase(F("LED"));
		scpi.RegisterCommand(F(":ON"), &ledOn);
		scpi.RegisterCommand(F(":OFF"), &ledOff);
	scpi.SetCommandTreeBase(F("LOCK"));
		scpi.RegisterCommand(F(":ON"), &lockOn);
		scpi.RegisterCommand(F(":OFF"), &lockOff);
 
	Serial.begin(BAUD);
	pinMode(LED_BUILTIN, OUTPUT);
	EEPROM.get(lockPositionAddress, lockPosition);
}

void loop() {
	if (Serial.available()) {
		scpi.ProcessInput(Serial, "\n");
	}
}

void pause(long ms) {
	delay(ms / 1000);
	delayMicroseconds(ms % 1000);
}

void moveMotor(int steps, int dir) {
	for (int i = 0; i < steps; ++i) {
		stepper.step(dir);
		lockPosition += dir;
		pause(stepDelay);
	}
	EEPROM.put(lockPositionAddress, lockPosition);
}

void identify(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	interface.println(F("DSDevs,DSDriver,#00," VREKRER_SCPI_VERSION));
	//*IDN? Suggested return string should be in the following format:
	// "<vendor>,<model>,<serial number>,<firmware>"
}

void ledOn(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	digitalWrite(LED_BUILTIN, HIGH);
}

void ledOff(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	digitalWrite(LED_BUILTIN, LOW);
}

void lockOn(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	moveMotor(lockLockedPosition - lockPosition, 1);
}

void lockOff(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	moveMotor(lockPosition, -1);
}
