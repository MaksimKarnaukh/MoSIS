"""
Useful drawing function to easily draw a CBD model in Graphviz.
"""
from pyCBD.Core import CBD
from pyCBD.lib.std import *


def gvDraw(cbd, filename, rankdir="LR", colors=None):
	"""
	Outputs a :class:`CBD` as a `GraphViz <https://graphviz.org/>`_ script to filename.

	For instance, drawing the CBD given in the :doc:`examples/EvenNumberGen` example, the following figure
	can be obtained:

	.. figure:: _figures/EvenNumberGV.svg

	Note:
		The resulting Graphviz file might look "clunky" and messy when rendering with
		the standard :code:`dot` engine. The :code:`neato`, :code:`twopi` and :code:`circo`
		engines might provide a cleaner and more readable result.

	Args:
		cbd (CBD):          The :class:`CBD` to draw.
		filename (str):     The name of the dot-file.
		rankdir (str):      The GraphViz rankdir of the plot. Must be either :code:`TB`
							or :code:`LR`.
		colors (dict):      An optional dictionary of :code:`blockname -> color`.
	"""
	# f = sys.stdout
	f = open(filename, "w")
	write = lambda s: f.write(s)

	write("""// CBD model of the {n} block
// Created with CBD.converters.CBDDraw
digraph model {{
 splines=ortho;
 label=<<B>{n} ({t})</B>>;
 labelloc=\"t\";
 fontsize=20;
 rankdir=\"{rd}\";
""".format(n=cbd.getPath(), t=cbd.getBlockType(), rd=rankdir))

	if colors is None:
		colors = {}

	def writeBlock(block):
		"""
		Writes a block to graphviz.

		Args:
			block:  The block to write.
		"""
		if isinstance(block, ConstantBlock):
			label = " {}\\n({})\\n{}".format(block.getBlockType(), block.getBlockName(), block.getValue())
		elif isinstance(block, GenericBlock):
			label = " {}\\n({})\\n{}".format(block.getBlockType(), block.getBlockName(), block.getBlockOperator())
		elif isinstance(block, ClampBlock) and block._use_const:
			label = " {}\\n({})\\n[{}, {}]".format(block.getBlockType(), block.getBlockName(), block.min, block.max)
		else:
			label = block.getBlockType() + "\\n(" + block.getBlockName() + ")"

		shape = "box"
		if isinstance(block, CBD):
			shape = "Msquare"
		elif isinstance(block, ConstantBlock):
			shape = "ellipse"

		col = ""
		if block.getBlockName() in colors:
			col = ", color=\"{0}\", fontcolor=\"{0}\"".format(colors[block.getBlockName()])

		write(" {b} [label=\"{lbl}\", shape={shape}{col}];\n".format(b=nodeName(block),
			lbl=label,
			shape=shape,
			col=col))

	def nodeName(block):
		return "node_%d" % id(block)

	for port in cbd.getInputPorts():
		s = "%s_%s" % (nodeName(cbd), port.name)
		write(" {s} [shape=point, width=0.01, height=0.01];\n".format(s=s))
		i = "inter_%d_%s" % (id(port.block), port.name)
		write(" {i} [shape=point, width=0.01, height=0.01];\n".format(i=i))
		write(" {b} -> {i} [taillabel=\"{inp}\", arrowhead=\"none\", arrowtail=\"inv\", dir=both];\n".format(i=i, b=s, inp=port.name))
	for block in cbd.getBlocks():
		writeBlock(block)
		for in_port in block.getInputPorts():
			other = in_port.getIncoming().source
			op = other.name
			i = "inter_%d_%s" % (id(other.block), op)
			write(" {i} -> {b} [headlabel=\"{inp}\", arrowhead=\"normal\", arrowtail=\"none\", dir=both];\n".format(i=i, b=nodeName(block), inp=in_port.name))
		for op in block.getOutputPortNames():
			i = "inter_%d_%s" % (id(block), op)
			# if i not in conn: continue
			write(" {i} [shape=point, width=0.01, height=0.01];\n".format(i=i))
			write(" {a} -> {i} [taillabel=\"{out}\", arrowtail=\"oinv\", arrowhead=\"none\", dir=both];\n"\
			      .format(i=i, a=nodeName(block), out=op))
	for port in cbd.getOutputPorts():
		other = port.getIncoming().source
		i = "inter_%d_%s" % (id(other.block), other.name)
		t = "%s_%s" % (nodeName(cbd), port.name)
		write(" {b} [shape=point, width=0.01, height=0.01];\n".format(b=t))
		write(" {i} -> {b} [headlabel=\"{inp}\", arrowhead=\"onormal\", arrowtail=\"none\", dir=both];\n".format(i=i, b=t, inp=port.name))

	write("\n}")
	f.close()
