#include "Arduino.h"
#include <Vrekrer_scpi_parser.h>

SCPI_Parser scpi;

const int ledPin = LED_BUILTIN;

void setup() {
	scpi.RegisterCommand("*IDN?", &identify);
	scpi.SetCommandTreeBase(F("LED"));
		scpi.RegisterCommand(F(":ON"), &ledOn);
		scpi.RegisterCommand(F(":OFF"), &ledOff);
 
	Serial.begin(9600);
	pinMode(ledPin, OUTPUT);
}

void loop() {
	if (Serial.available()) {
		scpi.ProcessInput(Serial, "\n");
	}
}

void identify(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	interface.println(F("DSDevs,DSDriver,#00," VREKRER_SCPI_VERSION));
	//*IDN? Suggested return string should be in the following format:
	// "<vendor>,<model>,<serial number>,<firmware>"
}

void ledOn(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	digitalWrite(ledPin, HIGH);
}

void ledOff(SCPI_C commands, SCPI_P parameters, Stream& interface) {
	digitalWrite(ledPin, LOW);
}
