import numpy as np
import math

PROTOTRAK_PLUS_CONFIG = {
	"places": 5,
	"line_numbers": True,
	"separator": " ",
	"line_ending": ";\n",
	"comment": lambda x: " ("+x+")",
	"header": "",
	"footer": "%",
	"compensation": True
}

BENCHMAN_CONFIG = {
	"places": 4,
	"line_numbers": True,
	"separator": " ",
	"line_ending": ";\n",
	"comment": lambda x: "",
	"compensation": False
}

def lowerstr(x):
	return x.lower() if type(x) == type(str) else x

class FileWrapper:
	def __init__(self, file, binary=False, en_print=False):
		self.file     = file
		self.binary   = binary
		self.en_print = en_print
		self.buf      = ""

	def write(self, x):
		if self.en_print:
			print(x, end='')
		self.buf += str(x)

	def close(self):
		#print(str.encode(self.buf))
		self.file.write(str.encode(self.buf) if self.binary else self.buf)

class Program:
	def __init__(self, config):
		self.lines = []
		self.config = config
		self.act_compensation  = None
		self.act_tool_diameter = None
		self.act_feedrate      = None
		self.act_position      = np.asarray((0,0,0))

	def feedrate(self, F=None):
		self.act_feedrate = F

	def code(self, code, **kwargs):
		# adds specified line of gcode, with no computations
		self.lines.append((code, kwargs))
		return self

	def rapid(self, pos):
		# a rapid movement to pos
		# remember, rapids don't use tool compensation.
		self.code("G00", X=pos[0], Y=pos[1], F=self.act_feedrate)
		self.act_position = np.asarray(pos)
		return self

	def linmove(self, pos, chain_pct=None):
		# a linear movement, from current position, to pos
		if chain_pct is None:
			self.code("G01", X=pos[0], Y=pos[1], F=self.act_feedrate)
			self.act_position = np.asarray(pos)
		else:
			start = self.act_position
			delta = np.asarray(pos)-self.act_position
			d = np.linalg.norm(delta)
			n = round(d/(self.act_tool_diameter*float(chain_pct)/100.0))
			for i in range(n+1):
				self.rapid(start + delta*float(i)/n)

		return self

	def arcmove(self, center, pos, dir, chain_pct=None, **kwargs):
		# an arc movement, from current machine position, to pos, about center, in specified direction.
		if chain_pct is None:
			code = ""
			if lowerstr(dir) in ["cw", "clockwise", -1]:
				code = "G02"
			elif lowerstr(dir) in ["ccw", "counterclockwise", +1]:
				code = "G03"
			else:
				raise Exception("Invalid arc direction")
			self.code(code, XB=self.act_position[0], YB=self.act_position[1],
					XC = center[0], YC=center[1],
					XE = pos[0], YE=pos[1],
					F=self.act_feedrate, **kwargs)
			self.act_position = pos
		else:
			start = self.act_position
			# blah blah do the chain drilling...
			raise Exception("Thad's lazy, you can't chain drill/plunge mill arcs yet")

		return self

	def slot(self, inside=True, climb=True, offsets=[0], **kwargs): #, flat_len=None, oall_len=None, wd=None, ax=None, ay=None, bx=None, by=None, cx=None, cy=None, theta=None):
		# Slots are defined with:
		# wd, start, end
		# wd, center, theta, and a len_

		# start, end:  tuples of (x,y) points for start and end of slot.
		# center:      tuple of (x,y) point for center of slot.
		# theta:       angle at which slot is oriented (0 is +x, 90 is +y)
		# len_flat:    length of flat part of slot
		# len_overall: overall length of slot
		# wd:          width of slot

		# offsets is an array of offsets from the final diameter. These can be repeated; e.g. offsets of [0.005,0,0] would give a roughing pass, and two finishing passes at the same diameter.

		if not "wd" in kwargs:
			raise Exception("Slot width not defined.")
		wd     = np.asarray(kwargs["wd"])
		start  = None
		end    = None
		center = None

		if "start" in kwargs and "end" in kwargs:
			start  = np.asarray(kwargs["start"])
			end    = np.asarray(kwargs["end"])
			center = (start+end)/2

			t_vec  = start-end
			t_vec  = t_vec/np.linalg.norm(t_vec)
			n_vec  = np.asarray((t_vec[1], -t_vec[0])) # simple x-y rotation

		elif "center" in kwargs and "theta" in kwargs and ("len_flat" in kwargs or "len_overall" in kwargs):
			center = np.asarray(kwargs["center"])
			theta  = float(kwargs["theta"])
			len_flat = None
			if "len_flat" in kwargs:
				len_flat = float(kwargs["len_flat"])
			elif "len_overall" in kwargs:
				len_flat = float(kwargs["len_overall"])-wd

			t_vec = np.asarray((math.cos(math.radians(theta)), math.sin(math.radians(theta))))
			n_vec = np.asarray((t_vec[1], -t_vec[0])) # simple x-y rotation

			start = center + t_vec*len_flat/2
			end   = center - t_vec*len_flat/2

		else:
			raise Exception("Slot position not defined.")

		if self.act_tool_diameter is None:
			raise Exception("Tool diameter never defined.")

		self.compensation("center")
		
		firstpass = True
		lastoffset = offsets[0]

		for offset in offsets:
			actwd = wd + (-1 if inside else +1)*(self.act_tool_diameter+offset*2)

			pt1 = start + n_vec*actwd/2
			pt2 = start - n_vec*actwd/2
			pt3 = end   - n_vec*actwd/2
			pt4 = end   + n_vec*actwd/2

			if firstpass:
				if inside:
					self.rapid(center)
					if climb:
						self.linmove(pt1)
					else:
						self.linmove(pt4)
				else:
					if climb:
						self.rapid(pt4)
					else:
						self.rapid(pt1)
			elif offset != lastoffset:
				if inside == climb:
					self.linmove(pt1)
				else:
					self.linmove(pt4)
			
			if inside == climb:
				self.arcmove(start, pt2, dir="ccw")
				self.linmove(pt3)
				self.arcmove(end,   pt4, dir="ccw")
				self.linmove(pt1)
			else:
				self.arcmove(end,   pt3, dir="cw")
				self.linmove(pt2)
				self.arcmove(start, pt1, dir="cw")
				self.linmove(pt4)

			firstpass  = False
			lastoffset = offset

	def circle(self, inside=True, climb=True, offsets=[0], overlap=10, center=None, r=None, d=None, chain_pct=None):
		# Circles are defined with:
		# - center
		# - r: radius, or d: diameter

		# offsets is an array of offsets from the final diameter. These can be repeated; e.g. offsets of [0.005,0,0] would give a roughing pass, and two finishing passes at the same diameter.
		# overlap is degrees of overlap, to help eliminate cusps (e.g. an overlap ot 10 will cause a movement of 370 degrees each pass)

		# untested!

		if center is None:
			raise Exception("Circle center not defined.")
		if r is None:
			if d is None:
				raise Exception("Circle size not defined.")
			else:
				r = float(d)/2

		self.compensation("center")
		firstpass  = True
		lastoffset = offsets[0]
		theta = 0
		if climb != inside:
			overlap = -overlap

		for offset in offsets:
			actr = r + (-1 if inside else +1)*(self.act_tool_diameter/2 + offset)
			if chain_pct is None:
				# 1: current point
				# 2: opposite point
				# 3: current point + overlap angle
				spt1 = center + actr*np.asarray((math.cos(math.radians(theta)), math.sin(math.radians(theta))))
				spt2 = center - actr*np.asarray((math.cos(math.radians(theta)), math.sin(math.radians(theta))))
				spt3 = center + actr*np.asarray((math.cos(math.radians(theta+overlap)), math.sin(math.radians(theta+overlap))))
				if firstpass:
					if inside:
						self.rapid(center)
						self.linmove(spt1)
					else:
						self.rapid(spt1)
				elif offset != lastoffset:
					if inside == climb:
						self.linmove(spt1)


				self.arcmove(center, spt2, "ccw" if climb==inside else "cw")
				self.arcmove(center, spt3, "ccw" if climb==inside else "cw")
				
				theta += overlap
				firstpass  = False
				lastoffset = offset
			else:
				c = math.pi*r*2 # circumference
				n = round(c/(self.act_tool_diameter*float(chain_pct)/100.0))
				for i in range(n):
					theta = math.pi*2.0*float(i)/n
					self.rapid(np.asarray((math.cos(theta), math.sin(theta)))*actr + np.asarray(center))

	def follow_dxf(self, dxf, inside=True, climb=True, offsets=[0], overlap=0):
		"""
		Follows a DXF path.
		The DXF should only contain one loop (it can be closed or open).
		If the loop is open, you may need to change the "inside" parameter to go in the correct direction.

		@param offsets: an array of offsets from the final path. These can be repeated; offsets=[0.1, 0, 0] would yield a roughing pass and two finishing passes at the same DOC.
		@param climb:   direction to machine (climb or conventional)
		@param overlap: for closed loops, how much to overlap between passes to eliminate cusps. For open loops, this is tangential extension distance.
		"""
		raise Exception("Thad's lazy, DXF stuff don't exist yet")

	def toolchange(self, T=1, D=None):
		"Perform a toolchange."
		self.code("M06", T=T, D=D)
		self.act_tool_diameter = D
		return self

	def compensation(self, TC=None):
		"""
		Set tool compensation mode.

		@param TC: Tool compensation direction.
		Left compensation:        'l', 'left', 1
		Right compensation:       'r', 'right', 2
		Center (no) compensation: 'c', 'center', 0
		"""

		TC = lowerstr(TC)
		if TC in [0, "center", "c"]:
			self.act_compensation = 0
			self.code("G40")
		elif TC in [1, "left", "l"]:
			self.act_compensation = 1
			self.code("G41")
		elif TC in [2, "right", "r"]:
			self.act_compensation = 2
			self.code("G42")
		else:
			raise Exception("Compensation not regonized (center|left|right)")
		return self

	def units(self, unit=""):
		"""
		Set document units.
		
		@param unit: unit to use (inches, inch, in, mm, millimeters, millimeter)
		"""

		if unit in ["in", "inch", "inches"]:
			self.code("G20")
		elif unit in ["mm", "millimeters", "millimeter"]:
			self.code("G21")
		else:
			raise Exception("Unrecognized units (in|mm)")
		return self

	def relativity(self, mode=""):
		"""
		Set machine relativity.

		@param mode: relativity (inc or abs)
		"""

		if mode in ["relative", "inc", "rel", "incremental"]:
			self.code("G91")
		elif mode in ["abs", "absolute"]:
			self.code("G90")
		else:
			raise Exception("Unrecognized relativity (inc|abs)")
		return self

	def comment(self, comment):
		"""
		Create a comment block in g-code.
		@param comment: comment to make
		"""
		self.code("", comment=comment)
		return self

	def to_file(self, rawfile, binary=False, en_print=False):
		file = FileWrapper(rawfile, binary, en_print)
		file.write(self.config["header"])
		# post-processes gcode into specified file-like object (has .write method)
		for idx, line in enumerate(self.lines):
			if self.config["line_numbers"]:
				file.write("N%d" % idx)
				file.write(self.config["separator"])
			file.write("%s" % line[0])
			
			# parse options from values
			codesets = {}
			for key, value in line[1].items():
				if not key.isupper():
					codesets[key]=value

			# write values
			for key, value in line[1].items():
				if key.isupper():
					file.write(self.config["separator"])
					file.write(key)
					if type(value) == int or key in ["M", "S", "G", "H", "T", "L", "N", "O", "P", "TC"]:
						# force certain codes to be integers
						file.write("%d"%int(value))
					elif type(value) == float or isinstance(value, np.float64):
						file.write(("%%.%df"%self.config["places"])%value)
					else:
						file.write(value)
					if "absolute" in codesets and codesets["absolute"] and key in ["X","XC","XB","XE","Y","YB","YC","YE","Z","ZC","ZB","ZE"]:
						file.write("A")
			if "comment" in codesets:
				file.write(self.config["comment"](codesets["comment"]))
			file.write(self.config["line_ending"])
		file.write(self.config["footer"])
		file.close()