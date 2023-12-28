from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random
from typing import List, Dict
from components.messages import Query, QueryAck, Car
from enum import Enum

# set a seed for reproducibility
random.seed(42)


class QueryState(Enum):
    AVAILABLE = 1
    NOT_SENT = 2
    SENT = 3
    ACKNOWLEDGED = 4





class GasStationState(object):
    delay_dist_mean: float = 600.0
    delay_dist_std: float = 130.0
    minimum_car_stay: float = 120.0


    def __init__(self, observ_delay):
        self.query_state = QueryState.AVAILABLE
        self.observ_delay: float = observ_delay
        self.next_time: float = 0.0
        self.time: float = 0.0
        self.cars: List[Car] = []
        self.next_car: Car = None


    def carArrived(self, car:Car, delay_time):
        self.cars.append([delay_time, car])
        # Sort the cars by their delay time low to high
        self.cars.sort(key=lambda x: x[0])

    def decreaseCarDelays(self, elapsed_time):
        """
        Handles the elapsed time of the car delays
        :param elapsed_time: The elapsed time
        """
        for i in range(len(self.cars)):
            # self.cars is a list of tuples (delay, car)
            self.cars[i][0] -= elapsed_time

    def gasStationIsAvailable(self):
        return self.next_car is None

class GasStation(AtomicDEVS):
    """
    Represents the notion that some Cars need gas.
    It can store an infinite amount of Cars, who stay for a certain delay inside an internal queue.
    This component can be available (default) or unavailable, as described below.
    """

    """
    TODO
        in car_in port As soon as one is entered, it is given a delay time, 
        sampled from a normal distribution with mean 10 minutes and standard deviation of 130 seconds. 
        Cars are required to stay at least 2 minutes in the GasStation. 
        When this delay has passed and when this component is available, a Query is sent over the Q_send port. 
        
        When a QueryAck is received, the GasStation waits for QueryAck's t_until_dep time before outputting the next Car over the car_out output. 
        Only then, this component becomes available again. If the waiting time is infinite, the GasStation keeps polling until it becomes finite again. 
        
        Q_send: Sends a Query as soon as a Car has waited its delay. Next, this component becomes unavailable, preventing collisions on the RoadSegment after. 
        
        car_out: Outputs the Cars, with no_gas set back to false.      
              
    """
    def __init__(self, name, observ_delay=0.1):
        """
        :param name: The name for this model. Must be unique inside a Coupled DEVS.
        :param observ_delay:
            The interval at which the GasStation must poll if the received QueryAck has an infinite delay.
            Defaults to 0.1.
        """
        super(GasStation, self).__init__(name)
        self.state = GasStationState(observ_delay)

        # Cars can enter the GasStation via this port.
        self.car_in = self.addInPort("car_in")
        # Port for receiving QueryAck events
        self.Q_rack = self.addInPort("Q_rack")

        # Port for outputting generated cars
        self.car_out = self.addOutPort("car_out")
        # Sends a Query as soon as the newly sampled IAT says so.
        self.Q_send = self.addOutPort("Q_send")

    def timeAdvance(self):

        # return the delay of the first car
        if len(self.state.cars) > 0:
            return self.state.cars[0][0]
        return INFINITY


    def outputFnc(self):
        # if self.state.next_car is None:
        #     return {}
        if self.state.query_state == QueryState.NOT_SENT and not self.state.gasStationIsAvailable():
            return {
                self.Q_send: Query(self.state.next_car[1].ID),
            }

        elif self.state.query_state == QueryState.ACKNOWLEDGED:
            return {
                self.car_out: self.state.next_car,
            }
        else:
            return {}

    def intTransition(self):
        self.state.time += self.timeAdvance()

        # decrease the delay of every car by self.elapsed
        self.state.decreaseCarDelays(self.timeAdvance())

        # if there is no next car and there are cars in the queue
        if self.state.gasStationIsAvailable():
            if len(self.state.cars) > 0:
                first_car = self.state.cars[0]
                # if the car with the shortest delay is ready to enter the GasStation
                if first_car[0] <= 0.0:
                    self.state.next_car = first_car
                    self.car_out = self.state.cars.pop(0)
                    self.state.query_state = QueryState.NOT_SENT
                    self.state.next_time = 0.0
                # if the car with the shortest delay is not ready to enter the GasStation
                else:
                    self.state.next_time = first_car[0]
        else:
            # if there is a next car and it is not queried yet
            if self.state.query_state == QueryState.NOT_SENT:
                # send the query
                self.state.query_state = QueryState.SENT
                self.state.next_time = INFINITY
        return self.state

    def extTransition(self, inputs):
        self.state.time += self.timeAdvance()

        # decrease the delay of every car by self.elapsed
        self.state.decreaseCarDelays(self.elapsed)

        # A car arrives at the GasStation
        if self.car_in in inputs:
            # As soon as one is entered, it is given a delay time,
            # sampled from a normal distribution with mean 10 minutes and standard deviation of 130 seconds
            # A car is required to stay at least 2 minutes in the GasStation.
            delay_time = min(self.state.minimum_car_stay, random.normalvariate(self.state.delay_dist_mean, self.state.delay_dist_std))
            self.state.carArrived(inputs[self.car_in], delay_time)

            self.state.next_time = delay_time

        elif self.Q_rack in inputs:
            # When a QueryAck is received, the GasStation waits for QueryAck's t_until_dep time
            # before outputting the next Car over the car_out output.
            self.state.next_time = inputs[self.Q_rack].t_until_dep
            self.state.query_state = QueryState.AVAILABLE
            if self.state.next_time == INFINITY:
                self.state.next_time = self.state.observ_delay
                self.state.query_state = QueryState.NOT_SENT

        return self.state
