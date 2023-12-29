from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random
from typing import List
from components.messages import Query, QueryAck, Car
import itertools
from components.querystate import QueryState
from enum import Enum
# set a seed for reproducibility
random.seed(42)



class EventEnum(Enum):
    SEND_QUERY = 0
    RECEIVED_QUERY = 1
    RECEIVED_ACKNOWLEDGEMENT = 2
    CAR_OUT = 3

class RoadSegmentState(object):
    time: float = 0

    def __init__(self, cars_present: List[Car], t_until_dep: float, remaining_x: float):
        """
        :param cars_present (list):
            A list for all the Cars on this RoadSegment.
            Even though the existence of multiple Cars results in a collision,
            for extensibility purposes a list should be used.
        :param t_until_dep (float):
            The time until the current Car (i.e., the first one in cars_present) leaves the RoadSegment.
            If the Car's velocity is 0, this value is infinity. If no Car is present, this value is 0.
        :param remaining_x (float):
            The remaining distance that the current Car (i.e., the first one in cars_present)
            should still travel on this RoadSegment.
        """

        # While the state should contain many more fields, the following three should at least be there.
        self.cars_present: List[Car] = cars_present
        self.t_until_dep: float = t_until_dep
        self.remaining_x: float = remaining_x

        self.next_car: Car = None
        self.ackreceived: bool = False


class RoadSegment(AtomicDEVS):
    """
    Represents a small stretch of road that can only contain a single Car.
    When multiple Cars are on a RoadSegment, we assume the Cars crashed into each other.
    """
    observ_delay_default: float = 0.1
    priority_default: bool = False
    lane_default: int = 0

    def __init__(self, name, L: float, v_max: float, observ_delay: float = observ_delay_default, priority: bool = priority_default, lane: int = lane_default):
        """
        :param name (str):
            The name for this model. Must be unique inside a Coupled DEVS.
        :param L (float):
            The length of the RoadSegment.
            Given that the average Car is about 5 meters in length, a good estimate value for L would therefore be 5 meters.
        :param v_max (float):
            The maximal allowed velocity on this RoadSegment.
        :param observ_delay (float):
            The time it takes to reply to a Query that was inputted.
            This value mimics the reaction time of the driver.
            We can increase the observ_delay to accommodate for bad weather situations (e.g., a lot of fog and/or rain).
            Defaults to 0.1.
        :param priority (bool):
            Whether or not this RoadSegment should have priority on a merge with other road segments.
            Defaults to False.
        :param lane (int):
            Indicator of the lane this Roadsegment is currently part of.
            Defaults to 0.
        """
        super(RoadSegment, self).__init__(name)
        self.state = RoadSegmentState([], None, None)
        self.L: float = L
        self.v_max: float = v_max
        self.observ_delay: float = observ_delay
        self.priority: bool = priority
        self.lane: int = lane

        # All Cars are inputted on this port. As soon as a Car arrives, a Query is outputted over the Q_send port.
        self.car_in = self.addInPort("car_in")
        # Port that receives Query events.
        self.Q_recv = self.addInPort("Q_recv")
        # Port for receiving QueryAck events
        self.Q_rack = self.addInPort("Q_rack")

        # Port for outputting generated cars
        self.car_out = self.addOutPort("car_out")
        # Sends a Query as soon as the newly sampled IAT says so.
        self.Q_send = self.addOutPort("Q_send")
        # Replies a QueryAck to a Query.
        self.Q_sack = self.addOutPort("Q_sack")


    def sortEventQueue(self):
        self.state.event_queue.sort(key=lambda x: x[1])
    def overwriteCarOutTime(self, new_time:float):
        self.state.car_out_event[1] = new_time
        self.sortEventQueue()

    def nextEvent(self):
        """
        :returns: The next event in the event queue and the time it occurs.
        """
        if len(self.state.event_queue) == 0:
            return [None, INFINITY]
        return self.state.event_queue[0]

    def timeAdvance(self):
        next_event = self.nextEvent()
        if not next_event:
            return INFINITY
        next_time = next_event[1]
        return max( 0.0, next_time )

        # todo check
        return self.state.next_time

    def outputFnc(self):

        # throw error
        raise Exception("Invalid state")

    def intTransition(self):
        self.state.time += self.timeAdvance()

        # if there is no next car
        if self.state.gasStationIsAvailable():
            # if there are cars in the queue
            if len(self.state.cars) > 0:
                # if the car with the shortest delay is ready to enter the GasStation
                if self.state.cars[0][0] <= 0.0:
                    self.state.next_car = self.state.cars.pop(0)
                    self.state.query_state = QueryState.NOT_SENT
                    self.state.next_time = 0.0
        else:
            # if there is a next car and it is not queried yet
            if self.state.query_state == QueryState.NOT_SENT:
                # the query has been sent
                self.state.query_state = QueryState.SENT
                # wait for the QueryAck
                self.state.next_time = INFINITY
            # if the query has been sent and acknowledged
            if self.state.query_state == QueryState.ACKNOWLEDGED:
                # the car has left and the query is available again
                self.state.query_state = QueryState.AVAILABLE
                self.state.next_car = None

        return self.state

    def extTransition(self, inputs):
        if self.Q_rack in inputs and self.state.query_state == QueryState.SENT:
            query_ack: QueryAck = inputs[self.Q_rack]
            self.state.next_time = query_ack.t_until_dep
            self.state.query_state = QueryState.ACKNOWLEDGED
        return self.state

    def car_enter(self, car: Car):
        """
        Adds a Car to the RoadSegment.

        :param car (Car):
            The Car that enters the RoadSegment.
            Can be called to pre-fill the RoadSegment with a Car.
        """
        self.state.cars_present.append(car)
        # todo
