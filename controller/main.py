import cv2
import datetime

import numpy as np

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pyzbar.pyzbar import decode


def main():
	# Parse arguments
	parser = ArgumentParser(
		formatter_class = RawDescriptionHelpFormatter
	)
	parser.add_argument(
		"--verbose",
		action="store_true",
		help = "print logs",
	)
	parser.add_argument(
		"--window",
		action="store_true",
		help = "show a window with cv2 output",
	)
	args = parser.parse_args()

	# Initialize webcam
	cap = cv2.VideoCapture(0) # Use 0 for default camera

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
