#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   __main__.py -F CBD -e CBDA ..\model_libraries\Models.xml -sSrvg -f -d ..\src\python_models\

from pyCBD.Core import *
from pyCBD.lib.std import *


class CBDA(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['x_a'])

        # Create the Blocks
        self.addBlock(IntegratorBlock("i1"))
        self.addBlock(ConstantBlock("c1", value=(0)))
        self.addBlock(IntegratorBlock("i2"))
        self.addBlock(ConstantBlock("c2", value=(1)))
        self.addBlock(NegatorBlock("n1"))

        # Create the Connections
        self.addConnection("i1", "i2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("c2", "i2", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("c1", "i1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("i2", "n1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("n1", "x_a", output_port_name='OUT1')
        self.addConnection("n1", "i1", output_port_name='OUT1', input_port_name='IN1')


class CBDB(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['x_b'])

        # Create the Blocks
        self.addBlock(DerivatorBlock("d1"))
        self.addBlock(ConstantBlock("c1", value=(0)))
        self.addBlock(DerivatorBlock("d2"))
        self.addBlock(NegatorBlock("n1"))
        self.addBlock(ConstantBlock("c2", value=(1)))

        # Create the Connections
        self.addConnection("c1", "d1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("c2", "d2", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("d2", "n1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("n1", "d1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("n1", "x_b", output_port_name='OUT1')
        self.addConnection("d1", "d2", output_port_name='OUT1', input_port_name='IN1')


class sin_block(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['sin'])

        # Create the Blocks
        self.addBlock(GenericBlock("sinblock", block_operator=("sin")))
        self.addBlock(TimeBlock("t1"))

        # Create the Connections
        self.addConnection("t1", "sinblock", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sinblock", "sin", output_port_name='OUT1')


class Error(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(AbsBlock("lZDvAZIBtNZQrT6GSzD8-75"))
        self.addBlock(AdderBlock("lZDvAZIBtNZQrT6GSzD8-78", numberOfInputs=(2)))
        self.addBlock(NegatorBlock("lZDvAZIBtNZQrT6GSzD8-82"))
        self.addBlock(IntegratorBlock("lZDvAZIBtNZQrT6GSzD8-89"))
        self.addBlock(ConstantBlock("c1", value=(0)))
        self.addBlock(sin_block("sin_block"))

        # Create the Connections
        self.addConnection("IN1", "lZDvAZIBtNZQrT6GSzD8-82", input_port_name='IN1')
        self.addConnection("sin_block", "lZDvAZIBtNZQrT6GSzD8-78", output_port_name='sin', input_port_name='IN2')
        self.addConnection("lZDvAZIBtNZQrT6GSzD8-82", "lZDvAZIBtNZQrT6GSzD8-78", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("lZDvAZIBtNZQrT6GSzD8-78", "lZDvAZIBtNZQrT6GSzD8-75", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("lZDvAZIBtNZQrT6GSzD8-75", "lZDvAZIBtNZQrT6GSzD8-89", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("c1", "lZDvAZIBtNZQrT6GSzD8-89", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("lZDvAZIBtNZQrT6GSzD8-89", "OUT1", output_port_name='OUT1')


class ERROR_B(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['e_b'])

        # Create the Blocks
        self.addBlock(CBDB("cbdb"))
        self.addBlock(Error("error"))

        # Create the Connections
        self.addConnection("cbdb", "error", output_port_name='x_b', input_port_name='IN1')
        self.addConnection("error", "e_b", output_port_name='OUT1')


class ERROR_A(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['e_a'])

        # Create the Blocks
        self.addBlock(CBDA("cbda"))
        self.addBlock(Error("error"))

        # Create the Connections
        self.addConnection("cbda", "error", output_port_name='x_a', input_port_name='IN1')
        self.addConnection("error", "e_a", output_port_name='OUT1')


