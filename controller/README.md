# DSController

Barcode scanner and main controller for the deposit bin.

## Instructions (Linux)

### Setup

- Clone the repository `git clone https://github.com/tgrants/deposit-system`
- `cd deposit-system/controller`
- Create a virtual environment `python3 -m venv venv`
- Activate the virtual environment `source venv/bin/activate`
- Install all dependencies `pip install -r requirements.txt`
- Install tkinter (`apt install python3-tk` for Debian-derived distributions)
- Run `python3 main.py`

### Development environment

- Set up python interpreter (VSCode)
	- Get interpreter path `which python` (while in venv)
	- Set path `CTRL+SHIFT+P` -> `Python: Select interpreter`

## Options

- `-h --help` Display a list of all commands
- `-p --port` Set driver port. Defaults to ttyACM0.
- `-v --verbose` Print logs
- `-w --window` Show a window with cv2 output

## Resources
- https://www.geeksforgeeks.org/detect-and-read-barcodes-with-opencv-in-python/
