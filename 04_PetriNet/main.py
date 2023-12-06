import RC as rc
import os


def generate_graph(input_file, output_file, type, extra_args=""):
    os.system(f"python RC.py {input_file} {output_file} {type} -m {extra_args}")
    os.system(f"dot -Tpng -o ./output/{type}_graph.png {output_file}")


input_file = "./Petrinets/Petrinet1.tapn"

if __name__ == '__main__':

    # ./RC.py input [output] type, where the output
    # file is optional and the 'type' is expected to be a prefix of either 'reachability' or
    # 'coverability' (case-insensitve)

    generate_graph(input_file, "./output/reach.dot", "reachability", "-p -I 100")

    generate_graph(input_file, "./output/cov.dot", "coverability", "-p")
