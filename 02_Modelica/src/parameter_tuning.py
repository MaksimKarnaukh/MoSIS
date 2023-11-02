import os
from scipy import io
from matplotlib import pyplot
import numpy as np
import csv


def singleSimulation(A=60, b=0, M=1500, v0=30, x0=0):
    """
    This function simulates the model, once, with the given parameters, by executing through a shell command.
    It reads the results by calling the readMat function and displays a graph of the Temperature versus Time by calling the plotData function
    This function takes parameter values of the newtonCoolingWithTypes model.
    """
    # Create the string command that will be executed to execute the Modelica model
    # The command is structured as './<executable name> -override <param1 name>=<param1 value>, <param2 name>=<param2 value>..'
    simulationCommand = '.\\car_model.bat -override A=' + str(A) + ',b=' + str(b) + ',M=' + str(M) + ',v0=' + str(
        v0) + ',x0=' + str(x0)
    # Assuming that your shell is focused on the example/ directory, you should change directory to the one actually containing the executable. This directory usually has the same name as the Modelica file name.
    # Create the corresponding string command and execute it.
    os.chdir('CarDrag/car_package.car_model')
    # Simulate the model without generating terminal output
    os.system(simulationCommand + ' > NUL')
    # Obtain the variable values by reading the MAT-file
    [names, data] = readMat('car_model_res.mat')
    # Create a plot over time in the simulation
    # openDataPlot(data[0], data[2], 'time (seconds)', 'displacement (m)')
    os.chdir('../../')
    return data[2]


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

    # Define the range of 'b' values to explore
    b_values = np.linspace(0.01, 3.0, 300)

    displacement_data = []
    best_b_displacement_data = []
    errors = []
    min_error = float('inf')
    best_b = 0

    # Load the reference data from the CSV file
    reference_data = []
    with open('../input/deceleration_data.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # This skips the first row of the CSV file.
        next(csv_reader)
        reference_data = [float(row[1]) for row in csv_reader]

    print("starting simulations for b values")
    # Loop through 'b' values and simulate the car model with adjusted parameters
    for b in b_values:
        displacement = singleSimulation(b=b)
        displacement_data.append(displacement)

        # Adapt the displacement data to match the reference data
        displacement_adapted = [displacement[i] for i in range(0, 610, 10)]

        # Calculate the sum of squared errors
        error = sum((ref - sim) ** 2 for ref, sim in zip(reference_data, displacement_adapted))
        errors.append(error)

        # Check if the 'b' value has the minimum error
        if error < min_error:
            min_error = error
            best_b = b
            best_b_displacement_data = displacement

    print("finished simulations for b values")
    # Indicate the value of b for which the error is lowest.
    print(f"The best 'b' value (lowest error) is: {best_b:.2f}")

    # plot the error as a function of b.
    pyplot.plot(b_values, errors)
    pyplot.xlabel('b')
    pyplot.ylabel('Sum of squared errors')
    pyplot.show()

    # plot of the resulting curve (from selection of the value of b) superimposed with the csv dot plot.
    pyplot.plot(reference_data, 'o', label='reference data', markersize=4)
    best_b_displacement_data = [best_b_displacement_data[i] for i in range(0, 610, 10)]
    pyplot.plot(best_b_displacement_data, label='best b', color='red')
    pyplot.xlabel('time (s)')
    pyplot.ylabel('displacement (m)')
    pyplot.legend()
    pyplot.show()

