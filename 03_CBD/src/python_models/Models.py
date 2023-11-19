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


class TrapezoidIntegrator(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IC', 'IN1'], output_ports=['trap_int'])

        # Create the Blocks
        self.addBlock(DelayBlock("O5fMZ6u50ew7LmOudeCE-66"))
        self.addBlock(ConstantBlock("O5fMZ6u50ew7LmOudeCE-70", value=(0)))
        self.addBlock(AdderBlock("O5fMZ6u50ew7LmOudeCE-73", numberOfInputs=(2)))
        self.addBlock(ProductBlock("O5fMZ6u50ew7LmOudeCE-78", numberOfInputs=(3)))
        self.addBlock(AdderBlock("O5fMZ6u50ew7LmOudeCE-98", numberOfInputs=(2)))
        self.addBlock(DelayBlock("O5fMZ6u50ew7LmOudeCE-107"))
        self.addBlock(DeltaTBlock("kiNdS1_nELwOXWvILFVc-3"))
        self.addBlock(ConstantBlock("kiNdS1_nELwOXWvILFVc-7", value=(2)))
        self.addBlock(InverterBlock("uFovl10BGIAzvapy5D29-43"))
        self.addBlock(ProductBlock("uFovl10BGIAzvapy5D29-109", numberOfInputs=(3)))
        self.addBlock(NegatorBlock("uFovl10BGIAzvapy5D29-115"))
        self.addBlock(AdderBlock("uFovl10BGIAzvapy5D29-121", numberOfInputs=(2)))

        # Create the Connections
        self.addConnection("IC", "uFovl10BGIAzvapy5D29-121", input_port_name='IN2')
        self.addConnection("IN1", "O5fMZ6u50ew7LmOudeCE-66", input_port_name='IN1')
        self.addConnection("IN1", "uFovl10BGIAzvapy5D29-109", input_port_name='IN1')
        self.addConnection("IN1", "O5fMZ6u50ew7LmOudeCE-98", input_port_name='IN2')
        self.addConnection("O5fMZ6u50ew7LmOudeCE-70", "O5fMZ6u50ew7LmOudeCE-66", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("O5fMZ6u50ew7LmOudeCE-78", "O5fMZ6u50ew7LmOudeCE-73", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("O5fMZ6u50ew7LmOudeCE-66", "O5fMZ6u50ew7LmOudeCE-98", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("O5fMZ6u50ew7LmOudeCE-98", "O5fMZ6u50ew7LmOudeCE-78", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("O5fMZ6u50ew7LmOudeCE-73", "O5fMZ6u50ew7LmOudeCE-107", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("O5fMZ6u50ew7LmOudeCE-73", "trap_int", output_port_name='OUT1')
        self.addConnection("kiNdS1_nELwOXWvILFVc-3", "O5fMZ6u50ew7LmOudeCE-78", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("kiNdS1_nELwOXWvILFVc-3", "uFovl10BGIAzvapy5D29-115", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("kiNdS1_nELwOXWvILFVc-7", "uFovl10BGIAzvapy5D29-43", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("uFovl10BGIAzvapy5D29-43", "O5fMZ6u50ew7LmOudeCE-78", output_port_name='OUT1', input_port_name='IN3')
        self.addConnection("uFovl10BGIAzvapy5D29-43", "uFovl10BGIAzvapy5D29-109", output_port_name='OUT1', input_port_name='IN3')
        self.addConnection("O5fMZ6u50ew7LmOudeCE-107", "O5fMZ6u50ew7LmOudeCE-73", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("uFovl10BGIAzvapy5D29-115", "uFovl10BGIAzvapy5D29-109", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("uFovl10BGIAzvapy5D29-121", "O5fMZ6u50ew7LmOudeCE-107", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("uFovl10BGIAzvapy5D29-109", "uFovl10BGIAzvapy5D29-121", output_port_name='OUT1', input_port_name='IN1')


class ForwardEulerIntegrator(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IC', 'IN1'], output_ports=['forward_int'])

        # Create the Blocks
        self.addBlock(AdderBlock("add2", numberOfInputs=(2)))
        self.addBlock(DelayBlock("delay1"))
        self.addBlock(AdderBlock("add1", numberOfInputs=(2)))
        self.addBlock(ProductBlock("XYqq4OHtO8QmNKRPjIp4-5", numberOfInputs=(2)))
        self.addBlock(ProductBlock("XYqq4OHtO8QmNKRPjIp4-1", numberOfInputs=(2)))
        self.addBlock(DeltaTBlock("XYqq4OHtO8QmNKRPjIp4-9"))
        self.addBlock(NegatorBlock("XYqq4OHtO8QmNKRPjIp4-11"))

        # Create the Connections
        self.addConnection("IN1", "XYqq4OHtO8QmNKRPjIp4-1", input_port_name='IN1')
        self.addConnection("IN1", "XYqq4OHtO8QmNKRPjIp4-5", input_port_name='IN1')
        self.addConnection("add2", "delay1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("add2", "forward_int", output_port_name='OUT1')
        self.addConnection("delay1", "add2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("add1", "delay1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("IC", "add1", input_port_name='IN1')
        self.addConnection("XYqq4OHtO8QmNKRPjIp4-9", "XYqq4OHtO8QmNKRPjIp4-11", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("XYqq4OHtO8QmNKRPjIp4-9", "XYqq4OHtO8QmNKRPjIp4-1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("XYqq4OHtO8QmNKRPjIp4-5", "add1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("XYqq4OHtO8QmNKRPjIp4-1", "add2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("XYqq4OHtO8QmNKRPjIp4-11", "XYqq4OHtO8QmNKRPjIp4-5", output_port_name='OUT1', input_port_name='IN2')


class g_t(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['gt'])

        # Create the Blocks
        self.addBlock(TimeBlock("time1"))
        self.addBlock(ConstantBlock("constminus1", value=(-1)))
        self.addBlock(AdderBlock("add1", numberOfInputs=(2)))
        self.addBlock(InverterBlock("div1"))
        self.addBlock(ConstantBlock("const1", value=(1)))
        self.addBlock(AdderBlock("add2", numberOfInputs=(2)))
        self.addBlock(PowerBlock("pow1"))
        self.addBlock(ConstantBlock("const2", value=(2)))
        self.addBlock(ProductBlock("prod1", numberOfInputs=(2)))

        # Create the Connections
        self.addConnection("constminus1", "add1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("time1", "add1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("time1", "add2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("const1", "add2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("add2", "pow1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("const2", "pow1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("pow1", "div1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("div1", "prod1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("add1", "prod1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("prod1", "gt", output_port_name='OUT1')


class g_tComp(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['gt_TR', 'gt_FE', 'gt_BE'])

        # Create the Blocks
        self.addBlock(ConstantBlock("const2", value=(0)))
        self.addBlock(g_t("gt"))
        self.addBlock(ForwardEulerIntegrator("forward_euler_integrator"))
        self.addBlock(BackwardEulerIntegrator("backward_euler_integrator"))
        self.addBlock(TrapezoidIntegrator("Trap"))

        # Create the Connections
        self.addConnection("gt", "forward_euler_integrator", output_port_name='gt', input_port_name='IN1')
        self.addConnection("gt", "backward_euler_integrator", output_port_name='gt', input_port_name='IN1')
        self.addConnection("gt", "Trap", output_port_name='gt', input_port_name='IN1')
        self.addConnection("const2", "forward_euler_integrator", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("const2", "backward_euler_integrator", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("const2", "Trap", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("forward_euler_integrator", "gt_FE", output_port_name='forward_int')
        self.addConnection("backward_euler_integrator", "gt_BE", output_port_name='backward_int')
        self.addConnection("Trap", "gt_TR", output_port_name='trap_int')


class BackwardEulerIntegrator(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IC', 'IN1'], output_ports=['backward_int'])

        # Create the Blocks
        self.addBlock(ConstantBlock("uFovl10BGIAzvapy5D29-12", value=(0)))
        self.addBlock(DelayBlock("uFovl10BGIAzvapy5D29-14"))
        self.addBlock(ProductBlock("uFovl10BGIAzvapy5D29-20", numberOfInputs=(2)))
        self.addBlock(DeltaTBlock("uFovl10BGIAzvapy5D29-24"))
        self.addBlock(AdderBlock("uFovl10BGIAzvapy5D29-28", numberOfInputs=(2)))
        self.addBlock(DelayBlock("uFovl10BGIAzvapy5D29-33"))

        # Create the Connections
        self.addConnection("IN1", "uFovl10BGIAzvapy5D29-14", input_port_name='IN1')
        self.addConnection("IC", "uFovl10BGIAzvapy5D29-33", input_port_name='IC')
        self.addConnection("uFovl10BGIAzvapy5D29-14", "uFovl10BGIAzvapy5D29-20", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("uFovl10BGIAzvapy5D29-24", "uFovl10BGIAzvapy5D29-20", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("uFovl10BGIAzvapy5D29-28", "uFovl10BGIAzvapy5D29-33", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("uFovl10BGIAzvapy5D29-28", "backward_int", output_port_name='OUT1')
        self.addConnection("uFovl10BGIAzvapy5D29-20", "uFovl10BGIAzvapy5D29-28", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("uFovl10BGIAzvapy5D29-33", "uFovl10BGIAzvapy5D29-28", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("uFovl10BGIAzvapy5D29-12", "uFovl10BGIAzvapy5D29-14", output_port_name='OUT1', input_port_name='IC')


