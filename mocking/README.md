# driver.py

This script mocks the driver.

## Controls

See `driver/driver.ino`.

## Instructions

### Linux

See `controller/README.md` for instructions to set up the working environment.
Create and connect 2 virtual ports with socat: `socat -d -d pty,raw,echo=0 pty,raw,echo=0`.
This will output something like:
```
2024/10/21 12:00:00 socat[12345] N PTY is /dev/pts/5
2024/10/21 12:00:00 socat[12345] N PTY is /dev/pts/6
2024/10/21 12:00:00 socat[12345] N starting data transfer loop with FDs [5,5] and [6,6]
```
In this case, `/dev/pts/5` and `/dev/pts/6` are the two virtual ports. Any data written to one of these ports will be available for reading on the other.
Run the mock driver and controller with one of these ports each: `python3 driver.py -p '/dev/pts/6'` and `python3 main.py -p '/dev/pts/6'`

### Windows

Install [com0com](https://com0com.sourceforge.net/) and set it up. See the [documentation](https://com0com.sourceforge.net/doc/UsingCom0com.pdf).
Create a port twin: `install Portname=COM10 Portname=COM11`.
Run the mock driver and controller with one of these ports each: `python driver.py -p COM10` and `python3 main.py -p COM11`

## Options

- `-h --help` Display a list of all commands
- `-b --baudrate` Set port baudrate. Defaults to 9600
- `-p --port` Set port
