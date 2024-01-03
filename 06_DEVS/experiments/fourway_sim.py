from typing import List

from pypdevs.simulator import Simulator
from other.fourway_crossroad import fourwayCrossroad, sequentialRoad
import matplotlib.pyplot as plt


def plot_tt_short(travel_time_per_car):
    """
    Plots the travel time per car for the short simulation.
    :param travel_time_per_car: (list)
        list of tuples (car, travel_time)
    """
    cars = [f"{c[0].ID}" for c in travel_time_per_car]
    travel_times = [c[1] for c in travel_time_per_car]

    # Plotting
    plt.bar(cars, travel_times, color='blue')
    plt.xlabel('Car IDs')
    plt.ylabel('Travel Time (seconds)')
    plt.title('Travel Times of Cars')
    plt.show()


def plot_tt_long(travel_time_per_car):
    """
    Plots the travel time per car for the long simulation.
    :param travel_time_per_car: (list)
        list of tuples (car, travel_time)
    """
    # plot the travel time per car with the car ID on the x-axis and the travel time on the y-axis
    plt.scatter([c[0].ID for c in travel_time_per_car], [c[1] for c in travel_time_per_car], c='red', marker='o')
    # use logarimtic scale on the y-axis
    plt.yscale('log')
    # make sure the x-axis contains the car IDs of all cars
    plt.xticks([c[0].ID for c in travel_time_per_car if c[0].ID % 10 == 0])
    # print the actual y value next to the point, rounded to 2 decimals
    # for i in travel_time_per_car:
    #     plt.text(i[0].ID, i[1], str(round(i[1], 2)))
    # make grid
    plt.grid(True)

    plt.xlabel('Car IDs')
    plt.ylabel('Travel Time (log of seconds)')
    plt.title('Travel Times of Cars')
    plt.show()


def handle_statistics(model: fourwayCrossroad, length):
    """
    Handles the plotting/printing of statistics of the simulation.
    :param model:
        the model to get the statistics from
    :param length: (str)
        the length ("short" or "long") of the simulation
    """

    statistics: List = [ collector.getStatistics() for collector in model.getCollectors()]



    total_time = sum([statistic["total_time"] for statistic in statistics])
    number_of_cars = sum(statistic["number_of_cars"] for statistic in statistics )
    average_travel_time = total_time / number_of_cars if number_of_cars > 0 else 0
    # concatenate the travel times per car of all collectors which are lists of tuples (car, travel_time)
    travel_time_per_car = [travel_time for collector in model.getCollectors() for travel_time in collector.getStatistics()["travel_time_per_car"]]

    simulated_time = max([statistic["time"] for statistic in statistics])

    print(f"Simulation statistics for {length} simulation:")

    # print the statistics
    print("\t -The simulated time is: " + str(simulated_time))
    # number of crashes
    print("\t -The number of collisions is: " + str(model.getNumberCrashes()))
    print("\t -The number of cars that passed the fourway crossroad is: " + str(number_of_cars))
    print("\t -The total time spent by cars in the fourway crossroad is: " + str(total_time))
    print("\t -The average time spent by a car in the fourway crossroad is: " + str(average_travel_time))
    print("\n")

    # plot the travel time per car
    # if length == "short":
    #     plot_tt_short(travel_time_per_car)
    # else:
    plot_tt_long(travel_time_per_car)


def fourway_crossroad_sim(termination_time, length, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit):
    """
    Simulates the roadstretch model.
    :param termination_time: (int)
        the time at which the simulation should stop
    :param length: (str)
        the length ("short" or "long") of the simulation
    :param L: (int)
        length of the road segments
    :param v_max: (int)
        maximum allowed velocity
    :param IAT_min: (int)
        minimum inter-arrival time
    :param IAT_max: (int)
        maximum inter-arrival time
    :param v_pref_mu: (int)
        mean of the preferred velocity
    :param v_pref_sigma: (int)
        standard deviation of the preferred velocity
    :param destinations: (list)
        list of destinations
    :param limit: (int)
        limit of cars
    """
    model = fourwayCrossroad("fourway_crossroad", L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit)
    sim: Simulator = Simulator(model)
    sim.setClassicDEVS()
    sim.setDrawModel(True, "fourway.dot", False)

    sim.setTerminationTime(termination_time)
    sim.setVerbose(f"./traces/fourway_crossroad_{termination_time}.txt")

    sim.simulate()

    handle_statistics(model, length)


def fourway_crossroad_sim_short():
    """
    Simulates the roadstretch model for a short period of time.
    Runs the simulation for 100 time units with a limit of 50 cars.
    """

    # constants for the road stretch
    L = 5  # length of the road segments
    v_max = 30  # maximum allowed velocity
    IAT_min = 5
    IAT_max = 7
    v_pref_mu = 20
    v_pref_sigma = 5
    destinations = ["N", "E", "S", "W"]
    limit = 50

    fourway_crossroad_sim(
        100,
        "short",
        L, v_max,
        IAT_min,
        IAT_max,
        v_pref_mu,
        v_pref_sigma,
        destinations,
        limit
    )


def roadstretch_sim_long():
    """
    Simulates the roadstretch model for a long period of time.
    Runs the simulation for 10000 time units with a limit of 50 cars.
    """

    # constants for the road stretch
    L = 5  # length of the road segments
    v_max = 30  # maximum allowed velocity
    IAT_min = 5
    IAT_max = 7
    v_pref_mu = 30
    v_pref_sigma = 10
    destinations = ["collector"]
    limit = 50

    fourway_crossroad_sim(
        10000,
        "long",
        L, v_max,
        IAT_min,
        IAT_max,
        v_pref_mu,
        v_pref_sigma,
        destinations,
        limit
    )


if __name__ == '__main__':
    fourway_crossroad_sim_short()
