import sys
import os

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


if __name__ == '__main__':
    tests()