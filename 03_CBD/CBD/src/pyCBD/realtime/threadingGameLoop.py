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

import pyCBD.realtime.accurate_time as time
from threading import Lock

_GL_LOCK = Lock()

class ThreadingGameLoop(object):
    """
    Game loop subsystem for realtime simulation.
    Time will only progress when a :func:`step` call is made.
    """
    def __init__(self):
        self.event_list = []

    def step(self):
        """
        Perform a step in the simulation.
        """
        with _GL_LOCK:
            now = time.time()
            while now >= self.event_list[0][0]:
                _, func = self.event_list.pop()
                func()
        
    def wait(self, delay, func):
        """
        Wait for the specified time, or faster if interrupted

        Args:
            delay (float):      Time to wait.
            func (callable):    The function to call.
        """
        self.event_list.append((time.time() + delay, func))
