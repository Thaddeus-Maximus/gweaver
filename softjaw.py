import gweaver as gw
import serial
import itertools

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

feedrate = 20.0

print("Input portion to generate. \n> ", end="")
portion = str(input())

if portion in ["slots"]:

	a = 3.5 # center of jaw
	b = 3.5625/2 # radius of slot pattern

	prog.code("G00", X=a-b, Y=-0.9375)
	prog.code("G00", X=a+b, Y=-0.9375)

	o = 0.000
	d_tool = 0.375+o*2

	prog.toolchange(D=d_tool)
	prog.feedrate(feedrate)
	prog.compensation("center")

	prog.slot(F=feedrate, wd=.460-d_tool, len_flat=0.2, center=(a-b, -0.9375), theta=90.0)
	prog.slot(F=feedrate, wd=.460-d_tool, len_flat=0.2, center=(a+b, -0.9375), theta=90.0)
	prog.slot(F=feedrate, wd=.690-d_tool, len_flat=0.2, center=(a-b, -0.9375), theta=90.0)
	prog.slot(F=feedrate, wd=.690-d_tool, len_flat=0.2, center=(a+b, -0.9375), theta=90.0)

if portion in ["face"]:
	for o in [0.020, 0.005, 0.000]:
		d_tool = 0.125+o*2

		prog.toolchange(D=d_tool)
		prog.feedrate(feedrate)
		prog.compensation("right")

		prog.slot(F=feedrate, wd=.490, len_flat=.350, center=(0.0, 0.0), theta=0)

####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)