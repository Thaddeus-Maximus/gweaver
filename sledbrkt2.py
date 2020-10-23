import gweaver as gw
import serial
import itertools

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

print("Which part?")
part = str(input())

pts = [
	(0.5, 0.5), (7.5, 0.5), # 3/8 bearings
	(0.9073, 1.0), (2.0928, 0.188), (2.0928, 1.813), # 3/16 dowels
	(1.5, 0.5), (1.5, 1.5), (6.375, 0.5), (6.625, 0.5), (6.625, 1.5), (6.375, 1.5) # mount holes
	] 

if part in ["", "drill"]:
	prog.toolchange(D=0.16)
	for x, y in pts:
		prog.code("G00", X=x, Y=-y)

if part in ["", "mount"]:
	for o in [0.010, 0.000]:
		d_tool = 0.1875+o*2

		prog.toolchange(D=d_tool)
		feedrate = 20.0
		prog.compensation("left")

		for a in [0.0, 1.0]:
			prog.code("G00", X=1.500, Y=-.500-a)
			prog.code("G03", XB=1.63, YB=-.500-a, XC=1.500, YC=-.500-a, XE=1.63, YE=-.500-a, F=feedrate)

			prog.code("G00", X=6.625,   Y=-.500-a)
			prog.code("G01", X=6.625,   Y=-.370-a)
			prog.code("G01", X=6.375,   Y=-.370-a, F=feedrate)
			prog.code("G03", XB=6.375, YB=-.370-a,   XC=6.375, YC=-0.5-a, XE=6.375, YE=-.630-a, F=feedrate)
			prog.code("G01", X=6.625,   Y=-.630-a, F=feedrate)
			prog.code("G03", XB=6.625, YB=-.630-a, XC=6.625, YC=-0.5-a, XE=6.625, YE=-.370-a, F=feedrate)
			prog.code("G01", X=6.375,   Y=-.370-a, F=feedrate)

####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)