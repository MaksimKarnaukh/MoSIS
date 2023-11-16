from pyCBD.Core import *
from pyCBD.lib.std import *

DELTA_T = 0.1

from pyCBD.Core import CBD
from pyCBD.lib.std import *
from pyCBD.lib.endpoints import SignalCollectorBlock

class SinGen(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=[], output_ports=[])

        # Create the Blocks
        self.addBlock(TimeBlock("time"))
        self.addBlock(GenericBlock("sin", block_operator=("sin")))
        self.addBlock(ConstantBlock("A", 1.0))
        self.addBlock(ConstantBlock("B", 1.0))
        self.addBlock(ProductBlock("amp"))
        self.addBlock(ProductBlock("per"))
        #   Using a buffer, the memory won't be flooded
        self.addBlock(SignalCollectorBlock("plot", buffer_size=500))

        # Create the Connections
        self.addConnection("B", "per")
        self.addConnection("time", "per")
        self.addConnection("per", "sin")
        self.addConnection("A", "amp")
        self.addConnection("sin", "amp")
        self.addConnection("amp", "plot")


