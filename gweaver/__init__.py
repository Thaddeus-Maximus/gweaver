
PROTOTRAK_PLUS_CONFIG = {
	"places": 4,
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
		self.buf += x

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

	def feedrate(self, F=None):
		self.act_feedrate = F

	def code(self, code, **kwargs):
		# adds specified line of gcode, with no computations
		self.lines.append((code, kwargs))
		return self

	def arc(self, XB=None, YB=None, XE=None, YE=None, R=None, RS=0, XC=None, YC=None):
		# Provide either:
		# XB, YB, XE, YE, R, CS
		# XB, YB, XE, YE, XC, YC
		# R is radius, CS is "center select"; -2 is large left-hand, -1 is small left-hand, +1 is small right-hand, +2 is large right-hand
		return self

	def toolchange(self, T=1, D=None):
		# perform a toolchange
		self.code("M06", T=T, D=D)
		self.act_tool_diameter = D
		return self

	def compensation(self, TC=None):
		TC = lowerstr(TC)
		# set compensation mode; 0=center, 1=right, 2=left
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
		if unit in ["in", "inch", "inches"]:
			self.code("G20")
		elif unit in ["mm", "millimeters", "millimeter"]:
			self.code("G21")
		else:
			raise Exception("Unrecognized units (in|mm)")
		return self

	def relativity(self, mode=""):
		if mode in ["relative", "inc", "rel", "incremental"]:
			self.code("G91")
		elif mode in ["abs", "absolute"]:
			self.code("G90")
		else:
			raise Exception("Unrecognized relativity (inc|abs)")
		return self

	def comment(self, comment):
		self.code("", comment=comment)
		return self

	def line(self, **kwargs):
		# not too sophisticated...
		if self.act_feedrate:
			self.code("G01", F=self.act_feedrate, **kwargs)
		else:
			self.code("G01", **kwargs)
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
					if type(value) == float:
						file.write(("%%.%df"%self.config["places"])%value)
					elif type(value) == int:
						file.write("%d"%value)
					else:
						file.write(value)
					if "absolute" in codesets and codesets["absolute"] and key in ["X","XC","XB","XE","Y","YB","YC","YE","Z","ZC","ZB","ZE"]:
						file.write("A")
			if "comment" in codesets:
				file.write(self.config["comment"](codesets["comment"]))
			file.write(self.config["line_ending"])
		file.write(self.config["footer"])
		file.close()