#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   __main__.py -F CBD -e CBDA ..\model_libraries\PID_Controller.xml -sSrvg -f -d ..\src\python_models\

from PID_Controller import *
from pyCBD.simulator import Simulator


cbd = CBDA("CBDA")

# Run the Simulation
sim = Simulator(cbd)
sim.run(10)

# TODO: Process Your Simulation Results