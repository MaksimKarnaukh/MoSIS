from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random
from typing import List
from components.messages import Query, QueryAck, Car
import itertools
from enum import Enum

# set a seed for reproducibility
random.seed(42)


class QueryState(Enum):
    NOT_SENT = 1
    SENT = 2
    ACKNOWLEDGED = 3


class GeneratorState(object):
    # Constants for the maximum allowed acceleration and deceleration.
    dv_neg_max: float = 21.0
    dv_pos_max: float = 28.0
    time: float = 0
    next_time: float = 0.0
    generated_car_count: int = 0
    query_state: QueryState = QueryState.NOT_SENT

    def __init__(self, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit):
        self.IAT_min: float = IAT_min
        self.IAT_max: float = IAT_max
        self.v_pref_mu: float = v_pref_mu
        self.v_pref_sigma: float = v_pref_sigma
        self.destinations: List[str] = destinations
        self.limit: int = limit

        self.next_car: Car = None

        self.ackreceived: bool = False


class RoadSegment(AtomicDEVS):
    """
    """

    # The unique incremental identifier for the cars.
    id_iter = itertools.count()

    def __init__(self, name, ):
        """
        """
        super(Generator, self).__init__(name)
        self.state = GeneratorState()
        # Port for receiving QueryAck events
        self.Q_rack = self.addInPort("Q_rack")
        # Port for outputting generated cars
        self.car_out = self.addOutPort("car_out")
        # Sends a Query as soon as the newly sampled IAT says so.
        self.Q_send = self.addOutPort("Q_send")

    def timeAdvance(self):
        return self.state.next_time

    def outputFnc(self):
        # Outputs the newly generated Car.
        if self.state.next_car is None:
            return {
            }
        # if a car is generated, but not queried yet
        elif self.state.query_state == QueryState.NOT_SENT:

            # send the query
            return {self.Q_send: Query(self.state.next_car.ID),

                    }
        # if a car is generated and acknowledged
        elif self.state.query_state == QueryState.ACKNOWLEDGED:
            # send the car
            return {
                self.car_out: self.state.next_car,
            }
        # throw error
        raise Exception("Invalid state")

    def intTransition(self):
        self.state.time += self.timeAdvance()
        # if the car is created yet
        if self.state.next_car is not None:
            # but not queried yet, it is now sent
            if self.state.query_state == QueryState.NOT_SENT:
                self.state.query_state = QueryState.SENT
                self.state.next_time = INFINITY
            # elif a car is generated and acknowledged, it is now neither
            elif self.state.query_state == QueryState.ACKNOWLEDGED:
                self.state.query_state = QueryState.NOT_SENT
                self.state.next_car = None
                # next time is the IAT of the next car
                self.state.next_time = random.uniform(self.state.IAT_min, self.state.IAT_max)
        # if the car has not been created yet
        else:
            self.state.query_state = QueryState.NOT_SENT
            # if the count is under the limit, create a new one
            if self.state.generated_car_count < self.state.limit:
                self.state.next_car = self.createCar()
                self.state.next_time = 0.0
            # else, there is no next_car and the count is over the limit, so do nothing
            else:
                self.state.next_car = None
                self.state.next_time = INFINITY
        return self.state

    def extTransition(self, inputs):
        if self.Q_rack in inputs and self.state.query_state == QueryState.SENT:
            query_ack: QueryAck = inputs[self.Q_rack]
            self.state.next_time = query_ack.t_until_dep
            self.state.query_state = QueryState.ACKNOWLEDGED
        return self.state
