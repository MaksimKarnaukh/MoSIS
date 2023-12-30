scenario = {
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

        # we enter police interrupt mode (black and yellow switch every 500ms),
        # this is the reason why we exit green earlier than its 2 second timer
        (3174013700, "set_green", False),
        (3174013700, "set_yellow", True),
        (3674013700, "set_yellow", False),
        (4174013700, "set_yellow", True),
        (4674013700, "set_yellow", False),
        (5174013700, "set_yellow", True),
        (5674013700, "set_yellow", False),
        (6174013700, "set_yellow", True),

        # a short press on the button
        # switches traffic light mode to 'reactive' during police interrupt mode
        (6252499500, "set_led", True),

        # we are still in police interrupt mode
        # black and yellow switch every 500ms
        (6674013700, "set_yellow", False),
        (7174013700, "set_yellow", True),
        (7674013700, "set_yellow", False),
        (8174013700, "set_yellow", True),
        (8674013700, "set_yellow", False),
        (9174013700, "set_yellow", True),
        (9674013700, "set_yellow", False),
        (10174013700, "set_yellow", True),
        (10674013700, "set_yellow", False),

        # We exit police interrupt mode (default light is red)
        (10674013700, "set_red", True),
        (12674013700, "set_red", False),

        # light stays green for longer than 2s (because of car detection events):
        # however, after 5s, even though cars are still driving by, the light still goes to yellow:
        (12674013700, "set_green", True),
        (17674013700, "set_green", False),
        (17674013700, "set_yellow", True),
    ],
},
