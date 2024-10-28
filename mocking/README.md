# driver.py

This script mocks the driver - useful for when you don't have an arduino with all of the components at home.

## Controls

See [`driver/README.md`](../driver/README.md).

## Instructions

See [`docs/setup.md`](../docs/setup.md) for instructions to set up the working environment.

### Linux

Create and connect 2 virtual ports with socat: `socat -d -d pty,raw,echo=0 pty,raw,echo=0`.
This will output something like:
```
2024/10/21 12:00:00 socat[12345] N PTY is /dev/pts/5
2024/10/21 12:00:00 socat[12345] N PTY is /dev/pts/6
2024/10/21 12:00:00 socat[12345] N starting data transfer loop with FDs [5,5] and [6,6]
```
In this case, `/dev/pts/5` and `/dev/pts/6` are the two virtual ports. Any data written to one of these ports will be available for reading on the other.
Run the mock driver and controller with one of these ports each: `python3 mocking/driver.py -p '/dev/pts/5'` and `python3 controller/main.py -p '/dev/pts/6'`

### Windows

Install [com0com](https://com0com.sourceforge.net/) and set it up. See the [documentation](https://com0com.sourceforge.net/doc/UsingCom0com.pdf).
Create a port twin: `install Portname=COM10 Portname=COM11`.
Run the mock driver and controller with one of these ports each: `python driver.py -p COM10` and `python3 main.py -p COM11`

### State

The current state of the virtual bin is saved in `state.json`. It will be created automatically.
It is recommended to delete this file after every update to ensure no values are missing.

## Options

- `-h --help` Display a list of all commands
- `-b --baudrate` Set port baudrate. Defaults to `9600`
- `-f --filename` Set. Defaults to `state.json`
- `-p --port` Set port
