import gweaver as gw
import serial
import itertools

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")
prog.feedrate(50.0)
prog.toolchange(D=0.5)

####################
###  REAL  SHIT  ###
####################

"""for y in [0.0, 2.0]:
	prog.slot(inside=False, climb=False,
		wd=1.0, len_overall=2.0, center=(0.0, y), theta=0,
		offsets=[0.1, 0.005, 0.0])"""

prog.circle(inside=True, climb=False, d=3, center=(0,0), offsets=[0.5, 0.1, 0.0, 0.0], overlap=20)

####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)