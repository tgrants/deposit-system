import cv2
import datetime
import serial
import signal
import threading
import time
import tkinter
import queue

import numpy as np

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
from tkinter import ttk


class SharedData:
	def __init__(self):
		self.barcode_queue = queue.Queue()
		self.frame = None
		self.lock = threading.Lock()
	
	def add_barcode(self, data):
		with self.lock:
			self.barcode_queue.put(data)

	def get_barcode(self):
		try:
			return self.barcode_queue.get_nowait()
		except queue.Empty:
			return None
	
	def clear_barcodes(self):
		self.barcode_queue.queue.clear()

	def set_frame(self, frame):
		self.frame = frame

	def get_frame(self):
		return self.frame


class Gui:
	def __init__(self, root, shared_data):
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
		print("Space pressed")

	def update_video_feed(self):
		while True:
			frame = self.shared_data.get_frame()
			if frame is None: continue
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			img = Image.fromarray(frame)
			imgtk = ImageTk.PhotoImage(image=img)
			self.current_image = imgtk
			self.video_label.config(image=imgtk)
			self.video_label.imgtk = imgtk
			self.root.after(50)


def barcode_scanner(args, shared_data, stop_event):
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
						cv2.polylines(frame, [np.array(pts, np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

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


def driver_comm(args, shared_data, stop_event):
	print("Starting driver comm")

	# Connect to the driver
	ser = serial.Serial(args.port, 9600)
	time.sleep(2)
	ser.write("*IDN?\n".encode())
	while not stop_event.is_set():
		if ser.in_waiting > 0:
			response = ser.readline().decode().strip()
			print("Identity:", response)
			break

	print("Stopping driver comm")
	return


def controller(args, shared_data, stop_event):
	print("Starting main controller")
	barcode_list = [] # List of all unique scanned barcodes
	while not stop_event.is_set():
		barcode_data = shared_data.get_barcode()
		if barcode_data == None:
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


def main():
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
	def signal_handler(signum, frame):
		stop_event.set()
	signal.signal(signal.SIGINT, signal_handler)

	barcode_thread = threading.Thread(target=barcode_scanner, args=(args, shared_data, stop_event))
	driver_thread = threading.Thread(target=driver_comm, args=(args, shared_data, stop_event))
	controller_thread = threading.Thread(target=controller, args=(args, shared_data, stop_event))

	barcode_thread.start()
	driver_thread.start()
	controller_thread.start()

	root = tkinter.Tk()
	gui = Gui(root, shared_data)

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
