import gweaver as gw
import serial
import itertools

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

feedrate = 20.0

print("Input portion to generate. \n> ", end="")
portion = str(input())

if portion in ["softjaw"]:
	for o in [0.020, 0.005, 0.000]:
		d_tool = 0.125+o*2

		prog.toolchange(D=d_tool)

		prog.slot(F=feedrate, wd=.239-d_tool, len_overall=.590-d_tool, center=(0.0, 0.0), theta=0)

if portion in ["", "chamfer"]:
	o = .02
	d_tool = 0

	prog.toolchange(D=d_tool)

	prog.slot(F=feedrate, wd=.500+o*2, len_flat=.360+o*2, center=(0.0, 0.0), theta=0)

####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)