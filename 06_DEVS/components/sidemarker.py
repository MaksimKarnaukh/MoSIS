"""
"""

from pypdevs.DEVS import AtomicDEVS, CoupledDEVS, Port
from pypdevs.infinity import INFINITY
import random

from components.messages import QueryAck

class SideMarker(AtomicDEVS):
    """
    Marks all inputted QueryAcks to have sideways set to true.
    It also immediately outputs the inputted events.
    This block should be placed in-between the (Q_sack, Q_rack) connection of two RoadSegments
        if both want to merge onto a third RoadSegment.
    """
    def __init__(self, name):
        """
        :param name: The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(SideMarker, self).__init__(name)

        self.state = {
            "events": []
        }
        # Port that receives QueryAcks.
        self.mi: Port = self.addInPort("mi")
        self.mo: Port = self.addOutPort("mo")

    def timeAdvance(self):
        return INFINITY

    def outputFnc(self):
        # It outputs the QueryAck at once.
        return {
            self.mo: self.state["event"]
        }

    def extTransition(self, inputs):
        # marks all inputted QueryAcks to have sideways set to true. It also immediately outputs the inputted events.
        if self.mi in inputs:
            self.state["event"] = inputs[self.mi]
            self.state["event"].sideways = True
        return self.state


"""
@dataclass
class Customer:
    entered_at: float


from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random


class Generator(AtomicDEVS):
    def __init__(self, name):
        super(Generator, self).__init__(name)

        self.state = {
            "next_time": 0.0,
            "next_person": None,
            "time": 0.0
        }

        self.out = self.addOutPort("out")

    def timeAdvance(self):
        return self.state["next_time"]

    def outputFnc(self):
        if self.state["next_person"] is None:
            return {}
        return {
            self.out: self.state["next_person"]
        }

    def intTransition(self):
        self.state["time"] += self.timeAdvance()
        self.state["next_person"] = Customer(self.state["time"])
        self.state["next_time"] = random.uniform(5, 6)
        return self.state


class Store(AtomicDEVS):
    def __init__(self, name):
        super(Store, self).__init__(name)

        self.state = {
            "customers": []
        }

        self.inp = self.addInPort("inp")
        self.out = self.addOutPort("out")

    def extTransition(self, inputs):
        for i in range(len(self.state["customers"])):
            self.state["customers"][i][0] -= self.elapsed
        if self.inp in inputs:
            customer = inputs[self.inp]
            self.state["customers"].append([random.gauss(10, 5), customer])
            self.state["customers"] = sorted(self.state["customers"], key=lambda x: x[0])
        return self.state

    def timeAdvance(self):
        if len(self.state["customers"]) > 0:
            return self.state["customers"][0][0]
        return INFINITY

    def outputFnc(self):
        return {
            self.out: self.state["customers"][0][1]
        }

    def intTransition(self):
        self.state["customers"].pop(0)
        return self.state


class Collector(AtomicDEVS):
    def __init__(self, name):
        super(Collector, self).__init__(name)

        self.state = {
            "total_time": 0.0,
            "n": 0,
            "time": 0.0
        }

        self.inp = self.addInPort("inp")

    def extTransition(self, inputs):
        self.state["time"] += self.elapsed
        if self.inp in inputs:
            customer = inputs[self.inp]
            self.state["n"] += 1
            self.state["total_time"] += self.state["time"] - customer.entered_at
        return self.state


class Supermarket(CoupledDEVS):
    def __init__(self, name):
        super(Supermarket, self).__init__(name)

        self.gen = self.addSubModel(Generator("gen"))
        self.store = self.addSubModel(Store("store"))
        self.col = self.addSubModel(Collector("col"))

        self.connectPorts(self.gen.out, self.store.inp)
        self.connectPorts(self.store.out, self.col.inp)


if __name__ == '__main__':
    from pypdevs.simulator import Simulator

    model = Supermarket("market")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(100)
    sim.setVerbose(None)
    sim.simulate()
"""