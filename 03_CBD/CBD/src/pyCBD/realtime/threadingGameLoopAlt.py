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

from threading import Lock

_GL_LOCK = Lock()

class ThreadingGameLoopAlt(object):
    """
    Alternative game loop subsystem for realtime simulation.
    Time will only progress when a :func:`step` call is made.

    The difference with the :class:`pyCBD.realtime.threadingGameLoop.ThreadingGameLoop`
    class is that this version does not use the internal "time" structure to keep
    track of executions. It is up to the used to provide the current simulation time.

    Warning:
        Due to its bare-bone nature, it is pertinent to only use this backend if you
        really know what you're doing.
    """
    def __init__(self):
        self.event_list = []
        self.time = 0.0

    def step(self, time):
        """
        Perform a step in the simulation. Actual processing is done in a seperate thread.
        The clock will only update when this function is called, so call it often enough!

        Args:
            time (float):   The simulation time at which this step is called.
        """
        with _GL_LOCK:
            self.time = time
            while self.time >= self.event_list[0][0]:
                _, func = self.event_list.pop()
                func()
        
    def wait(self, delay, func):
        """
        Wait for the specified time.

        Args:
            delay (float):      Time to wait.
            func (callable):    The function to call.
        """
        self.event_list.append((self.time + delay, func))
