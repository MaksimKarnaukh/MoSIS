from pypdevs.simulator import Simulator
from other.roadstretch import RoadStretch
import matplotlib.pyplot as plt


def plot_cars(travel_time_per_car):
    # plot the travel time per car with the car ID on the x-axis and the travel time on the y-axis
    plt.plot([c[0].ID for c in travel_time_per_car], [c[1] for c in travel_time_per_car], 'ro')
    # use logarimtic scale on the y-axis
    plt.yscale('log')
    # use a grid on x and y axis
    plt.grid(True)
    # make sure the x-axis contains the car IDs of all cars
    plt.xticks([c[0].ID for c in travel_time_per_car])
    # print the actual y value next to the point, rounded to 2 decimals
    for i in travel_time_per_car:
        plt.text(i[0].ID, i[1], str(round(i[1], 2)))

    plt.xlabel('Car ID')
    plt.ylabel('Travel time')
    plt.show()

def handle_statistics(model):
    """
    Handles the plotting/printing of statistics of the simulation.
    :param model:
        the model to get the statistics from
    """

    statistics = model.collector.getStatistics()

    total_time = statistics["total_time"]
    average_travel_time = statistics["average_time"]
    number_of_cars = statistics["number_of_cars"]
    travel_time_per_car = statistics["travel_time_per_car"]

    print("Simulation statistics:")

    # number of crashes
    print("The number of crashes is: " + str(model.getNumberCrashes()))
    print("The total time is: " + str(total_time))

    # plot the travel time per car
    plot_cars(travel_time_per_car)



def roadstretch_sim(termination_time, cars_limit):

    # constants for the road stretch
    L = 5  # length of the road segments
    v_max = 30  # maximum allowed velocity
    IAT_min = 5
    IAT_max = 7
    v_pref_mu = 30
    v_pref_sigma = 10
    destinations = ["collector"]
    limit = 50

    model = RoadStretch("roadstretch", L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit)
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(termination_time)
    sim.setVerbose(f"./traces/roadstretch_{termination_time}.txt")
    sim.simulate()

    handle_statistics(model)


def roadstretch_sim_short():
    """
    Simulates the roadstretch model for a short period of time.
    Runs the simulation for 10000 time units with a limit of 5 cars.
    """
    roadstretch_sim(100, 50)


def roadstretch_sim_long():
    """
    Simulates the roadstretch model for a long period of time.
    Runs the simulation for 10000 time units with a limit of 50 cars.
    """
    roadstretch_sim(10000, 50)


if __name__ == '__main__':

    roadstretch_sim_short()

    # roadstretch_sim_long()