"""
This module implements a barcode scanning system with a graphical user interface (GUI)
for real-time video feed display and barcode recognition, as well as communication
with a connected driver over serial.

Classes:
	SharedData: Manages shared data with thread-safe methods.
	Gui: Displays a GUI with video feed and provides interactive controls.

Functions:
	barcode_scanner: Continuously reads from the webcam, decodes barcodes, and updates shared data.
	driver_comm: Interfaces with a connected device to retrieve and display identity information.
	controller: Processes unique barcodes and performs actions on new detections.
	main: Initializes the application, starts threads, and launches the GUI.

Command-line Arguments:
	-h --help: Displays a list of all commands
	-p, --port: Specifies the serial port for driver communication.
	-v, --verbose: Enables detailed logging for debugging and insights.
	-w, --window: Enables an additional OpenCV window for debugging and visualization.
"""

# Standard
import datetime
import signal
import time
import threading
import tkinter
import queue
from tkinter import ttk
from argparse import ArgumentParser, RawDescriptionHelpFormatter

# Third party
import cv2
import numpy
import serial
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode


class SharedData:
	"""
	SharedData class for managing resources shared between threads.
	"""

	def __init__(self):
		"""
		Initialize SharedData.
		"""
		self.barcode_queue = queue.Queue()
		self.command_queue = queue.Queue()
		self.frame = None
		self.lock = threading.Lock()

	def add_barcode(self, data: str):
		"""
		Add barcode data to the barcode queue.
		
		Args:
			data (str): The barcode data to add.
		"""
		with self.lock:
			self.barcode_queue.put(data)

	def get_barcode(self) -> str:
		"""
		Retrieve barcode data from the queue, if available.
		
		Returns:
			str or None: The barcode data if available, otherwise None.
		"""
		try:
			return self.barcode_queue.get_nowait()
		except queue.Empty:
			return None

	def clear_barcodes(self):
		"""
		Clear all barcode data from the queue.
		"""
		self.barcode_queue.queue.clear()

	def set_frame(self, frame: cv2.typing.MatLike):
		"""
		Set the current video frame.
		
		Args:
			frame (cv2.typing.MatLike): The frame to store.
		"""
		self.frame = frame

	def get_frame(self) -> cv2.typing.MatLike:
		"""
		Retrieve the current video frame.
		
		Returns:
			MatLike: The stored video frame.
		"""
		return self.frame


class Gui:
	"""
	Gui class to manage the graphical user interface (GUI) for the Deposit system,
	displaying video feed and responding to user input.
	"""

	def __init__(self, root, shared_data):
		"""
		Initialize the graphical user inteface.
		
		Args:
			root (tkinter.Tk): The root Tkinter window.
			shared_data (SharedData): The shared data instance.
		"""
		self.root = root
		self.shared_data = shared_data
		self.root.title("Deposit system")
		self.label = ttk.Label(root, text="Label :)")
		self.label.pack(pady=10)
		self.video_label = ttk.Label(root)
		self.video_label.pack()
		root.bind("<space>", self.space_pressed)

		self.current_image = None
		self.video_thread = threading.Thread(target=self.update_video_feed)
		self.video_thread.daemon = True
		self.video_thread.start()

	def space_pressed(self, event):
		"""
		Handle the spacebar press event.
		
		Args:
			event (tkinter.Event): The key press event.
		"""
		print("Space pressed")

	def update_video_feed(self):
		"""
		Update the video feed in the GUI using frames from SharedData.
		"""
		while True:
			frame = self.shared_data.get_frame()
			if frame is None:
				continue
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			img = Image.fromarray(frame)
			imgtk = ImageTk.PhotoImage(image=img)
			self.current_image = imgtk
			self.video_label.config(image=imgtk)
			self.video_label.imgtk = imgtk
			self.root.after(50)


