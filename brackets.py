import gweaver as gw
import serial
import sys

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

if len(sys.argv) < 2:
	print("Provide which part you wish to generate code for as an argument.")
	exit()

part = sys.argv[1]

prog.toolchange(D=0.3125)
prog.feedrate(10.0)
#prog.compensation("left")

slot_ys = [-.66, -.66-.45]

if "hole" in part:
	ys = []
	if "slot" in part:
		ys = slot_ys
	else:
		ys = [1.0-.25]

	for i in range(4):
		for j in range(2):
			for y in ys:
				x = .375 + 2.125*i + 1.25*j
				prog.rapid((x, y))
elif part == "slots":
	for i in range(4):
		for j in range(2):
			x = .375 + 2.125*i + 1.25*j
			prog.slot(offsets=[.005, .000], start=(x, slot_ys[0]), end=(x, slot_ys[1]), wd=0.325)


else:
	print("Invalid part.")
	exit()

####################
### POST PROCESS ###
####################

with gw.prototrak_serial("COM3") as s:
	prog.to_file(s, binary=True, en_print=True)