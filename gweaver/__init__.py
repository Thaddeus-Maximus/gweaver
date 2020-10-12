
PROTOTRAK_PLUS_CONFIG = {
	"places": 4,
	"line_numbers": True,
	"separator": " ",
	"line_ending": ";\n",
	"comment": lambda x: " ("+x+")"
}

class Program:
	def __init__(self, config):
		self.lines = []
		self.config = config

	def code(self, code, **kwargs):
		# adds specified line of gcode, with no computations
		self.lines.append((code, kwargs))

	def to_file(self, file):
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

