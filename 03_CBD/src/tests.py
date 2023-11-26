import sys
import os
import re

def contains_reoccuring_lines(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

        return len(lines) != len(set(lines))
def find_reoccuring_lines(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
        linecount = len(lines)
        linesetcount = len(set(lines))
        print("Linecount: " + str(linecount))
        print("Linesetcount: " + str(linesetcount))
        return list(set([x for x in lines if lines.count(x) > 1]))


def find_non_const_variables(c_code):
    assignment_pattern = re.compile(r'\b([a-zA-Z_]\w*)\s*=\s*([^;]+);')
    variable_dict = {}
    assignments = re.findall(assignment_pattern, c_code)
    for left_var, right_expr in assignments:
        right_vars = re.findall(r'\b([a-zA-Z_]\w*)', right_expr)
        variable_dict[left_var] = variable_dict.get(left_var, set())
        for right_var in right_vars:
            variable_dict[left_var].add(right_var)
    # Check for variables on the right side without a corresponding assignment on the left side
    non_const_variables = []
    for l, r in variable_dict.items():
        for var in r:
            if var not in variable_dict:
                non_const_variables.append(var)

    return non_const_variables


def tests():
    # print current working directory
    print(os.getcwd())
    filepath = "..\\output\\PID\\sources\\"
    files = ["eq0.c", "eqs.c", "defs.h"]
    for file in files:
        if contains_reoccuring_lines(filepath + file):
            print("File " + file + " contains reoccuring lines")
            print(find_reoccuring_lines(filepath + file))
        else:
            print("File " + file + " does not contain reoccuring lines")
        if file == "eqs.c" or file == "eq0.c":
            with open(filepath + file, 'r') as f:
                c_code = f.read()
                non_const_variables = find_non_const_variables(c_code)
                if len(non_const_variables) > 0:
                    print("The following variables do not appear on left side, but are used on right side of equations:")
                    print(non_const_variables)
                else:
                    print("All variables are fine.")


if __name__ == '__main__':
    tests()