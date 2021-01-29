import gweaver as gw
import serial
import sys

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

if len(sys.argv) < 2:
	print("Provide which part you wish to generate code for as an argument.")
	exit()

part = sys.argv[1]

prog.toolchange(D=0.50)
prog.feedrate(10.0)
#prog.compensation("left")

if part=="outer":
	prog.circle(inside=False, climb=True, offsets=[0.02, 0.005, 0, 0], overlap=10, center=(0.0,0.0), d=.696)

elif part == "inner":
	prog.circle(inside=False, climb=True, offsets=[0.1, 0.02, 0.005, 0, 0], overlap=10, center=(.060,0.0), d=.433)

else:
	print("Invalid part.")
	exit()

####################
### POST PROCESS ###
####################

with gw.prototrak_serial("COM3") as s:
	prog.to_file(s, binary=True, en_print=True)