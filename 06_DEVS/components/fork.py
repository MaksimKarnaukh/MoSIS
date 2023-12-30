from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
from typing import List
from components.messages import Query, QueryAck, Car
from components.querystate import QueryState
from enum import Enum
from components.roadsegment import RoadSegmentState, RoadSegment
from components.roadsegment import EventEnum


class Fork(RoadSegment):
    """
    A fork in the road.
    Allows Cars to choose between multiple RoadSegments. This allows for a simplified form of "lane switching".
    For the sake of convenience of this assignment, the switching criteria is:
    output a Car over the car_out2 port if its no_gas member is true.
    Given that this block inherits from RoadSegment, all aspects discussed there are also applicable.
    """
    def __init__(self, name, L, v_max):
        """
        :param name (str):
            The name for this model. Must be unique inside a Coupled DEVS.
        :param L (float):
            The length of the RoadSegment.
            Given that the average Car is about 5 meters in length, a good estimate value for L would therefore be 5 meters.
        :param v_max (float):
            The maximal allowed velocity on this RoadSegment.
        """
        super(Fork, self).__init__(name, L, v_max)

        self.car_out2 = self.addOutPort("car_out2")

    def outputFnc(self):
        # get the next event
        event = self.nextEvent()
        # the next event is a car leaving, override the default output function
        if event[0] == EventEnum.CAR_OUT:
            # get the car
            car: Car = self.state.cars_present[0]
            # send the car out
            if car.no_gas:
                return {
                    self.car_out2: car
                }
            else:
                return {
                    self.car_out: car
                }
        # apply the default output function
        return super(Fork, self).outputFnc()


