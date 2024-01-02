from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random
from typing import List, Tuple

from components.messages import QueryAck, Car

class CollectorState(object):
    def __init__(self):
        self.total_time: float = 0.0
        self.n: int = 0
        self.time: float = 0.0
        self.cars: List[Tuple[Car, float]] = [] # list of tuples (car, travel_time)

    def __repr__(self):
        return ""


class Collector(AtomicDEVS):

    def __init__(self, name):
        """
        Initializes the SideMarker
        :param name: The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(Collector, self).__init__(name)

        self.state = CollectorState()

        # Port that receives the Cars to collect.
        # It can be useful to already compute some statistics upon the arrival of new Cars.
        self.car_in = self.addInPort("car_in")

    def extTransition(self, inputs):
        self.state.time += self.elapsed
        if self.car_in in inputs:
            car: Car = inputs[self.car_in]
            self.state.n += 1
            car_travel_time = self.state.time - car.departure_time
            self.state.total_time += car_travel_time
            self.state.cars.append((car, car_travel_time))
        return self.state

    # Don't define anything else, as we only store events.
    # Collector has no behaviour

    def getStatistics(self):
        return {
            "time": self.state.time,
            "total_time": self.state.total_time,
            # if n is 0, return 0 to avoid division by 0
            "average_time": self.state.total_time / self.state.n if self.state.n > 0 else 0,
            "number_of_cars": self.state.n,
            "travel_time_per_car": self.state.cars
        }
