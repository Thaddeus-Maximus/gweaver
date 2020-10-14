import gweaver
from math import *
import serial

prog = gweaver.Program(gweaver.PROTOTRAK_PLUS_CONFIG)
prog.code("PN1 G20 G90")

##################
### REAL STUFF ###
##################

print("Input offset")
o = float(input())

prog.code("M06", T=1, D=0.375)
prog.code("G40")

x = [-2.388+o, -1.163-o]
y = [-2.063-o, -2.391-o, -2.891+o]
feedrate = 10.0

prog.code("G00", X=x[0], Y=y[0], comment="Rapid")

prog.code("G01", XE=x[0], YE=y[2], F=feedrate, absolute=True)
prog.code("G01", XE=x[1], YE=y[2], F=feedrate, absolute=True)
prog.code("G01", XE=x[1], YE=y[1], F=feedrate, absolute=True)
prog.code("G01", XE=x[0], YE=y[0], F=feedrate, absolute=True)

####################
### POST PROCESS ###
####################

with serial.Serial("COM13", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)