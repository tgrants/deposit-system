import cv2
import datetime
import serial
import signal
import threading
import time
import queue

import numpy as np

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pyzbar.pyzbar import decode


def barcode_scanner(args, barcode_queue, stop_event):
	print("Starting barcode scanner")

	# Initialize webcam
	cap = cv2.VideoCapture(0) # Use 0 for the default camera

	try:
		while not stop_event.is_set():  # Main loop
			# Capture frame-by-frame
			ret, frame = cap.read()

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
				barcode_queue.put(barcode_data)

			if args.window:
				cv2.imshow('Barcode Scanner', frame)

				if cv2.waitKey(1) & 0xFF == ord('q'):
					break

	finally:
		# Release the webcam and close all windows
		cap.release()
		cv2.destroyAllWindows()
		print("Stopping barcode scanner")


def driver_comm(args, stop_event):
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


def interface_comm(args, stop_event):
	print("Starting interface comm")
	while not stop_event.is_set():
		time.sleep(1)
	print("Stopping interface comm")


def controller(args, barcode_queue, stop_event):
	print("Starting main controller")
	barcode_list = [] # List of all unique scanned barcodes
	while not stop_event.is_set():
		if barcode_queue.empty():
			time.sleep(0.05)
			continue
		barcode_data = barcode_queue.get()
		if barcode_data in barcode_list:
			time.sleep(0.05)
			continue
		if args.verbose:
			print("Unique barcode!")
		barcode_list.append(barcode_data)
		barcode_queue.queue.clear()
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

	barcode_queue = queue.Queue()

	stop_event = threading.Event()
	def signal_handler(signum, frame):
		stop_event.set()
	signal.signal(signal.SIGINT, signal_handler)

	barcode_thread = threading.Thread(target=barcode_scanner, args=(args, barcode_queue, stop_event))
	driver_thread = threading.Thread(target=driver_comm, args=(args, stop_event))
	interface_thread = threading.Thread(target=interface_comm, args=(args, stop_event))
	controller_thread = threading.Thread(target=controller, args=(args, barcode_queue, stop_event))

	barcode_thread.start()
	driver_thread.start()
	interface_thread.start()
	controller_thread.start()

	barcode_thread.join()
	driver_thread.join()
	interface_thread.join()
	controller_thread.join()


if __name__ == "__main__":
	main()
