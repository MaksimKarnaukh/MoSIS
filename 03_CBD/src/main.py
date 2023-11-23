import os
import random

import matplotlib.pyplot as plt
from pyCBD import depGraph, scheduling
from pyCBD.simulator import Simulator

from python_models.Models import *
from python_models.PID_Controller import *

from compile_and_run import compile_and_run
from zip_pid import zip_pid


def sim_model(model, time=10.0, time_step=0.1):
    sim = Simulator(model)

    sim.setDeltaT(time_step)
    # The termination time can be set as argument to the run call
    sim.run(time)


def make_plot(model, output_var_name: str, title=None, plot_linetype: str = '-', plot_linecolor: str = 'red',
              label: str = 'Signal', lw=1.5):
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
    # plot grid
    plt.grid(True)
    return plt


def sim_and_plot_model(model, plot_var_name, time=10.0, time_step=0.10):
    sim_model(model, time, time_step)
    plt = make_plot(model, plot_var_name)
    # save plot
    plt.savefig(f"../output/{plot_var_name}.png")
    plt.show()


def sim_and_plot_var_stepsize(model_class, plot_var_name, time, time_steps, log_scale=False, y_lim=None):
    # random unique colors for each stepsize as string
    scolors = [f"#{''.join([random.choice('0123456789ABCDEF') for j in range(6)])}" for i in range(len(time_steps))]

    for idx, step in enumerate(time_steps):
        model = model_class(f"{model_class.__name__}_{step}")
        sim_model(model, time, step)

        plt = make_plot(model, plot_var_name, title=f"{plot_var_name} variable stepsize", label=f"stepsize: {step}s",
                        plot_linecolor=scolors[idx], lw=1, plot_linetype='-')
    if log_scale:
        # use log scale for y axis
        plt.yscale('log')
    if y_lim is not None:
        # set the y axis bottom limit
        plt.ylim(bottom=y_lim)
    #     save plot
    plt.savefig(f"../output/{plot_var_name}_variable_stepsize.png")
    # show plot
    plt.show()


def ex_1():
    cbda = CBDA("cbda")
    sim_and_plot_model(cbda, "x_a")

    cbdb = CBDB("cbdb")
    sim_and_plot_model(cbdb, "x_b")

    sin = sin_block("sin")
    sim_and_plot_model(sin, "sin")

    stepsizes = (0.1, 0.01, 0.001)
    time = 50.0
    sim_and_plot_var_stepsize(ERROR_A, "e_a", time, stepsizes, log_scale=True, y_lim=1e-3)
    sim_and_plot_var_stepsize(ERROR_B, "e_b", time, stepsizes, log_scale=True, y_lim=1e-3)


def ex_2():
    gt = g_t("g(t)")
    sim_and_plot_model(gt, "gt")
    stepsizes = (0.1, 0.01, 0.001)
    time = 100.0
    results = {"analytical": [2.634922497], "FE": [], "BE": [], "TR": []}
    gt_compared = g_tComp("gt_compared")
    for idx, step in enumerate(stepsizes):
        model = g_tComp(f"{gt_compared.getBlockName()}_{step}")
        sim_model(model, time, step)
        # get the values for gt_FE, gt_BE, gt_TR at the end of the simulation
        results["FE"].append(model.getSignalHistory("gt_FE")[-1][1])
        results["BE"].append(model.getSignalHistory("gt_BE")[-1][1])
        results["TR"].append(model.getSignalHistory("gt_TR")[-1][1])
    print(results)

    print(f"analitical: {results['analytical'][0]}\n")
    for idx in range(len(stepsizes)):
        print(
            f"stepsize: {stepsizes[idx]}:\n\tFE: {results['FE'][idx]}\n\tBE: {results['BE'][idx]}\n\tTR: {results['TR'][idx]}\n")


def model_to_depgraph_topo(model, curIteration, delta_t=0.5) -> tuple[depGraph, list]:
    initial = depGraph.createDepGraph(model=model, curIteration=curIteration)
    topo = scheduling.TopologicalScheduler().schedule(initial, curIt=curIteration, time=delta_t * curIteration)
    return initial, topo


def initial_depgraph_topo(model) -> tuple[depGraph, list]:
    return model_to_depgraph_topo(model, 0)


def non_initial_depgraph_topo(model, delta_t=0.5) -> tuple[depGraph, list]:
    return model_to_depgraph_topo(model, 1, delta_t=delta_t)


