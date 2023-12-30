from pypdevs.simulator import Simulator
from other.roadstretch import RoadStretch


def roadstretch_sim_short():
    model = RoadStretch("roadstretch")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(100)
    sim.setVerbose("./traces/roadstretch")
    sim.simulate()


if __name__ == '__main__':
    roadstretch_sim_short()