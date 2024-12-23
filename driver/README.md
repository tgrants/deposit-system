# DSDriver

Controller for the physical components of the deposit bin.

## Controls

- `*IDN?` - Indetify device
- `*OPC?` - Return 1 if there are no pending operations
- `LED` - Control the builtin LED
	- `:ON` - Toggle ON
	- `:OFF` - Toggle OFF
- `LOCK` - Control the lock (motor)
	- `:ON` - move motor until locked
	- `:OFF` - move motor until unlocked
- `MEAS` - Measure using ultrasonic sensor
	- `:DIST?` - Distance

### Examples

## Resources

- https://wiki.archlinux.org/title/Arduino
- https://github.com/arduino-libraries/Stepper/
- https://github.com/Vrekrer/Vrekrer_scpi_parser
- https://howtomechatronics.com/tutorials/arduino/ultrasonic-sensor-hc-sr04/
