import itertools
import random
from enum import Enum
from typing import List

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY
import uuid
from components.messages import Query, QueryAck, Car

# set a seed for reproducibility
random.seed(42)


class QueryState(Enum):
    """
    The state of the Query.
    """
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
        """
        :param IAT_min (float):
            Lower bound for the IAT uniform distribution.
        :param IAT_max (float):
            Upper bound for the IAT uniform distribution.
        :param v_pref_mu (float):
            Mean of the normal distribution that is used to sample v_pref.
        :param v_pref_sigma (float):
            Standard deviation of the normal distribution that is used to sample v_pref.
        :param destinations (list):
            A non-empty list of potential (string) destinations for the Cars. A random destination will be selected.
        :param limit (int):
            Upper limit of the number of Cars to generate.
        """
        self.IAT_min: float = IAT_min
        self.IAT_max: float = IAT_max
        self.v_pref_mu: float = v_pref_mu
        self.v_pref_sigma: float = v_pref_sigma
        self.destinations: List[str] = destinations
        self.limit: int = limit

        self.next_car: Car = None

    def __repr__(self):
        return ""


class Generator(AtomicDEVS):
    """
    Periodically generates Cars.
    This component allows cars to enter the system.
    The inter-arrival time (IAT) for the Cars is given by a uniform distribution.
    Upon generation, each car is given a preferred velocity v_pref by sampling from a normal distribution.

    When a Car is generated, a Query is sent over the Q_send port.
    As soon as a QueryAck is received, the generated car is output over the car_out port.
    Next, the Generator waits for some time before generating another Car.
    Upon generation, the Car's no_gas is randomly set to be either true or false.
    """

    # The unique incremental identifier for the cars.
    id_iter = itertools.count()

    def __init__(self, name, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit, v_max=100.0):
        """
            :param name (str):
                The name for this model. Must be unique inside a Coupled DEVS.
            :param IAT_min (float):
                Lower bound for the IAT uniform distribution.
            :param IAT_max (float):
                Upper bound for the IAT uniform distribution.
            :param v_pref_mu (float):
                Mean of the normal distribution that is used to sample v_pref.
            :param v_pref_sigma (float):
                Standard deviation of the normal distribution that is used to sample v_pref.
            :param destinations (list):
                A non-empty list of potential (string) destinations for the Cars. A random destination will be selected.
            :param limit (int):
                Upper limit of the number of Cars to generate.
            :param v_max (float):
                The maximum velocity of the cars. Only needed because we don't want to generate a car with v greater
                than the max velocity of the road segment where the car will be outputted by the generator.
        """
        super(Generator, self).__init__(name)
        self.state = GeneratorState(IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit)
        self.v_max = v_max

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

    def createCar(self):
        """
        Function to create a new Car object with the necessary parameters.
        """
        # Upon generation, the Car's no_gas is randomly set to be either true or false.
        no_gas = random.choice([True, False])
        # Upon generation, each car is given a preferred velocity v_pref by sampling from a normal distribution.
        v_pref = max(0.0, random.normalvariate(self.state.v_pref_mu, self.state.v_pref_sigma))
        # A non-empty list of potential (string) destinations for the Cars. A random destination will be selected.
        destination = random.choice(self.state.destinations)
        distance_traveled = 0.0
        # The current simulation time becomes the Car's departure_time.
        departure_time = self.state.time
        car_id = next(self.id_iter)
        generated_car = Car(
            departure_time=departure_time, no_gas=no_gas,
            v_pref=v_pref, v=min(v_pref, self.v_max), destination=destination,
            distance_traveled=distance_traveled, ID=car_id,
            dv_neg_max=self.state.dv_neg_max, dv_pos_max=self.state.dv_pos_max
        )
        self.state.generated_car_count += 1
        return generated_car
