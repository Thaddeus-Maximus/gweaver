import gweaver
from math import *
import serial

R1 = 39.3701 # larger outer radius
R2 =  0.1969 # smaller outer radius
A =  3.0453 # longer distance to corner
B =  2.8633 # shorter distance to corner

CC =  2.8490
CS = 36.2205

DIH = 5.900  # inner hole diameter

BHX = 2.6575 # bolt hole x/y position

D_MILL   = 1.00
F_MILL   = 15.0 #
O_FINISH = 0.005

D_DRILL = 0.290
O_ROUGH = 0.05

prog = gweaver.Program(gweaver.PROTOTRAK_PLUS_CONFIG)
prog.code("PN1 G20 G90")

print("Input program to generate")
name = input()

##################
### REAL STUFF ###
##################

if name in ["","mount"]:
	prog.code("M06 T1", D=D_DRILL)
	prog.code("G40")
	for t in [(1,1), (1,-1), (-1,1), (-1,-1)]:
		prog.code("G00", X=t[0]*BHX, Y=t[1]*BHX)

if name in ["","chain"]:
	# chain drilling
	prog.code("M06 T1 D%.4f" % D_DRILL)
	prog.code("G40")
	DIC = DIH-D_DRILL-O_ROUGH*2
	N = round(DIC*pi/D_DRILL*1.1) # 1.1 for some overlap between holes
	for i in range(N):
		prog.code("G00 X%.4f Y%.4f" % (DIC/2*cos(2*pi*i/N), DIC/2*sin(2*pi*i/N)))

if name in ["","inner"]:
	# inner profile

	print("Input finish offset")
	O_FINISH = float(input())

	d = D_MILL + O_FINISH*2

	prog.code("M06", T=1, D=d)
	prog.code("G41")
	prog.code("G03", XB=DIH/2, I=DIH/2, YB=0, F=F_MILL)

if name in ["","outer"]:
	# outer profile

	print("Input finish offset")
	O_FINISH = float(input())

	d = D_MILL + O_FINISH*2

	prog.code("M06", T=1, D=d)
	prog.code("G41")
	XV = [A, A, B, -B, -A, -A, -B, B, A]
	YV = [B, -B, -A, -A, -B, B, A, A, B]
	XCV = [-R1, R2, 0, -R2, R1, -R2, 0, R2]
	YCV = [0, -R2, R1, -R2, 0, -R2, -R1, -R2]
	prog.code("G00", X=XV[0], Y=YV[0], comment="Rapid")
	for i in range(8):
		prog.code("G02", XB=XV[i], YB=YV[i], XE=XV[i+1], YE=YV[i+1], XC=XCV[i], YC=YCV[i], F=F_MILL, absolute=True)

####################
### POST PROCESS ###
####################

with open(__file__ +'.'+name+'.nc', 'w') as f:
	prog.to_file(f)
#with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as f:
#	prog.to_file(f)