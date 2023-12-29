from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
from typing import List
from components.messages import Query, QueryAck, Car
from components.querystate import QueryState
from enum import Enum
from components.roadsegment import RoadSegmentState, RoadSegment
from components.roadsegment import EventEnum

# class EventEnum(Enum):
#     SEND_QUERY = 0
#     RECEIVED_QUERY = 1
#     RECEIVED_ACKNOWLEDGEMENT = 2
#     CAR_OUT = 3


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
        Initializes the Fork.

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
        # if the next event is a car entering, Sends a Query on Q_send as soon as a new Car arrives on this RoadSegment
        if event[0] == EventEnum.SEND_QUERY:
            # get the car if it is still present
            if len(self.state.cars_present) > 0:
                car: Car = self.state.cars_present[0]

                return {
                    self.Q_send: Query(car.ID)
                }

        elif event[0] == EventEnum.RECEIVED_QUERY:
            '''
                Replies a QueryAck to a Query. 
                The QueryAck's t_until_dep equals the remaining time of the current Car on the RoadSegment 
                    (which can be infinity if the Car's velocity is 0). 
                If there is no Car, t_until_dep equals zero. 
                The QueryAck's lane is set w.r.t. the RoadSegment's lane; 
                    and the QueryAck's sideways is set to be false here. 
            '''
            # if there is a car on the road segment
            if len(self.state.cars_present) > 0:
                # get the car
                car: Car = self.state.cars_present[0]
                return {
                    self.Q_sack: QueryAck(car.ID, self.state.t_until_dep, self.lane, False)
                }
        elif event[0] == EventEnum.CAR_OUT:
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
        print(f"emtpy outputFnc")
        return {}
