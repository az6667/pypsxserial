#!/usr/bin/env python3.6
#
# for python >= 3.6
#
# poorly written implementation of playstation serial upload capability via psxserial / unirom / etc.
# this checks nothing, will gladly send your grandmother through the serial port, and will fail with a whimper.
# tested with:
#    Language:
#      python3.6
#    OS:
#      macOS w/pl2303 driver extension
#      linux w/built-in driver
#      windows w/pl2303 driver
#    Hardware:
#      pl2303 (configured for 3.3v) and a 3-wire GND/TXD/RXD interface to PSX serial port
#    PSX:
#      psxserial (hitmen)
#      unirom (sicklebrick)
#
#
# usage:
#    python3 pypsxserial.py PSX-EXE.exe /dev/cu.usbserial
#    (substitute your serial port at the end, e.g. '/dev/ttyUSB0' under linux or e.g. 'COM1' under windows).
#
# note: for best results with macOS, use the '/dev/cu.usbserialxyz' style port instead of '/dev/tty.usbserial'.
#    programmed pause at end to ensure trashy pl2303 driver extension doesn't smash this crashy kernel
#
# how it works:
#    send an 0x63 to start
#    check the psx gives us something. (psxserial gives me 0x62, unirom gives 0x99?)
#    slurp full 2048 byte header from .exe, send that through in one chunk.
#    rewind, send three chunks of 4 bytes from the .exe:
#       16-20 = PC start address
#       24-28 = write location?
#       28-32 = size minus header
#    send through the .exe in 2048 byte chunks, skipping the header.
#    send through a single 2048 byte chunk full of 0xff
#    close port
#

import serial
import sys
import time

if len(sys.argv) < 3:
    print("usage: pypsxserial.py <FILE_TO_UPLOAD.EXE> <SERIAL_PORT_DEVICE>\n")
    print("example port devices:\n   /dev/cu.usbserial (macOS - avoid tty.*)\n   /dev/ttyUSB0 (linux)\n   COM1 (windows)\n")
    quit(-1)

filename = sys.argv[1]
ttydevice = sys.argv[2]

try:
    filedata=open(filename,"rb").read()
    filelen=len(filedata)
    with serial.Serial(ttydevice,115200) as ser:
        print(f'using serial port: {ser.name}')
        print("sending start command 0x63...",end="")
        ser.write(b'\x63')
        print("done. reading response...")
        data=ser.read(1)
        print(f'response received: {data}')
        print("having a little nap...")
        time.sleep(1)
        print("sending header....",end="")
        ser.write(filedata[0:2048])
        print(",PC...",end="")
        ser.write(filedata[16:20])
        print(",writeaddr...",end="")
        ser.write(filedata[24:28])
        print(",writelen...")
        ser.write(filedata[28:32])
        print("now sending file contents:")
        chunks = (int)((filelen-(filelen%2048))/2048)
        for x in range(chunks):
            print(f'chunk: {x}')
            ser.write(filedata[(x+1)*2048:(x+2)*2048])
        print("writing remaining bytes")
        ser.write(filedata[(chunks*2048):(chunks*2048)+(filelen%2048)])
        print("sending close & execute command...")
        finalchunk = b''
        for x in range(2048):
            finalchunk += b'\xff'
        ser.write(finalchunk)
        print("done!")
        ser.close()
except:
    print("something error happens")
finally:
    #need a sleep, to avoid bad driver bugs
    time.sleep(2)
