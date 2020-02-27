# PyPSXSerial
###### requirements: python >= 3.6, pyserial, 3-wire serial cable for psx, receiver software (psx-side)
A poorly-written implementation of playstation serial upload capability via psxserial / unirom / etc.
This checks nothing, will gladly send your grandmother through the serial port, and will fail with a whimper.

### Tested with:
- Interpreter: python3.6
- OS: macOS, linux, windows
- Hardware: pl2303 (configured for 3.3v) and a 3-wire GND/TXD/RXD interface to PSX serial port
- PSX-side receiver: psxserial (hitmen), unirom (sicklebrick)

### Usage:
`python3 pypsxserial.py PSX-EXE.exe /dev/cu.usbserial`

(substitute your serial port at the end, e.g. '/dev/ttyUSB0' under linux or e.g. 'COM1' under windows).

### Note:
for best results with macOS, use the '/dev/cu.usbserialxyz' style port instead of '/dev/tty.usbserial'.
programmed pause at end to ensure trashy pl2303 driver extension doesn't smash this crashy kernel

### How it works:
1. send an 0x63 to start
2. check the psx gives us something. (psxserial gives me 0x62, unirom gives 0x99?)
3. slurp full 2048 byte header from .exe, send that through in one chunk.
4. rewind, send three chunks of 4 bytes from the .exe:
   - 16-20 = PC start address
   - 24-28 = write location?
   - 28-32 = size minus header
5. send through the .exe in 2048 byte chunks, skipping the header.
6. send through a single 2048 byte chunk full of 0xff
7. close port

