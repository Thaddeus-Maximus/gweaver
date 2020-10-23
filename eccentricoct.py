import gweaver as gw
import serial
import itertools

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

feedrate = 20.0


for o in [0.020, 0.005, 0.000]:
	d_tool = 0.5+o*2

	prog.toolchange(D=d_tool)
	prog.feedrate(feedrate)
	prog.compensation("left")

	pts = [(.078, -.188), (-.078, -.188), (-.188, -.078), (-.188, .078), (-.078, .188), (.078, .188), (.188, .078), (.188, -.078)]
	pts.append(pts[0]) # wraparound
	
	prog.code("G00", X=1.0, Y=-1.0)
	for x, y in pts:
		prog.code("G01", X=x, Y=y, F=feedrate)

####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)