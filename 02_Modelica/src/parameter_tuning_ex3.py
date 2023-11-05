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
index_e_t = names.index('add.y')


def singleSimulation(k_p=1.0, k_i=1.0, k_d=20.0):
    """
    This function simulates the model, once, with the given parameters, by executing through a shell command.
    It reads the results by calling the readMat function and displays a graph of the Temperature versus Time by calling the plotData function
    This function takes parameter values of the newtonCoolingWithTypes model.
    """
    simulationCommand = f'.\\control_loop.bat -override pID_controller.k_p={k_p},pID_controller.k_i={k_i},pID_controller.k_d={k_d}'
    os.chdir('Controller/pid_package.control_loop')
    os.system(simulationCommand + ' > NUL')
    [names, data] = readMat('control_loop_res.mat')
    os.chdir('../../')
    return data[index_mech_car_displacement], data[index_of_lead_displacement], data[0]


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


def calculate_RMSE(simulated, reference):
    """
    This function calculates the RMSE between the simulated and reference data
    """
    rmse = np.sqrt(np.mean((simulated - reference) ** 2))
    return rmse


def update_best_RMSE(displacement_data, best_displacement_data):
    if not best_displacement_data or displacement_data[3] < best_displacement_data[3]:
        return displacement_data
    return best_displacement_data


def handle_single_simulation(k):
    #                 simulate
    [k_p, k_i, k_d] = k
    [displacement_eco, displacement_lead, time_data] = singleSimulation(k_p=k_p, k_i=k_i, k_d=k_d)

    reference_data = [i - 10 for i in displacement_lead]
    # time the loop to see how long it takes round to 2 decimal places
    rmse = calculate_RMSE(displacement_eco, reference_data)
    displacement_data = (displacement_eco, reference_data, time_data, rmse, (k_p, k_i, k_d), displacement_lead)
    return displacement_data


def vary_combinations():
    best_displacement_data = None

    # values for k_p from 200 to 400 with multiples of 10
    k_p_values = np.linspace(210, 390, 20)
    # values for k_i from 1 to 20 with multiples of 1
    k_i_values = np.linspace(1, 20, 20)
    # values for k_d from 1 to 20 with multiples of 1
    k_d_values = np.linspace(1, 20, 20)
    # loop over kp_values
    start2 = time.time()

    for k_p in k_p_values:
        start = time.time()
        results = [handle_single_simulation((k_p, k_i, k_d)) for k_i in k_i_values for k_d in k_d_values]
        best_displacement_data = update_best_RMSE(min(results, key=lambda x: x[3]),best_displacement_data)
        print("total time taken this loop: ", round(time.time() - start, 2), "s")

    print("total time taken: ", round(time.time() - start2, 2), "s")


    print(f'Lowest RMSE: {best_displacement_data[3]}, best k: {best_displacement_data[4]}')

    # for the best simulated, plot the difference between ego car and reference car
    pyplot.plot(best_displacement_data[2], [best_displacement_data[1][i] - best_displacement_data[0][i] for i in
                                    range(len(best_displacement_data[0]))], label=f'best {best_displacement_data[4]}',
                color='red')
    pyplot.xlabel('time (s)')
    pyplot.ylabel('displacement (m)')
    pyplot.legend()
    pyplot.show()

    # plot the displacement of the ego car and the lead car
    pyplot.plot(best_displacement_data[2], best_displacement_data[0], label=f'ego car {best_displacement_data[4]}',
                color='red')
    pyplot.plot(best_displacement_data[2], best_displacement_data[5], label=f'lead car {best_displacement_data[4]}',
                color='blue')
    pyplot.xlabel('time (s)')
    pyplot.ylabel('displacement (m)')
    pyplot.legend()
    pyplot.show()

    # plot the displacement of the ego car and the lead car for part of the plot
    pyplot.plot(best_displacement_data[2], best_displacement_data[0], label=f'ego car {best_displacement_data[4]}',
                color='red')
    pyplot.plot(best_displacement_data[2], best_displacement_data[5],
                label=f'lead car {best_displacement_data[4]}',
                color='blue')
    pyplot.xlim(0, 10)
    pyplot.ylim(0, 175)
    pyplot.xlabel('time (s)')
    pyplot.ylabel('displacement (m)')
    pyplot.legend()
    pyplot.show()



# "function" that calls the single simulation function from shell. In your code, this function call should be in a loop over the combinations of parameters.
if __name__ == "__main__":
    vary_combinations()
