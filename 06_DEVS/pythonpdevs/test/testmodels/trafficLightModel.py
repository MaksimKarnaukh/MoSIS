# -*- coding: Latin-1 -*-
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# trafficLight.py --- simple Traffic Light example
#                       --------------------------------
#                              October 2005
#                             Hans Vangheluwe 
#                         McGill University (Montr�al)
#                       --------------------------------
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

# Add the directory where pydevs lives to Python's import path
import sys

# Import code for DEVS model representation:
from pypdevs.infinity import *
from pypdevs.DEVS import *

# Import for uniform random number generators 
from random import uniform
from random import randint

#    ======================================================================    #

class TrafficLightMode:

  """Encapsulates the system's state
  """

  ###
  def __init__(self, current="red"):
    """Constructor (parameterizable).
    """
    self.set(current)

  def set(self, value="red"):
    self.__colour=value

  def get(self):
    return self.__colour

  def __str__(self):
    return self.get()

class TrafficLight(AtomicDEVS):
  """A traffic light 
  """
  
  ###
  def __init__(self, name=None):
    """Constructor (parameterizable).
    """
    
    # Always call parent class' constructor FIRST:
    AtomicDEVS.__init__(self, name)
    
    # STATE:
    #  Define 'state' attribute (initial sate):
    self.state = TrafficLightMode("red") 

    # PORTS:
    #  Declare as many input and output ports as desired
    #  (usually store returned references in local variables):
    self.INTERRUPT = self.addInPort(name="INTERRUPT")
    self.OBSERVED = self.addOutPort(name="OBSERVED")

  ###
  def extTransition(self, inputs):
    """External Transition Function."""
    
    # Compute the new state 'Snew' based (typically) on current
    # State, Elapsed time parameters and calls to 'self.peek(self.IN)'.
    #input = self.peek(self.INTERRUPT)
    input = inputs[self.INTERRUPT][0]

    state = self.state.get()

    if input == "toManual":
      if state == "manual":
       # staying in manual mode
       return TrafficLightMode("manual")
      if state in ("red", "green", "yellow"):
       return TrafficLightMode("manual")
      else:
       raise DEVSException(\
        "unknown state <%s> in TrafficLight external transition function"\
        % state)
    
    if input == "toAutonomous":
      if state == "manual":
        return TrafficLightMode("red")
      else:
       raise DEVSException(\
        "unknown state <%s> in TrafficLight external transition function"\
        % state) 

    raise DEVSException(\
      "unknown input <%s> in TrafficLight external transition function"\
      % input) 

  ###
  def intTransition(self):
    """Internal Transition Function.
    """

    state = self.state.get()

    if state == "red":
      return TrafficLightMode("green")
    elif state == "green":
      return TrafficLightMode("yellow")
    elif state == "yellow":
      return TrafficLightMode("red")
    else:
      raise DEVSException(\
        "unknown state <%s> in TrafficLight internal transition function"\
        % state)
  
  ###
  def outputFnc(self):
    """Output Funtion.
    """
   
    # A colourblind observer sees "grey" instead of "red" or "green".
 
    # BEWARE: ouput is based on the OLD state
    # and is produced BEFORE making the transition.
    # We'll encode an "observation" of the state the
    # system will transition to !

    # Send messages (events) to a subset of the atomic-DEVS' 
    # output ports by means of the 'poke' method, i.e.:
    # The content of the messages is based (typically) on current State.
 
    state = self.state.get()

    if state == "red":
      return {self.OBSERVED: ["grey"]}
      #self.poke(self.OBSERVED, "grey")
      # NOT self.poke(self.OBSERVED, "grey")
    elif state == "green":
      return {self.OBSERVED: ["yellow"]}
      #self.poke(self.OBSERVED, "yellow")
      # NOT self.poke(self.OBSERVED, "grey")
    elif state == "yellow":
      return {self.OBSERVED: ["grey"]}
      #self.poke(self.OBSERVED, "grey")
      # NOT self.poke(self.OBSERVED, "yellow")
    else:
      raise DEVSException(\
        "unknown state <%s> in TrafficLight external transition function"\
        % state)
    
  ###
  def timeAdvance(self):
    """Time-Advance Function.
    """
    
    # Compute 'ta', the time to the next scheduled internal transition,
    # based (typically) on current State.
    
    state = self.state.get()

    if state == "red":
      return 3
    elif state == "green":
      return 2
    elif state == "yellow":
      return 1
    elif state == "manual":
      return INFINITY 
    else:
      raise DEVSException(\
        "unknown state <%s> in TrafficLight time advance transition function"\
        % state)

