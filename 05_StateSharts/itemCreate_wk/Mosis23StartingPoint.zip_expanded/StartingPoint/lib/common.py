# Author: Joeri Exelmans
 
class QueueEntry:
    __slots__ = ('timestamp', 'callback', 'canceled', 'debug') # For MAXIMUM performance :)

    def __init__(self, timestamp, callback, debug):
        self.timestamp = timestamp
        self.callback = callback
        self.debug = debug
        self.canceled = False

# Simulation primitive.
# Uses virtualized (simulated) time, instead of looking at the wall clock.
class Controller:
    def __init__(self):
        self.event_queue = []
        self.simulated_time = 0

    def start(self, timestamp):
        self.simulated_time = timestamp
        self.start_time = timestamp

    def add_input(self, timestamp, sc, event, value=None):
        raise_method = getattr(sc, 'raise_' + event)
        if value is not None:
            callback = lambda: raise_method(value)
        else:
            callback = raise_method
        # print("input event: ", event)
        self.add_input_lowlevel(timestamp, callback, event)

    def add_input_lowlevel(self, timestamp, callback, debug):
        e = QueueEntry(timestamp, callback, debug)
        self.event_queue.append(e)
        self.event_queue.sort(key = lambda entry: entry.timestamp, reverse=True)
        return e

    def run_until(self, until):
        while self.have_event() and self.get_earliest() <= until:
            e = self.event_queue.pop();
            if not e.canceled:
                # print("handling", e.debug)
                self.simulated_time = e.timestamp
                e.callback()

    def have_event(self):
        return len(self.event_queue) > 0

    def get_earliest(self):
        return self.event_queue[-1].timestamp

# Our own timer service, used by the statechart.
# Much better than YAKINDU's pathetic timer service.
class TimerService:
    def __init__(self, controller):
        self.controller = controller;
        self.timers = {}

    # Duration: milliseconds
    def set_timer(self, sc, event_id, duration, periodic):
        def callback():
            sc.time_elapsed(event_id)

        self.unset_timer(callback, event_id)

        controller_duration = duration * 1000000 # ms to ns

        # print("set timer"+str(event_id), "duration", duration)
        e = self.controller.add_input_lowlevel(
            self.controller.simulated_time + controller_duration, # timestamp relative to simulated time
            callback,
            "timer"+str(event_id))

        self.timers[event_id] = e

    def unset_timer(self, callback, event_id):
        try:
            e = self.timers[event_id]
            e.canceled = True
        except KeyError:
            pass


def print_trace(trace, indent=0):
    print("[")
    for (timestamp, event_name, value) in trace:
        print((" "*indent)+"    (%i, \"%s\", %s)," % (timestamp, event_name, value))
    print((" "*indent)+"]", end='')
