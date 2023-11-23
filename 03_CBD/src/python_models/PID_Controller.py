#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   __main__.py -F CBD -e CBDA ..\model_libraries\PID_Controller.xml -sSrvg -f -d ..\src\python_models\

from pyCBD.Core import *
from pyCBD.lib.std import *


class PID(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN'], output_ports=['OUT'])

        # Create the Blocks
        self.addBlock(ConstantBlock("Constant390", value=(390)))
        self.addBlock(ConstantBlock("Const20", value=(20)))
        self.addBlock(IntegratorBlock("Integrator"))
        self.addBlock(DerivatorBlock("Derrivator"))
        self.addBlock(ProductBlock("Product_Kd", numberOfInputs=(2)))
        self.addBlock(ProductBlock("Product_Ki", numberOfInputs=(2)))
        self.addBlock(ProductBlock("Product_Kp", numberOfInputs=(3)))
        self.addBlock(AdderBlock("Summation", numberOfInputs=(3)))
        self.addBlock(ConstantBlock("Const0", value=(0)))

        # Create the Connections
        self.addConnection("IN", "Derrivator", input_port_name='IN1')
        self.addConnection("IN", "Integrator", input_port_name='IN1')
        self.addConnection("IN", "Product_Kp", input_port_name='IN2')
        self.addConnection("Constant390", "Product_Kp", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("Product_Ki", "Summation", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("Product_Kd", "Summation", output_port_name='OUT1', input_port_name='IN3')
        self.addConnection("Product_Kp", "Summation", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("Const20", "Product_Kd", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("Const20", "Product_Ki", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("Integrator", "Product_Ki", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("Derrivator", "Product_Kd", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("Summation", "OUT", output_port_name='OUT1')
        self.addConnection("Const0", "Integrator", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("Const0", "Derrivator", output_port_name='OUT1', input_port_name='IC')