#    ======================================================================    #

class PolicemanMode:

  """Encapsulates the Policeman's state
  """

  ###
  def __init__(self, current="idle"):
    """Constructor (parameterizable).
    """
    self.set(current)

  def set(self, value="idle"):
    self.__mode=value

  def get(self):
    return self.__mode

  def __str__(self):
    return self.get()

class Policeman(AtomicDEVS):
  """A policeman producing "toManual" and "toAutonomous" events:
      "toManual" when going from "idle" to "working" mode
      "toAutonomous" when going from "working" to "idle" mode
  """
  
  ###
  def __init__(self, name=None):
    """Constructor (parameterizable).
    """
    
    # Always call parent class' constructor FIRST:
    AtomicDEVS.__init__(self, name)
    
    # STATE:
    #  Define 'state' attribute (initial sate):
    self.state = PolicemanMode("idle") 

    # ELAPSED TIME:
    #  Initialize 'elapsed time' attribute if required
    #  (by default, value is 0.0):
    self.elapsed = 0 
    
    # PORTS:
    #  Declare as many input and output ports as desired
    #  (usually store returned references in local variables):
    self.OUT = self.addOutPort(name="OUT")

  ###
  # Autonomous system (no input ports), 
  # so no External Transition Function required
  #

  ###
  def intTransition(self):
    """Internal Transition Function.
       The policeman works forever, so only one mode. 
    """
  
    state = self.state.get()

    if state == "idle":
      return PolicemanMode("working")
    elif state == "working":
      return PolicemanMode("idle")
    else:
      raise DEVSException(\
        "unknown state <%s> in Policeman internal transition function"\
        % state)
    
  ###
  def outputFnc(self):
    """Output Funtion.
    """
   
    # Send messages (events) to a subset of the atomic-DEVS' 
    # output ports by means of the 'poke' method, i.e.:
    # The content of the messages is based (typically) on current State.
  
    state = self.state.get()

    if state == "idle":
      return {self.OUT: ["toManual"]}
      #self.poke(self.OUT, "toManual")
    elif state == "working":
      return {self.OUT: ["toAutonomous"]}
      #self.poke(self.OUT, "toAutonomous")
    else:
      raise DEVSException(\
        "unknown state <%s> in Policeman output function"\
        % state)
    
  ###
  def timeAdvance(self):
    """Time-Advance Function.
    """
    
    # Compute 'ta', the time to the next scheduled internal transition,
    # based (typically) on current State.
    
    state = self.state.get()

    if state == "idle":
      return 200
    elif state == "working":
      return 100
    else:
      raise DEVSException(\
        "unknown state <%s> in Policeman time advance function"\
        % state)

#    ======================================================================    #

class TrafficSystem(CoupledDEVS):

  def __init__(self, name=None):
    """ A simple traffic system consisting of a Policeman and a TrafficLight.
    """

    # Always call parent class' constructor FIRST:
    CoupledDEVS.__init__(self, name)

    # Declare the coupled model's output ports:
    # Autonomous, so no output ports
    #self.OUT = self.addOutPort(name="OUT")

    # Declare the coupled model's sub-models:

    # The Policeman generating interrupts 
    self.policeman = self.addSubModel(Policeman(name="policeman"))

    # The TrafficLight 
    self.trafficLight = self.addSubModel(TrafficLight(name="trafficLight"))

    # Only connect ...
    self.connectPorts(self.policeman.OUT, self.trafficLight.INTERRUPT)
    #self.connectPorts(self.trafficLight.OBSERVED, self.OUT)

  def select(self, immList):
    """Give the Policeman highest priority.
       Note how the technique used below can
       be generalized to encode priorities based on model type.
       To distinguish between models of the same type,
       the name or unique ID should be used.
    """
    # return the first Policeman instance in the immList
    for i in range(len(immList)):
      #if immList[i].__class__ == TrafficLight:
      if immList[i].__class__ == Policeman:
        return immList[i]
    
    # if no Policeman instances found, return the last entry
    return immList[-1]

    # Alternative: randomly choose among imminent submodels
    #return immList[randint(0,len(immList))]

    # If the select method is not defined, the immList[0] 
    # will be chosen by default.

#    ======================================================================    #

