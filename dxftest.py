import gweaver as gw
import serial
import itertools

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")
prog.feedrate(50.0)
prog.toolchange(D=0.5)

####################
###  REAL  SHIT  ###
####################

print(gw.dxf_entities("test.dxf"))

####################
### POST PROCESS ###
####################

#with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
#	prog.to_file(s, binary=True, en_print=True)