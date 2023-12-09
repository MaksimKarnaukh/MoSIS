from srcgen import a, b, c, d, e, f
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
        "input_trace": [
            (1000000000, "i", None),
            (2000000000, "i", None),
        ],
        "output_trace": [
            (1000000000, "x", None),
            (2000000000, "x", None),
        ],
    },
]
SCENARIOS_C = [
    {
        "name": "C",
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
SCENARIOS_D = [
    {
        "name": "D",
        "input_trace": [],
        "output_trace": [
            (4000000000, "x", None),
            (5000000000, "y", None),
        ],
    },
]
SCENARIOS_E = [
    {
        "name": "D",
        "input_trace": [],
        "output_trace": [
            (3000000000, "x", None),
            (4000000000, "y", None),
        ],
    },
]
SCENARIOS_F = [
    {
        "name": "D",
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

if __name__ == "__main__":
    run_scenarios(a.A, SCENARIOS_A, [], [])
    run_scenarios(b.B, SCENARIOS_B, [], [])
    run_scenarios(c.C, SCENARIOS_C, [], [])
    run_scenarios(d.D, SCENARIOS_D, [], [])
    run_scenarios(e.E, SCENARIOS_E, [], [])
    run_scenarios(f.F, SCENARIOS_F, [], [])
