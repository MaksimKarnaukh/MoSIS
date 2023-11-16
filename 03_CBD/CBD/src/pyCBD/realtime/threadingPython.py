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

from threading import Thread
from pyCBD.realtime import accurate_time

class ThreadingPython(object):
    """
    Simple Python threads subsystem
    """
    def wait(self, time, func):
        """
        Wait for the specified time before executing :attr:`func`.

        Args:
            time (float):       Time to wait.
            func (callable):    The function to call.
        """
        #NOTE this call has a granularity of 5ms in Python <= 2.7.x in the worst case, so beware!
        #     the granularity seems to be much better in Python >= 3.x
        p = Thread(target=self.run, args=[time, func])
        p.daemon = True
        p.start()

    def run(self, delay, func):
        """
        Function to call on a seperate thread: will block for the
        specified time and call the function afterwards.

        Args:
            delay (float):  The wait delay.
            func:           The function to call. No arguments can be
                            used and no return values are needed.
        """
        accurate_time.sleep(delay)
        func()
