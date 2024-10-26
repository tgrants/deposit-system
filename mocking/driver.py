"""
The module simulates the driver.

Classes:
	SCPIParser: A class to manage SCPI commands and process incoming serial commands.

Functions:
	identify: Sends device identification information over the serial connection.
	led_on: Turns the LED on and provides a status message.
	led_off: Turns the LED off and provides a status message.
	setup: Sets up SCPI command registration and initializes the command structure.
	loop: Continuously listens for and processes serial input commands.

Command-line Arguments:
	-h --help: Displays a list of all commands
	-p, --port: Specify the port to connect to the mock serial driver.
	-b, --baudrate: Define the baud rate for the serial connection (default is 9600).
"""

# Standard
import time
from argparse import ArgumentParser, RawDescriptionHelpFormatter

# Third party
import serial


class SCPIParser:
	"""
	SCPIParser class to register and process SCPI commands.
	"""

	def __init__(self):
		"""
		Initialize the SCPIParser.
		"""
		self.commands = {}
		self.command_tree_base = ""

	def register_command(self, command, func):
		"""
		Register a SCPI command with a specific function.
		
		Args:
			command (str): The SCPI command to register.
			func (callable): The function to execute when the command is received.
		"""
		full_command = self.command_tree_base + command
		self.commands[full_command] = func

	def set_command_tree_base(self, base_command):
		"""
		Set the base command tree, which prefixes all registered commands.
		
		Args:
			base_command (str): The base command prefix for registered commands.
		"""
		self.command_tree_base = base_command

	def process_input(self, input_command):
		"""
		Process an incoming command and execute the associated function if registered.
		
		Args:
			input_command (str): The command received from the input.
		"""
		input_command = input_command.strip()
		if input_command in self.commands:
			self.commands[input_command]()
		else:
			print(f"Unknown command: {input_command}")


def identify():
	"""
	Send device identification information over serial.
	"""
	serial_conn.write("DSDevs,DSDriver,#00,mock_driver\n".encode())


def led_on():
	"""
	Turn on the builtin LED.
	"""
	global led_state
	led_state = "ON"
	print("LED is ON")


def led_off():
	"""
	Turn off the builtin LED.
	"""
	global led_state
	led_state = "OFF"
	print("LED is OFF")


def setup():
	"""
	Register SCPI commands and configure the command tree base.
	"""
	scpi.register_command("*IDN?", identify)
	scpi.set_command_tree_base("LED")
	scpi.register_command(":ON", led_on)
	scpi.register_command(":OFF", led_off)


def loop():
	"""
	Continuously read and process incoming serial commands.
	"""
	while True:
		if serial_conn.in_waiting > 0:
			input_command = serial_conn.readline().decode().strip()
			scpi.process_input(input_command)


parser = ArgumentParser(
	formatter_class = RawDescriptionHelpFormatter
)
parser.add_argument(
	"-p",
	"--port",
	action = "store",
	help = "mock driver port",
)
parser.add_argument(
	"-b",
	"--baudrate",
	action = "store",
	default = 9600,
	help = "port baudrate",
)
args = parser.parse_args()

led_state = "OFF"
scpi = SCPIParser()

port = args.port
baudrate = args.baudrate

serial_conn = serial.Serial(port, baudrate, timeout=1)
time.sleep(2)

try:
	setup()
	loop()
except KeyboardInterrupt:
	print("Exiting program...")
finally:
	serial_conn.close()
