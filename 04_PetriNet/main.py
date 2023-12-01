import RC as rc
import os
import graphviz as gv


def generate_graph(input_file, output_file, type):
    os.system(f"python RC.py {input_file} {output_file} {type} -m -p")
    os.system(f"dot -Tpng -o ./output/{type}_graph.png {output_file}")

input_file = "./Petrinets/Petrinet1.tapn"

if __name__ == '__main__':

    # ./RC.py input [output] type, where the output
    # file is optional and the 'type' is expected to be a prefix of either 'reachability' or
    # 'coverability' (case-insensitve)

    generate_graph(input_file, "./output/cov.dot", "coverability")

    # doesn't work cause infinite
    # generate_graph(input, "./output/cov.dot", "coverability")

    # don't uncomment this
    # os.system(f"python RC.py {input_file} ./output/net.dot coverability -g")
    # os.system(f"dot -Tpng -o ./output/graph.png net.dot")

    # os.system(f"python RC.py {input_file} ./output/net.dot coverability -p")




