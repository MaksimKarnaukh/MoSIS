"""
"""

from pypdevs.DEVS import AtomicDEVS, CoupledDEVS, Port
from pypdevs.infinity import INFINITY
import random

from components.messages import QueryAck

class SideMarker(AtomicDEVS):
    """
    Marks all inputted QueryAcks to have sideways set to true.
    It also immediately outputs the inputted events.
    This block should be placed in-between the (Q_sack, Q_rack) connection of two RoadSegments
        if both want to merge onto a third RoadSegment.
    """
    def __init__(self, name):
        """
        :param name: The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(SideMarker, self).__init__(name)

        self.state = {
            "events": []
        }
        # Port that receives QueryAcks.
        self.mi: Port = self.addInPort("mi")
        self.mo: Port = self.addOutPort("mo")

    def timeAdvance(self):
        return INFINITY

    def outputFnc(self):
        # It outputs the QueryAck at once.
        return {
            self.mo: self.state["event"]
        }

    def extTransition(self, inputs):
        # marks all inputted QueryAcks to have sideways set to true. It also immediately outputs the inputted events.
        if self.mi in inputs:
            self.state["event"] = inputs[self.mi]
            self.state["event"].sideways = True
        return self.state
