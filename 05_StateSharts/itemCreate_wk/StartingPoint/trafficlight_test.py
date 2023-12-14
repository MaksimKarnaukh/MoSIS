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
    },

    # You MUST add one extra scenario HERE!
    {
        "name": "special scenario",
        "input_trace": [
            # we enter police interrupt mode
            (1174013700, "button_pressed", None),
            (3174013700, "button_released", None),

            # a short press on the button - switches mode to 'reactive'
            (6052499500, "button_pressed", None),
            (6252499500, "button_released", None),

            # We exit police interrupt mode
            (8674013700, "button_pressed", None),
            (10674013700, "button_released", None),

            # cars are driving by while light is green:
            (13074013700, "car_detected", None),
            (14574013700, "car_detected", None),
            (15374013700, "car_detected", None),
            (16174013700, "car_detected", None),
            (17474013700, "car_detected", None),
        ],
        "output_trace": [
            (0, "set_red", True),
            (2000000000, "set_red", False),
            (2000000000, "set_green", True),

            # we enter police interrupt mode (black and yellow switch every 500ms), this is the reason why we exit green earlier than its 2 second timer
            (3174013700, "set_green", False),
            (3174013700, "set_yellow", True),
            (3674013700, "set_yellow", False),
            (4174013700, "set_yellow", True),
            (4674013700, "set_yellow", False),
            (5174013700, "set_yellow", True),
            (5674013700, "set_yellow", False),
            (6174013700, "set_yellow", True),

            # a short press on the button - switches traffic light mode to 'reactive' during police interrupt mode
            (6252499500, "set_led", True),

            # we are still in police interrupt mode (black and yellow switch every 500ms)
            (6674013700, "set_yellow", False),
            (7174013700, "set_yellow", True),
            (7674013700, "set_yellow", False),
            (8174013700, "set_yellow", True),
            (8674013700, "set_yellow", False),
            (9174013700, "set_yellow", True),
            (9674013700, "set_yellow", False),
            (10174013700, "set_yellow", True),
            (10674013700, "set_yellow", False),

            # We exit police interrupt mode
            (10674013700, "set_red", True),
            (12674013700, "set_red", False),

            # light stays green for longer than 2s (because of car detection events):
            # however, after 5s, even though cars are still driving by, the light still goes to yellow:
            (12674013700, "set_green", True),
            (17674013700, "set_green", False),
            (17674013700, "set_yellow", True),
        ],
    },
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