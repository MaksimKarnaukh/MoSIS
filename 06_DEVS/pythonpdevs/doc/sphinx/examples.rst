..
    Copyright 2014 Modelling, Simulation and Design Lab (MSDL) at 
    McGill University and the University of Antwerp (http://msdl.cs.mcgill.ca/)

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Examples for Parallel DEVS
==========================

A small *trafficModel* and corresponding *trafficExperiment* file is included in the *examples* folder of the PyPDEVS distribution. This (completely working) example is slightly too big to use as a first introduction to PyPDEVS and therefore this page will start with a very simple example.

For this, we will first introduce a simplified queue model, which will be used as the basis of all our examples. The complete model can be downloaded: :download:`queue_example.py <queue_example.py>`.

This section should provide you with all necessary information to get you started with creating your very own PyPDEVS simulation. More advanced features are presented in the next section.

Generator
---------

Somewhat simpler than a queue even, is a generator. It will simply create a message to send after a certain delay and then it will stop doing anything.

Informally, this would result in a DEVS specification as:

* Time advance function returns the waiting time to generate the message, infinity after the message was created
* Output function outputs the generated message
* Internal transition function marks the generator as done
* External transition function will never happen (as there are no inputs)
* Confluent transition function will never happen (as no external transition will ever happen)

In PythonPDEVS, this simply becomes the class::

    class Generator(AtomicDEVS):
        def __init__(self):
            AtomicDEVS.__init__(self, "Generator")
            self.state = True
            self.outport = self.addOutPort("outport")

        def timeAdvance(self):
            if self.state:
                return 1.0
            else:
                return INFINITY

        def outputFnc(self):
            # Our message is simply the integer 5, though this could be anything
            # It is mandatory to output lists (which signify the 'bag')
            return {self.outport: [5]}

        def intTransition(self):
            self.state = False
            return self.state

Note that all functions have a *default* behaviour, which is sufficient if the function will never be called. In most situations, the *confTransition* function is sufficient and rarely requires to be overwritten.

It is possible to simulate this model, though nothing spectacular will happen. For this reason, we will postpone actual simulation examples.

Simple queue
------------

To couple the *Generator* model up to something useful, we will now create a simple queue model. It doesn't do any real computation and just forwards the message after a certain (fixed) time delay. For simplicity, we allow the queue to *drop* the previous message if a message was already being processed.

Informally, this would result in a DEVS specification as:

* Time advance function returns the processing time if a message is being processed, or INFINITY otherwise
* Output function outputs the message
* Internal transition function removes the message from the queue
* External transition function adds the message to the queue
* Confluent transition function can simply default to the internal transition function, immeditaly followed by the external transition function

To implement this in PythonPDEVS, one simply has to write::

  class Queue(AtomicDEVS):
    def __init__(self):
        AtomicDEVS.__init__(self, "Queue")
        self.state = None
        self.processing_time = 1.0
        self.inport = self.addInPort("input")
        self.outport = self.addOutPort("output")

    def timeAdvance(self):
        if self.state is None:
            return INFINITY
        else:
            return self.processing_time

    def outputFnc(self):
        return {self.outport: [self.state]}

    def extTransition(self, inputs):
        # To access them, you will need to access each element seperately
        # In this case, we only use the first element from the bag as we
        # know that it will only contain one element
        self.state = inputs[self.inport][0]
        return self.state

    def intTransition(self):
        self.state = None
        return self.state
    
And we are done with our basic queue model. 

However, there is currently no means of testing it, as simply simulating this model will have no effect, due to no messages arriving. We will thus have to couple it with the *Generator* we previously made.

Coupling
--------

To couple up the *Generator* to the *Queue*, all we have to do is create a *CoupledDEVS* class and simulate this class::

    class CQueue(CoupledDEVS):
        def __init__(self):
            CoupledDEVS.__init__(self, "CQueue")
            self.generator = self.addSubModel(Generator())
            self.queue = self.addSubModel(Queue())
            self.connectPorts(self.generator.outport, self.queue.inport)

That is all for the coupled model. Note that it is not required for every port of a model to be connected to another port. For example the *outport* of the *Queue* is not connected. Any output that is put on this port is thus discarded.

It is perfectly allowed to do model construction and connection in e.g. a loop or conditionally, as long as the required functions are called.

.. note:: The DEVS formalism allows for an input-to-output translation function, but this is not implemented in PythonPDEVS.

Simulation
----------

Now that we have an actual coupled model that does something remotely useful, it is time to simulate it. Simulation is as simple as constructing a *Simulator* object with the model and calling *simulate()* on the simulator::

    model = CQueue()
    sim = Simulator(model)
    sim.simulate()

Sadly, nothing seems to happen because no tracers are enabled. Note that it is possible to access the attributes of the model and see that they are actually changed as directed by the simulation::
    
    model = CQueue()
    print(model.generator.state)
    sim = Simulator(model)
    sim.simulate()
    print(model.generator.state)

This code will simply print *True* in the beginning and *False* at the end, since the model is updated in-place in this situation. The model will **not** be simulated in-place if either simulation is distributed, or reinitialisation is enabled.

Tracing
-------

To actually see some results from the simulation, it is advised to enable certain tracers. The simplest tracer is the *verbose* tracer, which will output some details in a human-readable format. Enabling the verbose tracer is as simple as setting the *setVerbose()* configuration to a destination file. For the verbose tracer, it is also possible to trace to stdout by using the *None* argument::

    model = CQueue()
    sim = Simulator(model)
    sim.setVerbose(None)
    sim.simulate()

Saving the output to a file can de done by passing the file name as a string. Note that a file handle does **not** work::

    model = CQueue()
    sim = Simulator(model)
    sim.setVerbose("myOutputFile")
    sim.simulate()

Multiple tracers can be defined simultaneously, all of which will be used. So to trace to the files *myOutputFile* and *myOutputFile* and simultaneously output to stdout, you could use::

    model = CQueue()
    sim = Simulator(model)
    sim.setVerbose("myOutputFile")
    sim.setVerbose(None)
    sim.setVerbose("myOutputFile2")
    sim.simulate()

.. note:: There is no way to unset a single tracer. There is however a way to remove all currently registered tracers: *setRemoveTracers()*, though it is generally only useful in reinitialized simulations.

An example output of the *verbose* tracer is::

    __  Current Time:       0.00 __________________________________________

        INITIAL CONDITIONS in model <CQueue.Generator>
        Initial State: True
        Next scheduled internal transition at time 1.00

        INITIAL CONDITIONS in model <CQueue.Queue>
        Initial State: None
        Next scheduled internal transition at time inf

    __  Current Time:       1.00 __________________________________________

        EXTERNAL TRANSITION in model <CQueue.Queue>
        Input Port Configuration:
            port <input>:
                5
        New State: 5
        Next scheduled internal transition at time 2.00

        INTERNAL TRANSITION in model <CQueue.Generator>
        New State: False
        Output Port Configuration:
            port <outport>:
                5
        Next scheduled internal transition at time inf

    __  Current Time:       2.00 __________________________________________

        INTERNAL TRANSITION in model <CQueue.Queue>
        New State: None
        Output Port Configuration:
            port <output>:
                5
        Next scheduled internal transition at time inf

.. note:: Several other tracers are available, such as *VCD*, *XML* and *Cell*. Their usage is very similar and is only useful in several situations. Only the *Cell* tracer requires further explanation and is mentioned in the *Advanced examples* section.

Termination
-----------

Our previous example stopped simulation automatically, since both models returned a time advance equal to infinity.

In several cases, it is desired to stop simulation after a certain period. The simplest example of this is when the *Generator* would keep generating messages after a certain delay. Without a termination condition, the simulation will keep going forever.

Adding a termination time is as simple as setting one additional configuration option::
    
    sim.setTerminationTime(5.0)

This will make the simulation stop as soon as simulation time 5.0 is reached. 

A termination time is sufficient in most situations, though it is possible to use a more advanced approach: using a termination function. Using the option::

    sim.setTerminationCondition(termFunc)

With this additional option, the function *termFunc* will be evaluated at every timestep. If the function returns *True*, simulation will stop. The function will receive 2 parameters from the simulator: the model being simulated and the current simulation time.

Should our generator save the number of messages it has generated, an example of such a termination function could be::

    def termFunc(clock, model):
        if model.generator.generated > 5:
            # The generator has generated more than 5 events
            # So stop
            return True
        elif clock[0] > 10:
            # Or if the clock has progressed past simulation time 10
            return True
        else:
            # Otherwise, we simply continue
            return False

The *clock* parameter in the termination condition will be a **tuple** instead of a simple floating point number. The first field of the tuple is the current simulation time (and can be used as such). The second field is a so-called *age* field, containing the number of times the same simulation time has occured. This is passed on in the termination condition as it is required in some cases for distributed simulation.

.. note:: Using a termination function is a lot slower than simply using a termination time. This option should therefore be avoided if at all possible.

.. warning:: It is **only** allowed to read from the model in the termination function. Performing write actions to the model has unpredictable consequences!

.. warning:: Running a termination function in a distributed simulation is slightly different, so please refer to the advanced section for this!

Simulation time
---------------

Accessing the global simulation time is a frequent operation, though it is not supported by DEVS out-of-the-box. Of course, the simulator internally keeps such a clock, though this is not meant to be accessed by the user directly as it is an implementation detail of PyPDEVS (and it might even change between releases!).

If you require access to the simulation time, e.g. to put a timestamp on a message, this can be done by writing some additional code in the model that requires this time as follows::

    class MyModelState():
        def __init__(self):
            self.actual_state = ...
            self.current_time = 0.0
        
    class MyModel(AtomicDEVS):
        def __init__(self, ...):
            AtomicDEVS.__init__(self, "ExampleModel")
            self.state = MyModelState()
            ...

        def extTransition(self, inputs):
            self.state.current_time += self.elapsed
            ...
            return self.state

        def intTransition(self):
            self.state.current_time += self.timeAdvance()
            ...
            return self.state

        def confTransition(self, inputs):
            self.state.current_time += self.timeAdvance()
            ...
            return self.state

In the *extTransition* method, we use the *elapsed* attribute to determine the time between the last transition and the current transition. However, in the *intTransition* we are **not** allowed to access it.
A more detailed explanation can be found at :ref:`elapsed_time`.

You are allowed to call the *timeAdvance* method again, as this is the time that was waited before calling the internal transition function (as defined in the DEVS formalism).
This requires, however, that your timeAdvance is deterministic (as it should be).
Deterministic timeAdvance functions are not trivial if you use random numbers, for which you should read up on :ref:`random_numbers` in PythonPDEVS.
