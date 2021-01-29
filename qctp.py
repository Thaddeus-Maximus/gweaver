import gweaver as gw
import serial
import sys

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

if len(sys.argv) < 2:
	print("Provide which part you wish to generate code for as an argument.")
	exit()
part = sys.argv[1]

feedrate = 10.0

prog.toolchange(D=0.5)
prog.feedrate(feedrate)
#prog.compensation("left")

slot_ys = [-.66, -.66-.45]

if "line" in part:
	prog.code(XB=2.500, YB=0.625, XE=1.875, YE=1.250, F=feedrate)
	prog.code(XB=1.183, YB=1.871, XE=0.554, YE=2.500, F=feedrate)
elif "bore" in part:
	prog.rapid((1.25, 1.25))
	prog.circle(offsets=[0.2, 0.1, 0.005, 0.000, -0.001], center=(1.25, 1.25), d=1.250)
else:
	print("Invalid part.")
	exit()

####################
### POST PROCESS ###
####################

with gw.prototrak_serial("COM3") as s:
	prog.to_file(s, binary=True, en_print=True)