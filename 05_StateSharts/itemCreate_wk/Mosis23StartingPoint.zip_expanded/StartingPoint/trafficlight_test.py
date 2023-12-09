# Author: Joeri Exelmans
from srcgen import statechart
from lib.test import run_scenarios

# For each test scenario, sends a sequence of timed input events to the statechart, and checks if the expected sequence of timed output events occurs.

# Each timed event is a tuple (timestamp, event_name, parameter_value)
# For events that don't have a parameter, the parameter value is always 'None'.
# Timestamps are in nanoseconds!

SCENARIOS = [
    {
        "name": "normal, 2 cycles",
        "input_trace": [
            # no input events - we just run 2 cycles in normal mode
        ],
        "output_trace": [
            (0, "set_red", True),
            (2000000000, "set_red", False),
            (2000000000, "set_green", True),
            (4000000000, "set_green", False),
            (4000000000, "set_yellow", True),
            (5000000000, "set_yellow", False),
            (5000000000, "set_red", True),
            (7000000000, "set_red", False),
            (7000000000, "set_green", True),
            (9000000000, "set_green", False),
            (9000000000, "set_yellow", True),
            (10000000000, "set_yellow", False),
            (10000000000, "set_red", True),
        ],
    },
    {
        "name": "reactive",
        "input_trace": [
            # a short press on the button - switches mode to 'reactive'
            (1833042679, "button_pressed", None),
            (1896566197, "button_released", None),
            # cars are driving by while light is green:
            (3240632732, "car_detected", None),
            (4144836187, "car_detected", None),
            (5032585363, "car_detected", None),
            (5976821597, "car_detected", None),
            (6888497796, "car_detected", None),
        ],
        "output_trace": [
            (0, "set_red", True),
            # LED flips on immediately after releasing the button:
            (1896566197, "set_led", True),
            (2000000000, "set_red", False),
            (2000000000, "set_green", True),
            # light stays green for longer than 2s:
            # however, after 5s, even though cars are still driving by, the light still goes to yellow:
            (7000000000, "set_green", False),
            (7000000000, "set_yellow", True),
            (8000000000, "set_yellow", False),
            (8000000000, "set_red", True),
            (10000000000, "set_red", False),
            (10000000000, "set_green", True),
            # light is green again, but this time, no cars are driving by.
            # therefore, light goes to yellow after 2s:
            (12000000000, "set_green", False),
            (12000000000, "set_yellow", True),
            (13000000000, "set_yellow", False),
            (13000000000, "set_red", True),
        ],
    },
    {
        "name": "police interrupt",
        "input_trace": [
            (0, "button_pressed", None),
            (2000000000, "button_released", None),
        ],
        "output_trace": [
            (0, "set_red", True),
            (2000000000, "set_red", False),
            (2000000000, "set_yellow", True),
            (2500000000, "set_yellow", False),
            (3000000000, "set_yellow", True),
            (3500000000, "set_yellow", False),
        ],
    }

    # You MUST add one extra scenario HERE!
]

# The following events are safe to repeat: (with same value)
# Do not change this:
IDEMPOTENT = [
    "set_red",
    "set_yellow",
    "set_green",
    "set_led",
]

# We pretend that initially, these events occur:
# Do not change this:
INITIAL = [
    ("set_red", False),
    ("set_yellow", False),
    ("set_green", False),
    ("set_led", False),
]


if __name__ == "__main__":
    run_scenarios(statechart.Statechart, SCENARIOS, INITIAL, IDEMPOTENT)