def getPortName(model, block: BaseBlock, var_name, sep="_"):
    portname = f"{var_name}"
    while block is not model:
        portname = block.getBlockName() + sep + portname
        block = block._parent

    return sep + portname


def getPortNames(model, block: BaseBlock, var_names, sep="_"):
    portnames = var_names
    while block is not model:
        # append block.getBlockName() + sep to the beginning of each portname
        portnames = [block.getBlockName() + sep + portname for portname in portnames]
        block = block._parent
    return [sep + portname for portname in portnames]


def operationToCString(portname_out, portnames_in, operation) -> str:
    portname_in1, *portnames_in = portnames_in

    return f"{portname_out} = {portname_in1}{''.join([' ' + operation + ' ' + portname_in for portname_in in portnames_in])};\n"


def blockToCString(model, block: BaseBlock) -> str:
    """
    Returns the C code for the block
    """
    portnames = getPortNames(model, block, block.getOutputPortNames() + block.getInputPortNames())

    # if block is a constant block
    if isinstance(block, ConstantBlock):
        return f"{portnames[0]} = {block.getValue()}\n;"

    # if block is a DeltaTBlock
    elif isinstance(block, DeltaTBlock):
        return f"{portnames[0]} = delta\n;"

    # if block is a DelayBlock
    elif isinstance(block, DelayBlock):
        return f""

    # if block is a ProductBlock
    elif isinstance(block, ProductBlock):
        portname_out, *portnames_in = portnames
        return operationToCString(portname_out, portnames_in, "*")

    # if block is an AdderBlock
    elif isinstance(block, AdderBlock):
        portname_out, *portnames_in = portnames
        return operationToCString(portname_out, portnames_in, "+")

    # if block is a NegatorBlock
    elif isinstance(block, NegatorBlock):
        portname_out, portname_in = portnames
        return f"{portname_out} = -{portname_in};\n"

    # if block is a InverterBlock
    elif isinstance(block, InverterBlock):
        portname_out, portname_in = portnames
        return f"{portname_out} = 1/{portname_in};\n"

    # else throw exception because we don't know how to handle this block
    else:
        raise Exception(f"Unknown block type: {type(block)}")


def construct_eq0(model, metadata):
    """
    Construct the eq0.c file for a model. This file contains the initial equations in C for the model.
    """
    initial, topo = initial_depgraph_topo(model)
    result: str = ""
    for block_in_list in topo:
        block: BaseBlock = block_in_list[0]
        if len(block_in_list) > 1:
            raise Exception(f"More than one block in list: {block_in_list}")
        # if block is a port block
        if isinstance(block, Port):
            continue
        result += blockToCString(model, block=block)

    with open("../output/PID/sources/eq0.c", "w") as f:
        f.write(result)
    return result


def getAllInputNames(model: CBD, sep="."):
    """
    Returns all input names of the model.
    Inspired by :func:'pyCBD.Core.CBD.getAllSignalNames'
    """
    res = []
    for block in model.getBlocks():
        if isinstance(block, CBD):
            res.extend(getAllInputNames(block, sep))
        for out in block.getInputPorts():
            path = block.getPath(sep, True)
            if len(path) == 0:
                path = out.name
            else:
                path += sep + out.name
            res.append(path)
    for out in model.getInputPorts():
        path = model.getPath(sep, True)
        if len(path) == 0:
            path = out.name
        else:
            path += sep + out.name
        res.append(path)
    return res


def construct_defs_h(model: CBD, metadata):
    """
    Construct the defs.h file for a model. This file contains the definitions of the variables in the model.
    """
    defs_h: str = ""

    defs_h += f"#define M {len(metadata)} /* Number of Internal Variables*/ \n"
    for idx, signal in enumerate(metadata):
        defs_h += f"#define {signal} (cbd->modelData[{metadata[signal]['ValueReference']}])\n"
    with open("../output/PID/sources/defs.h", "w") as f:
        f.write(defs_h)


def construct_eqs(model: CBD, delta_t=0.5):
    """
    Construct the eqs.c file for a model. This file contains the equations in C for the model.
    """
    initial, topo = non_initial_depgraph_topo(model, delta_t=delta_t)
    result: str = ""
    for block_in_list in topo:
        block: BaseBlock = block_in_list[0]
        if len(block_in_list) > 1:
            raise Exception(f"More than one block in list: {block_in_list}")
        # if block is a port block
        if isinstance(block, Port):
            continue
        result += blockToCString(model, block=block)

    with open("../output/PID/sources/eqs.c", "w") as f:
        f.write(result)
    return result


