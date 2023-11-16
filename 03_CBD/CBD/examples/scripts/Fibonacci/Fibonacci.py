#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from pyCBD.Core import *
from pyCBD.lib.std import *


class FibonacciGen(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=[], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(DelayBlock("delay1"))
        self.addBlock(DelayBlock("delay2"))
        self.addBlock(AdderBlock("sum", 2))
        self.addBlock(ConstantBlock("zero", value=(0)))
        self.addBlock(ConstantBlock("one", value=(1)))

        # Create the Connections
        self.addConnection("delay1", "delay2", input_port_name='IN1', output_port_name='OUT1')
        self.addConnection("delay1", "sum", input_port_name='IN2', output_port_name='OUT1')
        self.addConnection("delay2", "sum", input_port_name='IN1', output_port_name='OUT1')
        self.addConnection("sum", "delay1", input_port_name='IN1', output_port_name='OUT1')
        self.addConnection("sum", "OUT1", output_port_name='OUT1')
        self.addConnection("zero", "delay1", input_port_name='IC', output_port_name='OUT1')
        self.addConnection("one", "delay2", input_port_name='IC', output_port_name='OUT1')


