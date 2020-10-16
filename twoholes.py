import gweaver as gw
import serial

prog = gw.Program(gw.PROTOTRAK_PLUS_CONFIG).units("mm").relativity("abs")

print("Input offset")
o = float(input())
dx = 1.5*25.4/2
dy = 13.175 #48/2
dy2 = 55.675
r  = 16.0/2
feedrate = 250

prog.toolchange(D=9.0/16.0*25.4+o*2)
prog.feedrate(feedrate)
prog.compensation("left")

prog.code("G00", X=r+dx, Y=-dy)
prog.code("G03", XB=r+dx, YB=-dy, I=-r, F=feedrate)
prog.code("G00", X=r-dx, Y=-dy)
prog.code("G03", XB=r-dx, YB=-dy, I=-r, F=feedrate)
prog.code("G00", X=r-0, Y=-dy2)
prog.code("G03", XB=r-0, YB=-dy2, I=-r, F=feedrate)


####################
### POST PROCESS ###
####################

with serial.Serial("COM3", baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as s:
	prog.to_file(s, binary=True, en_print=True)