def scalar_variable(f, entry):
    # <ScalarVariable>: Has 5 attributes:
    #     name (the name of the variable, as exposed to the user),
    #     valueReference (the index in the modelData array that refers to this variable),
    #     initial (how the variable is initialized; "exact" implies that it is known, "calculated" otherwise),
    #     causality (kind of parameter; "input" implies model input, "output" is model output, "local" otherwise),
    #     variability (how the value will change; "constant" for ConstantBlocks, "continuous" otherwise).

    f += f"\t<!-- index: {entry['index']} -->\n"
    f += f"\t<ScalarVariable name=\"{entry['name']}\" valueReference=\"{entry['ValueReference']}\" causality=\"{entry['causality']}\" variability=\"{entry['variability']}\""
    if entry['initial'] is not None:
        f += f" initial=\"{entry['initial']}\""
    f += ">\n"
    """
        Additionally, there is a <Real> tag as a child, which has a start attribute 
        (indicating the starting value of the variable) if the <ScalarVariable>'s initial equals "exact".
    """
    if entry['initial'] == 'exact' or entry['causality'] == 'input':
        f += f"\t\t<Real start=\"{entry['Real']}\"/>\n"
    # else if entry is input
    else:
        f += f"\t\t<Real/>\n"
    f += f"\t</ScalarVariable>\n"
    return f


def scalar_variables(file_contents, meta_data):
    # resulting_string
    resulting_string = ""

    #     loop over key, entry in metadata
    for key, entry in meta_data.items():
        resulting_string = scalar_variable(resulting_string, entry)
    file_contents = file_contents.replace("<!-- TODO: ScalarVariable tags -->", resulting_string)
    return file_contents


def model_variables(file_contents, meta_data):
    # <ModelVariables>: Contains the M internal variables, denoted as unique <ScalarVariable>s.

    return scalar_variables(file_contents, meta_data)


def outputs(file_contents, meta_data):
    # It contains an <Outputs> tag, which has a set of <Unknown> children.
    # Each <Unknown> has an attribute index, referring to the corresponding index w.r.t. the ordering of the ScalarVariables.
    resulting_string = ""
    for key, entry in meta_data.items():
        if entry['causality'] == 'output':
            resulting_string += f"\t<Unknown index=\"{entry['index']}\"/>"
    file_contents = file_contents.replace("<!-- TODO: Unknown tags -->", resulting_string, 1)
    return file_contents


def initial_unknowns(file_contents, meta_data):
    # There is also an <InitialUnknowns> tag, which will be the exact same as the <Outputs> tag
    # (for the purposes of this exercise).
    # Each <Unknown> has an attribute index,
    resulting_string = ""

    for key, entry in meta_data.items():
        if entry['causality'] == 'output':
            resulting_string += f"\t<Unknown index=\"{entry['index']}\"/>"
    file_contents = file_contents.replace("<!-- TODO: Unknown tags -->", resulting_string, 1)
    return file_contents


def model_structure(file_contents, meta_data):
    """
     <ModelStructure>: Special cases of the variables.
    """

    file_contents = outputs(file_contents, meta_data)
    file_contents = initial_unknowns(file_contents, meta_data)
    return file_contents


def construct_modelDescription_xml(model: CBD, meta_data):
    """
     This file contains a lot of information about the general simulation setup. Please only change the described tags of this file. The other files are constructed such that they are linked correctly. Note that the description below and the provided FMU are a massive oversimplification of the total FMI 2.0 reference.

    <ModelVariables>: Contains the M internal variables, denoted as unique <ScalarVariable>s.
    <ScalarVariable>: Has 5 attributes:
        name (the name of the variable, as exposed to the user),
        valueReference (the index in the modelData array that refers to this variable),
        initial (how the variable is initialized; "exact" implies that it is known, "calculated" otherwise),
        causality (kind of parameter; "input" implies model input, "output" is model output, "local" otherwise),
        variability (how the value will change; "constant" for ConstantBlocks, "continuous" otherwise).
    Additionally, there is a <Real> tag as a child, which has a start attribute (indicating the starting value of the variable) if the <ScalarVariable>'s initial equals "exact".
    <ModelStructure>: Special cases of the variables. It contains an <Outputs> tag, which has a set of <Unknown> children. There is also an <InitialUnknowns> tag, which will be the exact same as the <Outputs> tag (for the purposes of this exercise). Each <Unknown> has an attribute index, referring to the corresponding index w.r.t. the ordering of the ScalarVariables. Only the model outputs are <Unknown>s (for the purposes of this exercise).
    """

    with open("../input/template/modelDescription.xml", "r") as f_in:
        file_contents = f_in.read()
    # sort meta_data by value reference
    meta_data = dict(sorted(meta_data.items(), key=lambda item: item[1]['ValueReference']))

    # copy the modelDescription.xml from the original template (in the input folder) to the output folder

    # inject the <ModelVariables> into the modelDescriptionExpansion.xml
    # go to the line that contains <ModelVariables>

    file_contents = model_variables(file_contents, meta_data)
    file_contents = model_structure(file_contents, meta_data)
    # see if the file exists
    #     write the file
    with open("../output/PID/modelDescription.xml", "w+") as f_out:
        f_out.write(file_contents)


