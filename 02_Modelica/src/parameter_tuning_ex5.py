import os
import time

import numpy as np
from matplotlib import pyplot
from scipy import io


def readMat(matFileName):
    """
    function to read MAT-file data. matFileName is the name of the MAT-file generated on execution of a Modelica executable
    The output is [names, data] where names is an array of strings which are names of variables, data is an array of values of the associated variable in the same order
    :param matFileName:
    :return:
    """
    dataMat = io.loadmat(matFileName)
    names = [''] * len(dataMat['name'][0])
    data = [None] * len(names)
    # Check if the matrix of metadatas are transposed.
    if dataMat['Aclass'][3] == 'binTrans':
        # If the matrix of matadata needs to be transposed, the names need to be read from each string
        for x in range(len(dataMat['name'])):
            for i in range(len(dataMat['name'][x])):
                if dataMat['name'][x][i] != '\x00':
                    names[i] = names[i] + dataMat['name'][x][i]
        # If the matrix of metadata needs to be transposed, the index of variable trace needs to be read in a transposed fashion
        for i in range(len(names)):
            # If it is a variable, read the whole array
            if (dataMat['dataInfo'][0][i] == 0) or (dataMat['dataInfo'][0][i] == 2):
                data[i] = dataMat['data_2'][dataMat['dataInfo'][1][i] - 1]
            # If it is a parameter, read only the first value
            elif dataMat['dataInfo'][0][i] == 1:
                data[i] = dataMat['data_1'][dataMat['dataInfo'][1][i] - 1][0]
    else:
        # If the matrix of metadata need not be transposed, the names can be read directly as individual strings
        names = dataMat['name']
        # If the matrix of metadata need not be transposed, the index of variable trace needs to be read directly
        for i in range(len(names)):
            # If it is a variable, read the whole array
            if (dataMat['dataInfo'][i][0] == 0) or (dataMat['dataInfo'][i][0] == 2):
                data[i] = dataMat['data_2'][dataMat['dataInfo'][i][1] - 1]
            # If it is a parameter, read only the first value
            elif dataMat['dataInfo'][i][0] == 1:
                data[i] = dataMat['data_1'][dataMat['dataInfo'][i][1] - 1][0]
    # Return the names of variables, and their corresponding values
    return [names, data]


[names, data] = readMat('.\\Controller\\pid_package.control_loop\\control_loop_res.mat')
index_of_lead_displacement = names.index('lead_car.x_lt')
index_mech_car_displacement = names.index('add1.u1')
index_diff_mech_and_lead_car = names.index('add1.y')
index_e_t = names.index('add.y')


def singleSimulation(set_point=10, k_p=390.0, k_i=20.0, k_d=20.0):
    """
    This function simulates the model, once, with the given parameters, by executing through a shell command.
    It reads the results by calling the readMat function and displays a graph of the Temperature versus Time by calling the plotData function
    This function takes parameter values of the newtonCoolingWithTypes model.
    """
    simulationCommand = f'.\\control_loop.bat -override set_point={set_point},pID_controller.k_p={k_p},pID_controller.k_i={k_i},pID_controller.k_d={k_d}'
    os.chdir('Controller/pid_package.control_loop')
    os.system(simulationCommand + ' > NUL')
    [names, data] = readMat('control_loop_res.mat')
    os.chdir('../../')
    return data[index_diff_mech_and_lead_car],data[index_mech_car_displacement], data[index_of_lead_displacement], data[0]


def compareDataPlot(xdata, ydata1, ydata2, xLabel, yLabel):
    """
    This function plots the data from the simulation.
    xdata is x-axis data
    ydata is corresponding y-axis data
    xLabel is the string label value to be displayed in the plot for the x axis
    yLabel is the string label value to be displayed in the plot for the y axis
    """
    figure, axis = pyplot.subplots()
    axis.plot(xdata, ydata1, label='reference data', markersize=4)
    axis.plot(xdata, ydata2, label='best b', color='red')
    pyplot.xlabel(xLabel)
    pyplot.ylabel(yLabel)
    pyplot.legend()
    pyplot.show()


def openDataPlot(xdata, ydata, xLabel, yLabel):
    """
    This function plots the data from the simulation.
    xdata is x-axis data
    ydata is corresponding y-axis data
    xLabel is the string label value to be displayed in the plot for the x axis
    yLabel is the string label value to be displayed in the plot for the y axis
    """
    figure, axis = pyplot.subplots()
    axis.plot(xdata, ydata)
    pyplot.xlabel(xLabel)
    pyplot.ylabel(yLabel)
    pyplot.show()



def handle_single_simulation(set_point):
    #                 simulate
    [difference_lead_mech,displacement_ego_car,displacement_lead_car, time_data] = singleSimulation(set_point)

    displacement_data = (difference_lead_mech,displacement_ego_car,displacement_lead_car, time_data)
    return displacement_data


def has_collided(simulated_data):
    # Check if the two cars have collided, this happened when the difference between the two cars is negative
    return any([i < 0 for i in simulated_data[0]])

def find_best_set_point():
    #Start from a set-point of 9.9 and keep going lower until you can find a simulation trace where the two cars collide with each other. Keep your control parameters the same as designed by you in part 4 of the assignment!
    simulation = handle_single_simulation(10)

    set_point = 9.9
    while not has_collided(simulation):
        simulation = handle_single_simulation(set_point)
        set_point -= 0.1
        print(f"Trying set point {set_point}")
    print(f"Found set point {set_point}")
#     plot the displacement of the ego car and the lead car in the same plot
    pyplot.plot(simulation[3], simulation[1], label='ego car displacement')
    pyplot.plot(simulation[3], simulation[2], label='lead car displacement')
    pyplot.xlabel('time')
    pyplot.ylabel('displacement')
    pyplot.legend()
    # y axis limits 0 and 10
    # pyplot.ylim(0, 100)
    pyplot.show()

    # plot the difference between the displacement of the ego car and the lead car
    openDataPlot(simulation[3], simulation[0], 'time', 'lead car displacement - ego car displacement')


# "function" that calls the single simulation function from shell. In your code, this function call should be in a loop over the combinations of parameters.
if __name__ == "__main__":
    find_best_set_point()