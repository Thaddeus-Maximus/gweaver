import gweaver as gw
import serial
import itertools

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")
prog.feedrate(50.0)
prog.toolchange(D=0.5)

####################
###  REAL  SHIT  ###
####################

prog.follow_dxf("test.dxf", inside=False)

####################
### POST PROCESS ###
####################

#with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
with open("dump.nc", "w") as s:
	prog.to_file(s, binary=False, en_print=True)