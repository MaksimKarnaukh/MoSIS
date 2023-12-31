from pypdevs.simulator import Simulator
from other.roadstretch import RoadStretch
import matplotlib.pyplot as plt

def roadstretch_sim(termination_time, cars_limit):

    model = RoadStretch("roadstretch", limit=cars_limit)
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(termination_time)
    sim.setVerbose(f"./traces/roadstretch_{termination_time}.txt")
    sim.simulate()

    # print the results
    print("Simulation statistics:")
    print(model.collector.getStatistics())
    # number of crashes
    print("The number of crashes is: " + str(model.getNumberCrashes()))

    total_time = model.collector.state.total_time
    average_travel_time = model.collector.state.average_time
    number_of_cars = model.collector.state.number_of_cars
    travel_time_per_car = model.collector.state.travel_time_per_car

    # plot the travel time per car with the car ID on the x-axis and the travel time on the y-axis
    plt.plot([c[0].ID for c in travel_time_per_car], [c[1] for c in travel_time_per_car], 'ro')
    plt.axis([0, number_of_cars, 0, total_time])
    plt.xlabel('Car ID')
    plt.ylabel('Travel time')
    plt.show()


def roadstretch_sim_short():
    """
    Simulates the roadstretch model for a short period of time.
    Runs the simulation for 10000 time units with a limit of 5 cars.
    """
    roadstretch_sim(10000, 5)


def roadstretch_sim_long():
    """
    Simulates the roadstretch model for a long period of time.
    Runs the simulation for 10000 time units with a limit of 50 cars.
    """
    roadstretch_sim(10000, 50)


if __name__ == '__main__':

    roadstretch_sim_short()

    # roadstretch_sim_long()