import os
from scipy import io
from matplotlib import pyplot
import numpy as np
import csv


def singleSimulation(k_p=1.0, k_i=1.0, k_d = 20.0):
    """
    This function simulates the model, once, with the given parameters, by executing through a shell command.
    It reads the results by calling the readMat function and displays a graph of the Temperature versus Time by calling the plotData function
    This function takes parameter values of the newtonCoolingWithTypes model.
    """
    # Create the string command that will be executed to execute the Modelica model
    # The command is structured as './<executable name> -override <param1 name>=<param1 value>, <param2 name>=<param2 value>..'
    simulationCommand = f'.\\control_loop.bat -override pID_controller.k_p={k_p},pID_controller.k_i={k_i},pID_controller.k_d={k_d}'
    # print(simulationCommand)
    # Assuming that your shell is focused on the example/ directory, you should change directory to the one actually containing the executable. This directory usually has the same name as the Modelica file name.
    # Create the corresponding string command and execute it.
    os.chdir('Controller/pid_package.control_loop')

    # Simulate the model without generating terminal output
    os.system(simulationCommand + ' > NUL')
    # Obtain the variable values by reading the MAT-file
    [names, data] = readMat('control_loop_res.mat')
    # Create a plot over time in the simulation
    openDataPlot(data[0], data[178], 'time (seconds)', 'displacement (m)')

    # compareDataPlot(data[0], data[59],data[178], 'time (seconds)', 'displacement (m)')
    os.chdir('../../')
    # 59 vs 178

    return data[178]

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


# "function" that calls the single simulation function from shell. In your code, this function call should be in a loop over the combinations of parameters.
if __name__ == "__main__":

    # time = 0 to 70 seconds, with a step size of 0.5 seconds
    time = np.linspace(0.1, 70.0, 141)


    displacement_data = []
    best_b_displacement_data = []
    errors = []
    min_error = float('inf')
    best_b = 0
    [names, data] = readMat('.\\Controller\\pid_package.control_loop\\control_loop_res.mat')
    index_of_lead_displacement = names.index('lead_car.x_lt')
    reference_data = data[index_of_lead_displacement]


    # Vary k_p only to study its effect on the behavior of the ego car.
    # Define the range of 'k_p' values to explore
    k_p_values = np.linspace(0.1, 40.0, 141)

    print("starting simulations for b values")
    # Loop through 'b' values and simulate the car model with adjusted parameters
    for k_p in k_p_values:
        displacement = singleSimulation(k_p=k_p)
        displacement_data.append(displacement)
        # # Calculate the sum of squared errors
        error = sum((ref - sim) ** 2 for ref, sim in zip(reference_data, displacement))
        errors.append(error)

        # Check if the 'k_p' value has the minimum error
        if error < min_error:
            min_error = error
            best_b = k_p
            best_b_displacement_data = displacement

    print("finished simulations for b values")
    # Indicate the value of b for which the error is lowest.
    print(f"The best 'k_p' value (lowest error) is: {best_b:.2f}")
    #
    # plot the error as a function of b.
    pyplot.plot(k_p_values, errors)
    pyplot.xlabel('k_p')
    pyplot.ylabel('Sum of squared errors')
    pyplot.show()

    # # plot of the resulting curve (from selection of the value of b) superimposed with the csv dot plot.
    # pyplot.plot(reference_data, 'o', label='reference data', markersize=4)
    # best_b_displacement_data = [best_b_displacement_data[i] for i in range(0, 610, 10)]
    # pyplot.plot(best_b_displacement_data, label='best b', color='red')
    # pyplot.xlabel('time (s)')
    # pyplot.ylabel('displacement (m)')
    # pyplot.legend()
    # pyplot.show()

