import gweaver as gw
import serial

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

print("Which part?")
part = str(input())

if part in ["", "holes"]:
	x = [+a+.470 for a in [0,1,2]]
	y = [-a-.470 for a in [0,1,2,3]]
	for idx in [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (3,0)]:
		prog.code("G00", X=x[idx[1]], Y=y[idx[0]])
	prog.code("G00", X=14.0, Y=0.0)

if part in ["", "outline"]:
	for o in [0.005, 0]:
		d = 0.25+o*2
		r = 0.140
		feedrate = 20.0

		prog.toolchange(D=d)
		prog.feedrate(feedrate)
		prog.compensation("left")

		prog.code("G00", X=2.830, Y=0.25, comment="Prep for work")
		prog.code("G01", XE=2.830, YE=-0.030, F=feedrate)
		prog.code("G02", XB=2.830, YB=-0.030, XE=2.970, YE=-0.170, F=feedrate, I=0, J=-r) # XC=2.830, YC=-0.170, 
		prog.code("G01", XB=2.970, YB=-0.170, XE=2.970, YE=-1.830, F=feedrate)
		prog.code("G02", XB=2.970, YB=-1.830, XE=2.830, YE=-1.970, F=feedrate, I=-r, J=0) # XC=1.830, YC=-1.830, 
		prog.code("G01", XB=2.830, YB=-1.970, XE=1.110, YE=-1.970, F=feedrate)
		prog.code("G03", XB=1.110, YB=-1.970, XE=0.970, YE=-2.110, F=feedrate, I=0, J=-r) # XC=1.110, YC=-2.110, 
		prog.code("G01", XB=0.970, YB=-2.110, XE=0.970, YE=-3.830, F=feedrate)
		prog.code("G02", XB=0.970, YB=-3.830, XE=0.830, YE=-3.970, F=feedrate, I=-r, J=0) # XC=0.830, YC=-3.830, 
		prog.code("G01", XB=0.830, YB=-3.970, XE=0.170, YE=-3.970, F=feedrate)
		prog.code("G02", XB=0.170, YB=-3.970, XE=0.030, YE=-3.830, F=feedrate, I=0, J=r) # XC=0.170, YC=-3.830, 
		prog.code("G01", XB=0.030, YB=-3.830, XE=-0.2, YE=-3.830, comment="Move away off work")
	prog.code("G00", X=14.0, Y=0.0)


####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)