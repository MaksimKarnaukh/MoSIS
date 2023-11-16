#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py SinGen.xml -fav -F CBD -e SinGen -E delta=0.1
import sys
# from pathlib import Path
# import sys
# path_root = str(Path(__file__).parents[2].parents[0]) + '\\src\\'
# sys.path.append(str(path_root))
# print(path_root)
from pyCBD.Core import *
from pyCBD.lib.std import *

DELTA_T = 0.1

class SinGen(CBD):
    def __init__(self, name="SinGen"):
        CBD.__init__(self, name, input_ports=[], output_ports=["OUT1"])

        # Add the 't' parameter
        # Let's call it 'time'
        self.addBlock(TimeBlock("time"))

        # Add the block that computes the actual sine function
        # Let's call it 'sin'
        self.addBlock(GenericBlock("sin", block_operator="sin"))

        # Connect them together
        self.addConnection("time", "sin", input_port_name='IN1', output_port_name='OUT1')

        # Connect the output port
        self.addConnection("sin", "OUT1", output_port_name='OUT1')


