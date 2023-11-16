# Copyright 2014 Modelling, Simulation and Design Lab (MSDL) at 
# McGill University and the University of Antwerp (http://msdl.cs.mcgill.ca/)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class ThreadingTkInter:
    """
    Tk Inter subsystem for realtime simulation.

    Args:
        tk: TkInter root element.
    """
    def __init__(self, tk):
        self.tk = tk

    def wait(self, time, func):
        """
        Wait for the specified time to execute :attr:`func`.

        Args:
            time (float):       Time to wait.
            func (callable):    The function to call.
        """
        if time == float("inf"): return   # Undefined behaviour for CBD
        self.tk.after(int(time * 1000), func)
