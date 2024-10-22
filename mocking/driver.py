import serial
import time

from argparse import ArgumentParser, RawDescriptionHelpFormatter


class SCPI_Parser:
	def __init__(self):
		self.commands = {}
		self.command_tree_base = ""

	def RegisterCommand(self, command, func):
		full_command = self.command_tree_base + command
		self.commands[full_command] = func

	def SetCommandTreeBase(self, base_command):
		self.command_tree_base = base_command

	def ProcessInput(self, input_command):
		input_command = input_command.strip()
		if input_command in self.commands:
			self.commands[input_command]()
		else:
			print(f"Unknown command: {input_command}")


def identify():
	serial_conn.write("DSDevs,DSDriver,#00,mock_driver\n".encode())


def ledOn():
	global led_state
	led_state = "ON"
	print("LED is ON")


def ledOff():
	global led_state
	led_state = "OFF"
	print("LED is OFF")


def setup():
	scpi.RegisterCommand("*IDN?", identify)
	scpi.SetCommandTreeBase("LED")
	scpi.RegisterCommand(":ON", ledOn)
	scpi.RegisterCommand(":OFF", ledOff)


def loop():
	while True:
		if serial_conn.in_waiting > 0:
			input_command = serial_conn.readline().decode().strip()
			scpi.ProcessInput(input_command)


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
scpi = SCPI_Parser()

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
