import random

import numpy as np
from pyCBD.realtime.plotting import PlotManager, LinePlot, follow
import matplotlib.pyplot as plt
from python_models.Models import *
from pyCBD.simulator import Simulator


def sim_model(model, time=10.0, time_step=0.1):
    sim = Simulator(model)

    sim.setDeltaT(time_step)
    # The termination time can be set as argument to the run call
    sim.run(time)


def make_plot(model, output_var_name: str, title=None, plot_linetype: str = '--', plot_linecolor: str = 'black',
              label: str = 'Signal', lw = 0.5):
    if title is None:
        title = f"{model.getBlockName()}.{output_var_name} over time"
    x_axis_label = "Time (s)"
    y_axis_label = f"{model.getBlockName()}.{output_var_name}"

    data = model.getSignalHistory(output_var_name)
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    plt.title(title)
    x, y = [x for x, _ in data], [y for _, y in data]
    plt.plot(x, y, plot_linetype, c=plot_linecolor, lw=lw, label=label)
    plt.legend()
    return plt

def sim_and_plot_model(model, plot_var_name, time=10.0, time_step=0.10):
    sim_model(model, time, time_step)
    plt = make_plot(model, plot_var_name)
    plt.show()
    # save plot
    plt.savefig(f"../output/{plot_var_name}.png")
def sim_and_plot_var_stepsize(model_class, plot_var_name, time, time_steps):
    # random unique colors for each stepsize as string
    scolors = [f"#{''.join([random.choice('0123456789ABCDEF') for j in range(6)])}" for i in range(len(time_steps))]

    for idx,step in enumerate(time_steps):
        model = model_class(f"{model_class.__name__}_{step}")
        sim_model(model, time, step)
        plt = make_plot(model, plot_var_name, title= f"{plot_var_name} variable stepsize", label=f"stepsize: {step}s", plot_linecolor=scolors[idx], lw=1, plot_linetype='-')
    plt.show()
#     save plot
    plt.savefig(f"../output/{plot_var_name}_variable_stepsize.png")


def ex_1():
    cbda = CBDA("cbda")
    sim_and_plot_model(cbda, "x_a")

    cbdb = CBDB("cbdb")
    sim_and_plot_model(cbdb, "x_b")

    sin = sin_block("sin")
    sim_and_plot_model(sin, "sin")

    stepsizes = (0.1, 0.01, 0.001)
    time = 50.0
    # error_a = ERROR_A("error_a")
    sim_and_plot_var_stepsize(ERROR_A, "e_a", time, stepsizes)
    sim_and_plot_var_stepsize(ERROR_B, "e_b", time, stepsizes)





def ex_2():
    gt = g_t("g(t)")
    sim_and_plot_model(gt, "gt")
    stepsizes = (0.1, 0.01, 0.001)
    time = 100.0
    results = {"analytical": [2.634922497], "FE":[], "BE":[], "TR":[]}
    gt_compared = g_tComp("gt_compared")
    for idx,step in enumerate(stepsizes):
        model = g_tComp(f"{gt_compared.getBlockName()}_{step}")
        sim_model(model, time, step)
        # get the values for gt_FE, gt_BE, gt_TR at the end of the simulation
        results["FE"].append(model.getSignalHistory("gt_FE")[-1][1])
        results["BE"].append(model.getSignalHistory("gt_BE")[-1][1])
        results["TR"].append(model.getSignalHistory("gt_TR")[-1][1])
    print( results)

    print(f"analitical: {results['analytical'][0]}\n")
    for idx in range(len(stepsizes)):
        print(f"stepsize: {stepsizes[idx]}:\n\tFE: {results['FE'][idx]}\n\tBE: {results['BE'][idx]}\n\tTR: {results['TR'][idx]}\n")
if __name__ == '__main__':
    ex_1()
    ex_2()