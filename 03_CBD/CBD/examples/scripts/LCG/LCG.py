#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py LCG.xml -av -F CBD -e LCG -t 100

from pyCBD.Core import *
from pyCBD.lib.std import *


class LCG(CBD):
    def __init__(self, block_name, a=(1), c=(4), m=(9), x0=(0)):
        CBD.__init__(self, block_name, input_ports=[], output_ports=["OUT1"])

        # Create the Blocks
        self.addBlock(ConstantBlock("a", value=(a)))
        self.addBlock(ConstantBlock("x0", value=(x0)))
        self.addBlock(ConstantBlock("c", value=(c)))
        self.addBlock(ConstantBlock("m", value=(m)))
        self.addBlock(DelayBlock("delay"))
        self.addBlock(ProductBlock("mult"))
        self.addBlock(AdderBlock("sum"))
        self.addBlock(ModuloBlock("mod"))

        # Create the Connections
        self.addConnection("x0", "delay", input_port_name='IC', output_port_name='OUT1')
        self.addConnection("a", "mult", input_port_name='IN1', output_port_name='OUT1')
        self.addConnection("delay", "mult", input_port_name='IN2', output_port_name='OUT1')
        self.addConnection("mult", "sum", input_port_name='IN1', output_port_name='OUT1')
        self.addConnection("c", "sum", input_port_name='IN2', output_port_name='OUT1')
        self.addConnection("sum", "mod", input_port_name='IN1', output_port_name='OUT1')
        self.addConnection("m", "mod", input_port_name='IN2', output_port_name='OUT1')
        self.addConnection("mod", "delay", input_port_name='IN1', output_port_name='OUT1')
        self.addConnection("mod", "OUT1", input_port_name='IN1', output_port_name='OUT1')


