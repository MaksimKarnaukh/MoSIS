from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random
from typing import List
from components.messages import Query, QueryAck, Car
from enum import Enum

# set a seed for reproducibility
random.seed(42)

class ForkState(object):

    def __init__(self, ):
        pass


class Fork(AtomicDEVS):
    """
    Allows Cars to choose between multiple RoadSegments. This allows for a simplified form of "lane switching". For the sake of convenience of this assignment, the switching criteria is: output a Car over the car_out2 port if its no_gas member is true.
    Given that this block inherits from RoadSegment, all aspects discussed there are also applicable. The description below only focuses on what is new for this component.
    """

    def __init__(self, name, ):
        """
        """
        super(Fork, self).__init__(name)
        self.state = ForkState()
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
