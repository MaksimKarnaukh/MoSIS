"""
"""

from dataclasses import dataclass


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
