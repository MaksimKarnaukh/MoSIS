from srcgen import a, b, c, d, e
from lib.test import run_scenarios

SCENARIOS_A = [
    {
        "name": "A",
        "input_trace": [],
        "output_trace": [
            (1000000000, "x", None),
            (2000000000, "x", None),
            (3000000000, "x", None),
        ],
    },
]
SCENARIOS_B = [
    {
        "name": "B",
        "input_trace": [],
        "output_trace": [
            (2000000000, "inner", None),
            (3000000000, "outer", None),
            (5000000000, "inner", None),
            (6000000000, "outer", None),
            (8000000000, "inner", None),
            (9000000000, "outer", None),
        ],
    },
]
SCENARIOS_C = [
    {
        "name": "C",
        "input_trace": [],
        "output_trace": [],
    },
]
SCENARIOS_D = [
    {
        "name": "D",
        "input_trace": [],
        "output_trace": [],
    },
]
SCENARIOS_E = [
    {
        "name": "E",
        "input_trace": [],
        "output_trace": [
            (1000000000, "x", None),
            (1000000000, "y", None),
            (2000000000, "x", None),
            (2000000000, "y", None),
            (3000000000, "x", None),
            (3000000000, "y", None),
        ],
    },
]

if __name__ == "__main__":
    run_scenarios(a.A, SCENARIOS_A, [], [], verbose=True)
    run_scenarios(b.B, SCENARIOS_B, [], [], verbose=True)
    run_scenarios(c.C, SCENARIOS_C, [], [], verbose=True)
    run_scenarios(d.D, SCENARIOS_D, [], [], verbose=True)
    run_scenarios(e.E, SCENARIOS_E, [], [], verbose=True)
