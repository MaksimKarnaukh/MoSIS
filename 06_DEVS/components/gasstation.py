from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random
from typing import List, Dict
from components.messages import Query, QueryAck, Car
from components.querystate import QueryState
# set a seed for reproducibility
random.seed(42)


class GasStationState(object):

    # Constants for delay time distribution
    delay_dist_mean: float = 600.0
    delay_dist_std: float = 130.0

    minimum_car_stay: float = 120.0 # cars are required to stay at least 2 minutes in the GasStation.

    def __init__(self, observ_delay):
        """
        :param observ_delay:
            The interval at which the GasStation must poll if the received QueryAck has an infinite delay.
            Defaults to 0.1.
        """
        self.query_state = QueryState.AVAILABLE
        self.observ_delay: float = observ_delay
        self.next_time: float = 0.0
        self.time: float = 0.0
        self.cars: List[Car] = []
        self.next_car: Car = None
        self.nr_cars_passed: int = 0
        self.nr_total_delay: float = 0.0


    def carArrived(self, car:Car, delay_time):
        """
        car has arrived at the gas station with a delay time
        Adds the car to the queue and sorts the queue by remaining delay time
        :param car: The car that has arrived
        :param delay_time: The delay time
        """
        self.cars.append([delay_time, car])
        # Sort the cars by their delay time low to high
        self.cars.sort(key=lambda x: x[0])

    def decreaseCarDelays(self, elapsed_time):
        """
        decreases the delay of every car by elapsed_time
        :param elapsed_time: The elapsed time
        """
        for i in range(len(self.cars)):
            # self.cars is a list of tuples (delay, car)
            self.cars[i][0] -= elapsed_time

    def gasStationIsAvailable(self):
        """
        returns True if the GasStation is available, False otherwise (no car is currently being queried)
        """
        return self.next_car is None

    def __repr__(self):
        return ""


class GasStation(AtomicDEVS):
    """
    Represents the notion that some Cars need gas.
    It can store an infinite amount of Cars, who stay for a certain delay inside an internal queue.
    This component can be available (default) or unavailable, as described below.
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
        if self.state.gasStationIsAvailable():
            # return the delay of the first car
            if len(self.state.cars) > 0:
                # return the delay of the first car if it is positive
                # otherwise return 0.0
                return max(0.0, self.state.cars[0][0])
            # return infinity and wait for a car to arrive
            return INFINITY
        # specified variable time
        return self.state.next_time

    def outputFnc(self):
        # if the query is yet to be sent, send it
        if self.state.query_state == QueryState.NOT_SENT:
            return {
                self.Q_send: Query(self.state.next_car[1].ID),
            }
        # if the query is sent and acknowledged, the car leaves
        elif self.state.query_state == QueryState.ACKNOWLEDGED:
            return {
                self.car_out: self.state.next_car[1],
            }
        # base case
        else:
            return {}

    def intTransition(self):
        self.state.time += self.timeAdvance()

        # decrease the delay of every car by self.elapsed
        self.state.decreaseCarDelays(self.timeAdvance())

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
                self.state.next_car[1].no_gas = False
                self.state.next_car = None

        return self.state

    def extTransition(self, inputs):
        self.state.time += self.elapsed

        # decrease the delay of every car by self.elapsed
        self.state.decreaseCarDelays(self.elapsed)

        # A car arrives at the GasStation
        if self.car_in in inputs:
            # As soon as one is entered, it is given a delay time,
            # sampled from a normal distribution with mean 10 minutes and standard deviation of 130 seconds
            # A car is required to stay at least 2 minutes in the GasStation.
            delay_time = max(self.state.minimum_car_stay, random.normalvariate(self.state.delay_dist_mean, self.state.delay_dist_std))
            self.state.carArrived(inputs[self.car_in], delay_time)

        elif self.Q_rack in inputs:
            # When a QueryAck is received, the GasStation waits for QueryAck's t_until_dep time
            # before outputting the next Car over the car_out output.
            self.state.next_time = inputs[self.Q_rack].t_until_dep
            # if the delay is infinite, the GasStation must poll the QueryAck at a certain interval
            if self.state.next_time == INFINITY:
                # set the next time to the observ_delay
                self.state.next_time = self.state.observ_delay
                # set the query state to not sent, so that the query is sent again
                self.state.query_state = QueryState.NOT_SENT
            else:
                # the query has been acknowledged
                self.state.query_state = QueryState.ACKNOWLEDGED

        return self.state
