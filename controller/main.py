import cv2
import datetime
import serial
import time

import numpy as np

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pyzbar.pyzbar import decode


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

	# Initialize webcam
	cap = cv2.VideoCapture(0) # Use 0 for default camera

	# Connect to the driver
	ser = serial.Serial(args.port, 9600)
	time.sleep(2)
	ser.write("*IDN?\n".encode())
	while True:
		if ser.in_waiting > 0:
			response = ser.readline().decode().strip()
			print("Identity:", response)
			break

	# List of scanned barcodes
	barcode_list = []

	try:
		print("Starting")
		while True: # Main loop
			# Capture frame-by-frame
			ret, frame = cap.read()

			# Decode barcodes in the frame
			barcodes = decode(frame)

			# Loop through detected barcodes
			for barcode in barcodes:
				# Extract the barcode data and type
				barcode_data = barcode.data.decode('utf-8')
				barcode_type = barcode.type

				if args.verbose:
					# Print barcode data and type
					print(f"Barcode: {barcode_data} | Type: {barcode_type} | Time: {datetime.datetime.now()}")

				if args.window:
					# Draw a rectangle around the barcode
					points = barcode.polygon
					if len(points) == 4:  # Ensure the barcode has 4 points
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

				# Save barcode
				if barcode_data in barcode_list:
					# Barcode already registered
					if args.verbose:
						print("Barcode already registered")
				else:
					barcode_list.append(barcode_data)

			if args.window:
				# Display the frame
				cv2.imshow('Barcode Scanner', frame)

				# Check if 'q' has been pressed
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break

	except KeyboardInterrupt:
		print("Exiting")
	
	finally:
		# Release the webcam and close all windows
		cap.release()
		cv2.destroyAllWindows()


if __name__ == "__main__":
	main()