def barcode_scanner(args, shared_data, stop_event):
	"""
	Initialize the webcam and continuously scan for barcodes, updating shared data with decoded results.
	
	Args:
		args (Namespace): Parsed command-line arguments.
		shared_data (SharedData): The shared data instance.
		stop_event (threading.Event): Event to signal when to stop the scanner.
	"""
	print("Starting barcode scanner")

	# Initialize webcam
	cap = cv2.VideoCapture(0) # Use 0 for the default camera

	try:
		while not stop_event.is_set():  # Main loop
			# Capture frame-by-frame
			ret, frame = cap.read()

			# Save frame in SharedData
			if ret:
				shared_data.set_frame(frame)

			# Decode barcodes in the frame
			barcodes = decode(frame)

			# Loop through detected barcodes
			for barcode in barcodes:
				barcode_data = barcode.data.decode('utf-8')
				barcode_type = barcode.type

				if args.verbose:
					print(f"Barcode: {barcode_data} | Type: {barcode_type} | Time: {datetime.datetime.now()}")

				if args.window:
					# Draw a rectangle around the barcode
					points = barcode.polygon
					if len(points) == 4:
						pts = [(p.x, p.y) for p in points]
						cv2.polylines(frame, [numpy.array(pts, numpy.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

					# Display the barcode data on the frame
					cv2.putText(
						frame,
						barcode_data,
						(barcode.rect.left, barcode.rect.top - 10),
						cv2.FONT_HERSHEY_SIMPLEX,
						0.5,
						(255, 0, 0),
						2
					)

				# Add barcode to queue
				shared_data.add_barcode(barcode_data)

			if args.window:
				cv2.imshow('Barcode Scanner', frame)

				if cv2.waitKey(1) & 0xFF == ord('q'):
					break

	finally:
		# Release the webcam and close all windows
		cap.release()
		cv2.destroyAllWindows()
		print("Stopping barcode scanner")


def driver_comm(args, shared_data: SharedData, stop_event):
	"""
	Communicate with the driver.
	
	Args:
		args (Namespace): Parsed command-line arguments.
		shared_data (SharedData): The shared data instance.
		stop_event (threading.Event): Event to signal when to stop driver communication.
	"""
	q_list = [ # Query list
		"*IDN?",
		"*OPC?",
		"MEAS:DIST?"
	]
	c_list = [ # Command list
		"LED:ON",
		"LED:OFF",
		"LOCK:ON",
		"LOCK:OFF",
	]
	print("Starting driver comm")
	# Connect to the driver
	ser = serial.Serial(args.port, 9600)
	time.sleep(2)
	ser.write("*IDN?\n".encode())
	while not stop_event.is_set():
		time.sleep(0.01)
		if ser.in_waiting > 0:
			response = ser.readline().decode().strip()
			print("Identity:", response)
			break
	while not stop_event.is_set():
		if shared_data.command_queue.empty():
			time.sleep(0.01)
			continue
		cmd = shared_data.command_queue.get_nowait()
		if cmd in q_list:
			ser.write(cmd.encode())
		elif cmd in c_list:
			ser.write(cmd.encode())
			ser.write("*OPC?".encode())
		else:
			print("Command not recognized")
			continue
		while not stop_event.is_set():
			time.sleep(0.01)
			if ser.in_waiting > 0:
				response = ser.readline().decode().strip()
				print(response)
				break
	print("Stopping driver comm")


def controller(args, shared_data, stop_event):
	"""
	Main controller loop to process unique barcodes.
	
	Args:
		args (Namespace): Parsed command-line arguments.
		shared_data (SharedData): The shared data instance.
		stop_event (threading.Event): Event to signal when to stop the controller.
	"""
	print("Starting main controller")
	barcode_list = [] # List of all unique scanned barcodes
	while not stop_event.is_set():
		barcode_data = shared_data.get_barcode()
		if barcode_data is None:
			time.sleep(0.05)
			continue
		if barcode_data in barcode_list:
			time.sleep(0.05)
			continue
		if args.verbose:
			print("Unique barcode!")
		barcode_list.append(barcode_data)
		shared_data.clear_barcodes()
	print("Stopping main controller")


def console_input(args, shared_data: SharedData, stop_event):
	"""
	Reads input from the console and adds it to the command queue.

	Args:
		args (Namespace): Parsed command-line arguments.
		shared_data (SharedData): The shared data instance.
		stop_event (threading.Event): Event to signal when to stop listening for input.
	"""
	print("Starting console input thread")
	while not stop_event.is_set():
		# Read input from the console
		user_input = input()
		if user_input:
			shared_data.command_queue.put(user_input)
	print("Stopping console input thread")


def main():
	"""
	Parse arguments, initialize shared data, start threads for barcode scanning,
	driver communication, and control, and launch the GUI.
	"""
	# Parse arguments
	parser = ArgumentParser(
		formatter_class = RawDescriptionHelpFormatter
	)
	parser.add_argument(
		"-p",
		"--port",
		action="store",
		default="/dev/ttyACM0",
		help = "driver port",
	)
	parser.add_argument(
		"-v",
		"--verbose",
		action="store_true",
		help = "print logs",
	)
	parser.add_argument(
		"-w",
		"--window",
		action="store_true",
		help = "show a window with cv2 output",
	)
	args = parser.parse_args()

	shared_data = SharedData()

	stop_event = threading.Event()
	def signal_handler():
		stop_event.set()
	signal.signal(signal.SIGINT, signal_handler)

	barcode_thread = threading.Thread(target=barcode_scanner, args=(args, shared_data, stop_event))
	driver_thread = threading.Thread(target=driver_comm, args=(args, shared_data, stop_event))
	controller_thread = threading.Thread(target=controller, args=(args, shared_data, stop_event))
	console_input_thread = threading.Thread(target=console_input, args=(args, shared_data, stop_event))

	barcode_thread.start()
	driver_thread.start()
	controller_thread.start()
	console_input_thread.start()

	root = tkinter.Tk()
	Gui(root, shared_data)

	def on_closing():
		stop_event.set()
		barcode_thread.join()
		driver_thread.join()
		controller_thread.join()
		root.destroy()
	root.protocol("WM_DELETE_WINDOW", on_closing)

	root.mainloop()


if __name__ == "__main__":
	main()
