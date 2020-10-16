import gweaver
from math import *
import serial

prog = gweaver.Program(gweaver.PROTOTRAK_PLUS_CONFIG).units("in").relativity("abs")

##################
### REAL STUFF ###
##################

print("Input offset")
o = float(input())

prog.toolchange(D=0.375)
prog.compensation("center")

x = [-2.388+o, -1.163-o]
y = [-2.063-o, -2.391-o, -2.891+o]
feedrate = 10.0

prog.code("G00", X=x[0], Y=y[0], comment="Rapid")
prog.feedrate(feedrate)

prog.line(XE=x[0], YE=y[2])
prog.line(XE=x[1], YE=y[2])
prog.line(XE=x[1], YE=y[1])
prog.line(XE=x[0], YE=y[0])

####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)