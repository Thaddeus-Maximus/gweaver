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

x0 = 0.5
y0 = 0.5
dx = 1.0
dy = -1.0
nx = 5
ny = 5

for i in range(nx):
	for j in range(ny):
		#print(i, j)
		if (i%2 == j%2) == ("tap" in part):
			prog.rapid((x0+i*dx, y0+i*dy))
			print(i, j)

####################
### POST PROCESS ###
####################

with gw.prototrak_serial("COM3") as s:
	prog.to_file(s, binary=True, en_print=True)