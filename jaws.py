import gweaver as gw
import serial
import sys

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

if len(sys.argv) < 2:
	print("Provide which part you wish to generate code for as an argument.")
	exit()

part = sys.argv[1]

prog.toolchange(D=0.250)
prog.feedrate(5.0)
prog.compensation("left")

if part=="854":
	prog.rapid  ((-.830, -2.349))
	prog.linmove((-.812, -2.338))
	prog.arcmove((-.900, -2.185), (-.775, -2.060), "ccw")
	prog.linmove((-.860, -1.974))

elif part == "855":
	prog.rapid  ((+.260, -1.974))
	prog.linmove((+.175, -2.060))
	prog.arcmove((+.300, -2.185), (+.212, -2.338), "ccw")
	prog.linmove((+.220, -2.343))

else:
	print("Invalid part.")
	exit()

####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)