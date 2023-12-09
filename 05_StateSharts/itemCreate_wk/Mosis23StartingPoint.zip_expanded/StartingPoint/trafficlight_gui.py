# Author: Joeri Exelmans

import tkinter
from srcgen import statechart
from lib.common import Controller, TimerService, print_trace

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yakindu.rx import Observer

import time

TIME_SCALE = 1

def scaled_now():
    return time.perf_counter_ns() * TIME_SCALE

OFF_COLOR = '#333333'

# Runs the Controller as close as possible to the wall-clock.
# Depending on how fast your computer is, simulated time will always run a tiny bit behind wall-clock time, but this error will NOT grow over time.
class RealTimeSimulation:
    def __init__(self, controller, tk, update_callback, scale=1.0):
        self.controller = controller
        self.tk = tk
        self.update_callback = update_callback
        self.scale = scale

        self.scheduled_id = None
        self.purposefully_behind = 0

    def add_input(self, sc, event, value=None):
        now = scaled_now() + self.purposefully_behind
        self.controller.add_input(now, sc, event, value)
        self.interrupt()
        return now - self.controller.start_time

    def interrupt(self):
        if self.scheduled_id is not None:
            self.tk.after_cancel(self.scheduled_id)

        if self.controller.have_event():
            now = scaled_now()
            earliest = self.controller.get_earliest()
            sleep_time = (earliest - now) // TIME_SCALE

            if sleep_time < 0:
                self.purposefully_behind = sleep_time
            else:
                self.purposefully_behind = 0

            def callback():
                # print("run_until...")
                self.controller.run_until(now + self.purposefully_behind)
                self.update_callback()
                self.interrupt()

            # print("sleeping for", int(sleep_time / 1000000), "ms")

            self.scheduled_id = self.tk.after(int(sleep_time / 1000000), callback)
        else:
            print("sleeping until woken up")


if __name__ == "__main__":
    # In these arrays, we will keep tuples (timestamp, event_name) of all input and output events, only to print them out at the end.
    input_trace = []
    output_trace = []

    toplevel = tkinter.Tk()
    toplevel.resizable(0,0)
    string_simtime = tkinter.StringVar(toplevel, '0.000')

    # For some reason, we have to initialize all 3 statecharts in code (instead of just the 'system' statechart)
    sc = statechart.Statechart()
    controller = Controller()
    sc.timer_service = TimerService(controller)

    # Callback function to display the simulated time:
    def update_callback():
        string_simtime.set('{:.3f}'.format((controller.simulated_time - controller.start_time) / 1000000000))

    sim = RealTimeSimulation(controller, toplevel, update_callback, scale=10.0)

    # Callback function for generating input events
    def generateInput(event_name):
        print("input event:", event_name)
        timestamp = sim.add_input(sc, event_name)
        tup = (timestamp, event_name, None) # our input events don't have a parameter
        input_trace.append(tup)

    # Create widgets....

    toplevel.title("Traffic Light")
    sim_frame = tkinter.Frame(toplevel)
    tkinter.Label(sim_frame, text="Simulated time is now:").pack(side=tkinter.LEFT)
    tkinter.Entry(sim_frame, state='readonly', width=8, textvariable=string_simtime, justify=tkinter.RIGHT).pack(side=tkinter.LEFT)
    tkinter.Label(sim_frame, text="s").pack(side=tkinter.LEFT)
    sim_frame.pack(side=tkinter.TOP)
    canvas = tkinter.Canvas(toplevel, bd=0, bg='#000000', width=100, height=300)
    red = canvas.create_oval(10,10,90,90, fill=OFF_COLOR)
    yellow = canvas.create_oval(10,110,90,190, fill=OFF_COLOR)
    green = canvas.create_oval(10,210,90,290, fill=OFF_COLOR)
    canvas.pack()
    # Buttons and LED display
    button_frame = tkinter.Frame(toplevel)
    button = tkinter.Button(button_frame, text="TOGGLE MODE")
    # Send event to our SC when button pressed or released:
    button.bind("<ButtonPress>", lambda _: generateInput("button_pressed"))
    button.bind("<ButtonRelease>", lambda _: generateInput("button_released"))
    button.pack(side=tkinter.LEFT)
    button_car = tkinter.Button(button_frame, text="PRETEND CAR DETECTED", command=lambda: generateInput("car_detected"))
    button_car.pack(side=tkinter.RIGHT)
    led_frame = tkinter.Frame(button_frame)
    string_led = tkinter.StringVar()
    led_entry = tkinter.Entry(led_frame, state='readonly', width=8, textvariable=string_led, justify=tkinter.RIGHT)
    led_entry.grid(row=0, column=1)
    led_frame.pack(side=tkinter.RIGHT)
    button_frame.pack()




    # Handle output events...

    # Bunch of callback functions
    def setRed(value):
        if value:
            canvas.itemconfigure(red, fill='#ff2222')
        else:
            canvas.itemconfigure(red, fill=OFF_COLOR)

    def setYellow(value):
        if value:
            canvas.itemconfigure(yellow, fill='#ffff22')
        else:
            canvas.itemconfigure(yellow, fill=OFF_COLOR)

    def setGreen(value):
        if value:
            canvas.itemconfigure(green, fill='#22ff22')
        else:
            canvas.itemconfigure(green, fill=OFF_COLOR)

    def setLed(value):
        if value:
            string_led.set("LED ON")
            led_entry.config(fg='red')
        else:
            string_led.set("LED OFF")
            led_entry.config(fg='grey')

    setLed(False)

    # Little helper class that turns a callback function into an YAKINDU-'Observer'.
    class CallbackObserver(Observer):
        def __init__(self, callback, event_name):
            self.callback = callback
            self.event_name = event_name

        def next(self, value=None):
            print("output event: %s(%s)" % (self.event_name, value))
            tup = (controller.simulated_time - controller.start_time, self.event_name, value)
            output_trace.append(tup)
            if value is None:
                self.callback()
            else:
                self.callback(value)

    # Bind output events to callbacks
    sc.set_red_observable.subscribe(CallbackObserver(setRed, "set_red"))
    sc.set_yellow_observable.subscribe(CallbackObserver(setYellow, "set_yellow"))
    sc.set_green_observable.subscribe(CallbackObserver(setGreen, "set_green"))
    sc.set_led_observable.subscribe(CallbackObserver(setLed, "set_led"))

    # Enter default states, start main loop...

    controller.start(scaled_now())
    sc.enter()
    sim.interrupt() # schedule first wakeup
    toplevel.mainloop()

    # Exiting...

    print("Exiting...")
    print("Full trace (you can add this to the SCENARIOS in test.py)...")
    print("{")
    print("    \"name\": \"interactive\",")
    print("    \"input_trace\": ", end='')
    print_trace(input_trace, 4)
    print(",")
    print("    \"output_trace\": ", end='')
    print_trace(output_trace, 4)
    print(",")
    print("}")