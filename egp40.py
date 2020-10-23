import gweaver as gw
import serial
import itertools

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

print("Which part?")
part = str(input())

if part in ["", "holes"]:
	xs = [-0.630, 0.630]
	ys = [-0.512, 0.512]
	for x, y in itertools.product(xs, ys):
		prog.code("G00", X=x, Y=y)

if part in ["", "slot"]:
	print("Input offset")
	o=float(input())

	d_tool = 0.125+o*2
	d_slot = 0.1974
	feedrate = 20.0

	prog.toolchange(D=d_tool)
	prog.feedrate(feedrate)
	prog.compensation("left")

	prog.code("G00", X=-.591, Y=0)
	prog.code("G01", XB=-.591, YB=d_slot/2, X=-.620, Y=d_slot/2, F=feedrate)
	prog.code("G03", XB=-.620, YB=d_slot/2, XC=-.620, YC=0, XE=-.620, YE=-d_slot/2, F=feedrate)
	prog.code("G01", X=-.591, Y=-d_slot/2, F=feedrate)
	prog.code("G03", XB=-.591, YB=-d_slot/2, XC=-.591, YC=0, XE=-.591, YE=d_slot/2, F=feedrate)

if part in ["", "bore"]:
	print("Input offset")
	o = float(input())

	d_tool = 0.125+o*2
	d_bore = 0.7864
	feedrate = 20.0

	prog.toolchange(D=d_tool)
	prog.feedrate(feedrate)
	prog.compensation("left")

	prog.code("G00", X=0, Y=0)
	prog.code("G03", XB=d_bore/2, YB=0, XE=d_bore/2, YE=0, XC=0, YC=0, F=feedrate)


####################
### POST PROCESS ###
####################

with serial.Serial("COM13", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)