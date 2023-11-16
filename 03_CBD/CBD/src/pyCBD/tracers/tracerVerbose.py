"""
Verbose tracer for the CBD Simulator.
"""

from .baseTracer import BaseTracer
from .color import COLOR

class VerboseTracer(BaseTracer):
	"""
	Verbose tracer for the CBD Simulator.
	"""
	def traceStartNewIteration(self, curIt, time):
		txt1 = COLOR.colorize("Iteration: ", COLOR.BOLD)
		txt2 = COLOR.colorize("{:>5}".format(curIt), COLOR.GREEN)
		txt3 = COLOR.colorize("; Time: ", COLOR.BOLD)
		txt4 = COLOR.colorize("{:>10.3}".format(time), COLOR.RED)
		rem = "_" * (self.width - 11 - 5 - 8 - 10)
		if curIt > 0:
			self.trace("\n")
		self.traceln("__", txt1, txt2, txt3, txt4, rem)
		self.trace("\n")

	def traceCompute(self, curIt, block):
		text = " " + COLOR.colorize(block.getPath(), COLOR.ITALIC, COLOR.CYAN) + ":"
		inps = block.getInputPorts()
		deps = [x.block.getBlockName() for x in block.getDependencies(curIt)]
		if len(inps) > 0:
			text += "\n\tINPUT VALUES:"
			for inp in inps:
				out = inp.getIncoming().source
				other = out.block
				if other.getBlockName() in deps:
					text += "\n\t\t{:>10} -> {:<10} : {}"\
						.format(other.getPath() + ":" + out.name, inp.name,
					            COLOR.colorize(str(inp.getHistory()[curIt]), COLOR.YELLOW))
		outs = block.getOutputPorts()
		if len(outs) > 0:
			if len(inps) > 0:
				text += "\n"
			text += "\n\tOUTPUT VALUES:"
			for out in outs:
				text += "\n\t\t{:<24} : {}".format(out.name, COLOR.colorize(str(out.getHistory()[curIt]), COLOR.YELLOW))
		self.traceln(text + "\n")
