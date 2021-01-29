import gweaver as gw
import serial

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

print("Which part?")
part = str(input())

if part in ["", "pocket"]:
	prog.toolchange(D=0.25)
	prog.feedrate(20.0)
	prog.compensation("center")

	prog.code("G106", XB=0.450, YB=0.660, XD=2.190, YD=-0.660, DR=2, TC=1, D=0.2, CR=0.02, FC=0.005, F=20.0)

if part in ["", "slots"]:
	prog.toolchange(D=0.1875)
	prog.feedrate(20.0)
	prog.compensation("center")
	xs = [0.60, 1.05, 1.50, 1.95]
	ys = [-0.40, -1.00]
	y  = ys[0]
	prog.rapid((-0.5, 0.0))
	prog.linmove((xs[0], 0.0))
	for x in xs:
		prog.linmove((x, y))
		y = ys[0] if y==ys[1] else ys[1]
		prog.linmove((x, y))

####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)