def adapt_causality(model: CBD, metadata):
    """
    Add the variability to the metadata of the model.
    """
    port: Port
    for port in getPortNames(model, model, model.getInputPortNames()):
        metadata[port]['causality'] = 'input'
        metadata[port]['initial'] = None
        metadata[port]['Real'] = 0
    for port in getPortNames(model, model, model.getOutputPortNames()):
        metadata[port]['causality'] = 'output'


def adapt_value_reference(metadata):
    # make ValueReference the index of the variable in the modelData dict
    for idx, var in enumerate(metadata.keys()):
        metadata[var]['ValueReference'] = idx
        metadata[var]['index'] = idx + 1


def adapt_initial_real_variability(model, metadata):
    """
    Adapts the initial, Real and variability field of the metadata,
        initial (how the variable is initialized; "exact" implies that it is known, "calculated" otherwise),
        variability (how the value will change; "constant" for ConstantBlocks, "continuous" otherwise).
         Additionally, there is a <Real> tag as a child, which has a start attribute (indicating the starting value of the variable) if the <ScalarVariable>'s initial equals "exact".
    cables connected to constants or deltaT blocks are exact
    """

    initial, topo = initial_depgraph_topo(model)
    it2, topo2 = non_initial_depgraph_topo(model)

    for [block] in topo + topo2:

        if isinstance(block, Port):
            continue
        if isinstance(block, ConstantBlock):  # or isinstance(block,DeltaTBlock):
            block: ConstantBlock
            for portname in getPortNames(model, block, block.getOutputPortNames()):
                metadata[portname]['initial'] = 'exact'
                metadata[portname]['Real'] = block.getValue()
                metadata[portname]['variability'] = 'constant'

            # port:Port
            # for port in block.getOutputPorts():
            #     connections = port.getOutgoing()
            #     target:Port
            #     for connection in connections:
            #         target = connection.target
            #
            #         portname = getPortName(model, target.block ,target.name)
            #         metadata[portname]['initial'] = 'exact'
            #         metadata[portname]['Real'] = block.getValue()


def add_blocks(model, metadata):
    """
Add the block to the metadata of the model.
Useful for debugging and later use.
    """

    for block in model.getBlocks():
        if isinstance(block, Port):
            continue
        portnames = getPortNames(model, block, block.getOutputPortNames() + block.getInputPortNames())
        for portname in portnames:
            metadata[portname]['block'] = block


def create_metadata(model: CBD):
    """
    Create the metadata for the model.
    """
    metadata = {}
    all_ports = model.getAllSignalNames(sep='_') + getAllInputNames(model, sep='_')
    for port in [f"_{port}" for port in all_ports]:
        metadata[port] = {'name': port, 'ValueReference': None, 'variability': 'continuous', \
                          'causality': 'local', 'initial': 'calculated', 'Real': None}

    add_blocks(model, metadata)
    adapt_causality(model, metadata)
    adapt_value_reference(metadata)
    adapt_initial_real_variability(model, metadata)

    return metadata



def ex_3():
    pid: CBD = PID("pid")
    # get all signal names of the model with the separator "_" and _ as prefix
    metadata = create_metadata(pid)
    construct_defs_h(pid, metadata)
    construct_eq0(pid, metadata)
    construct_eqs(pid)
    construct_modelDescription_xml(pid, metadata)

    zip_pid()
    compile_and_run()


if __name__ == '__main__':
    # ex_1()
    # ex_2()
    ex_3()
