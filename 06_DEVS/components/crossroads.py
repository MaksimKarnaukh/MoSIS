from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
from typing import List
from components.messages import Query, QueryAck, Car
from components.querystate import QueryState
from enum import Enum
from components.roadsegment import RoadSegmentState, RoadSegment
from components.roadsegment import EventEnum


class CrossRoadSegment(RoadSegment):
    """
    Acts as if it were a part of a crossroads. I.e.,
    this is a location where two roads merge and split at the same time.
    Combining multiple of these segments together results in a CrossRoad.
    Given that this block inherits from RoadSegment, all aspects discussed there are also applicable.
    """
    def __init__(self, name, destinations: List[str]):
        """
        :param name (str):
            The name for this model. Must be unique inside a Coupled DEVS.
        :param destinations (list):
            A non-empty list of potential (string) destinations for the Cars.
        """
        super(CrossRoadSegment, self).__init__(name, destinations=destinations)

        # Cars can enter on this segment as if it were the normal car_in port.
        # However, this port is only used for Cars that were already on the crossroads.
        self.car_in_cr = self.addInPort("car_in_cr")

        # Outputs the Cars that must stay on the crossroads.
        # In essence, these are all the Cars that have a destination not in this CrossRoadSegment's destinations field.
        self.car_out_cr = self.addOutPort("car_out_cr")
