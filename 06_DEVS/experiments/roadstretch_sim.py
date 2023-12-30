from pypdevs.simulator import Simulator
from other.roadstretch import RoadStretch


def roadstretch_sim_short():
    model = RoadStretch("roadstretch")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(10000)
    sim.setVerbose("./traces/roadstretch.txt")
    sim.simulate()

    # print the results
    print("The results are:")
    print(model.collector.getStatistics())
    # number of crashes
    print("The number of crashes is: " + str(model.getNumberCrashes()))

    # print("The average travel time is: " + str(model.collector.state.average_travel_time))
    # print("The average velocity is: " + str(model.collector.state.average_velocity))
    # print("The average distance traveled is: " + str(model.collector.state.average_distance_traveled))
    # print("The average waiting time is: " + str(model.collector.state.average_waiting_time))
    # print("The average queue length is: " + str(model.collector.state.average_queue_length))
    # print("The average queue waiting time is: " + str(model.collector.state.average_queue_waiting_time))
    # print("The average queue velocity is: " + str(model.collector.state.average_queue_velocity))
    # print("The average queue distance traveled is: " + str(model.collector.state.average_queue_distance_traveled))


def roadstretch_sim_long():
    model = RoadStretch("roadstretch")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(100)
    sim.setVerbose(None)
    sim.simulate()


if __name__ == '__main__':

    roadstretch_sim_short()

    # roadstretch_sim_long()