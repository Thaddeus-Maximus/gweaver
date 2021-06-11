import gweaver as gw
import serial
import sys
import math

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

if len(sys.argv) < 2:
	print("Provide which part you wish to generate code for as an argument.")
	exit()
part = sys.argv[1]

feedrate = 10.0

prog.toolchange(D=0.5)
prog.feedrate(feedrate)

slot_ys = [-.66, -.66-.45]

if "line" in part:
	prog.compensation("center")
	for d in [0.02, 0.00]:
		a = (0.25+d)/math.sqrt(2)
		prog.rapid  ((2.500+a, 0.625+a))
		prog.linmove((1.875+a, 1.250+a))
		prog.rapid  ((1.183+a, 1.871+a))
		prog.linmove((0.554+a, 2.500+a))
elif "bore" in part:
	prog.compensation("left")
	prog.rapid((1.25, 1.25))
	prog.circle(offsets=[0.3, 0.2, 0.1, 0.005, 0.000, -0.001], center=(1.25, 1.25), d=1.250)
else:
	print("Invalid part.")
	exit()

####################
### POST PROCESS ###
####################

with gw.prototrak_serial("COM3") as s:
	prog.to_file(s, binary=True, en_print=True)