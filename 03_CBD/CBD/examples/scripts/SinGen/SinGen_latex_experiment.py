#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from SinGen import *
from pyCBD.converters.latexify import CBD2Latex

sinGen = SinGen("SinGen")
cbd2latex = CBD2Latex(sinGen, show_steps=True, render_latex=False)

cbd2latex.simplify()

# print the resulting equations
print("RESULT IS:")
print(cbd2latex.render())
