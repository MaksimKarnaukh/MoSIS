from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
from typing import List
from components.messages import Query, QueryAck, Car
from enum import Enum


class EventEnum(Enum):
    SEND_QUERY = 0
    RECEIVED_QUERY = 1
    RECEIVED_ACKNOWLEDGEMENT = 2
    CAR_OUT = 3

class RoadSegmentState(object):
    time: float = 0

    def __init__(self, cars_present: List[Car], t_until_dep: float, remaining_x: float):
        """
        :param cars_present (list):
            A list for all the Cars on this RoadSegment.
            Even though the existence of multiple Cars results in a collision,
            for extensibility purposes a list should be used.
        :param t_until_dep (float):
            The time until the current Car (i.e., the first one in cars_present) leaves the RoadSegment.
            If the Car's velocity is 0, this value is infinity. If no Car is present, this value is 0.
        :param remaining_x (float):
            The remaining distance that the current Car (i.e., the first one in cars_present)
            should still travel on this RoadSegment.
        """

        # While the state should contain many more fields, the following three should at least be there.
        self.cars_present: List[Car] = cars_present
        self.t_until_dep: float = t_until_dep
        self.remaining_x: float = remaining_x

        self.next_car: Car = None
        self.entered_car_count: int = 0
        self.collisions: int = 0

        self.query_ack_reply: QueryAck = None

        self.time_since_last_query: float = 0.0
        self.previous_v_new = 0.0

        self.car_out_event = None
        # [[ Event, time ], ... ]
        self.event_queue: List[List] = []

    def __repr__(self):
        return ""


class RoadSegment(AtomicDEVS):
    """
    Represents a small stretch of road that can only contain a single Car.
    When multiple Cars are on a RoadSegment, we assume the Cars crashed into each other.
    """
    observ_delay_default: float = 0.1
    priority_default: bool = False
    lane_default: int = 0

    def __init__(self, name, L: float, v_max: float, observ_delay: float = observ_delay_default, priority: bool = priority_default, lane: int = lane_default):
        """
        :param name (str):
            The name for this model. Must be unique inside a Coupled DEVS.
        :param L (float):
            The length of the RoadSegment.
            Given that the average Car is about 5 meters in length, a good estimate value for L would therefore be 5 meters.
        :param v_max (float):
            The maximal allowed velocity on this RoadSegment.
        :param observ_delay (float):
            The time it takes to reply to a Query that was inputted.
            This value mimics the reaction time of the driver.
            We can increase the observ_delay to accommodate for bad weather situations (e.g., a lot of fog and/or rain).
            Defaults to 0.1.
        :param priority (bool):
            Whether or not this RoadSegment should have priority on a merge with other road segments.
            Defaults to False.
        :param lane (int):
            Indicator of the lane this Roadsegment is currently part of.
            Defaults to 0.
        """
        super(RoadSegment, self).__init__(name)
        self.state = RoadSegmentState([], None, None)
        self.L: float = L
        self.v_max: float = v_max
        self.observ_delay: float = observ_delay
        self.priority: bool = priority
        self.lane: int = lane

        # All Cars are inputted on this port. As soon as a Car arrives, a Query is outputted over the Q_send port.
        self.car_in = self.addInPort("car_in")
        # Port that receives Query events.
        self.Q_recv = self.addInPort("Q_recv")
        # Port for receiving QueryAck events
        self.Q_rack = self.addInPort("Q_rack")

        # Port for outputting generated cars
        self.car_out = self.addOutPort("car_out")
        # Sends a Query as soon as the newly sampled IAT says so.
        self.Q_send = self.addOutPort("Q_send")
        # Replies a QueryAck to a Query.
        self.Q_sack = self.addOutPort("Q_sack")


    def sortEventQueue(self):
        self.state.event_queue.sort(key=lambda x: x[1])
    def overwriteCarOutTime(self, new_time:float):
        self.state.car_out_event[1] = new_time
        self.sortEventQueue()

    def nextEvent(self):
        """
        :returns: The next event in the event queue and the time it occurs.
        """
        if len(self.state.event_queue) == 0:
            return [None, INFINITY]
        return self.state.event_queue[0]

    def timeAdvance(self):
        next_event = self.nextEvent()
        next_time = next_event[1]
        return max( 0.0, next_time )

    def addEvent(self, event: EventEnum, time: float):
        self.state.event_queue.append([event, time])
        # sort the event queue by time
        self.sortEventQueue()

    def addCarOutEvent(self, time:float):
        self.state.car_out_event = [EventEnum.CAR_OUT, time]
        self.state.event_queue.append(self.state.car_out_event)
        # sort the event queue by time
        self.sortEventQueue()

    def timePassed(self, time: float):
        """
        Handles the time passed since the last event.
        - Updates the time of all events in the event queue.
        - Updates the position of the car.
        - Updates the time since the last query.
        :param time: The time passed since the last event.

        """
        for event in self.state.event_queue:
            event[1] -= time
        self.state.time_since_last_query += time

        self.update_car_position(time)


    def popEvent(self):
        """
        Removes the first event from the event queue.
        :returns: The first event in the event queue.
        """
        return self.state.event_queue.pop(0)

    def outputFnc(self):
        # get the next event
        event = self.nextEvent()

        # if the next event is a car entering, Sends a Query on Q_send as soon as a new Car arrives on this RoadSegment
        if event[0] == EventEnum.SEND_QUERY:
            # get the car if it is still present
            if len(self.state.cars_present) > 0:
                car: Car = self.state.cars_present[0]

                return {
                    self.Q_send: Query(car.ID)
                }

        elif event[0] == EventEnum.RECEIVED_QUERY:
            '''
                Replies a QueryAck to a Query. 
                The QueryAck's t_until_dep equals the remaining time of the current Car on the RoadSegment 
                    (which can be infinity if the Car's velocity is 0). 
                If there is no Car, t_until_dep equals zero. 
                The QueryAck's lane is set w.r.t. the RoadSegment's lane; 
                    and the QueryAck's sideways is set to be false here. 
            '''
            # if there is a car on the road segment
            if len(self.state.cars_present) == 0:

                return {
                    self.Q_sack: self.state.query_ack_reply
                }
        elif event[0] == EventEnum.CAR_OUT:
            # get the car
            car: Car = self.state.cars_present[0]
            # send the car out
            return {
                self.car_out: car
            }

        return {}

    def intTransition(self):
        # get the time since last event
        time_passed = self.timeAdvance()

        # get the next event
        event = self.popEvent()

        # update the time of all events in the event queue
        self.timePassed(time_passed)

        if event[0] == EventEnum.CAR_OUT:
            # increase the car position with self.L
            self.state.cars_present[0].distance_traveled += self.L
            # remove the car from the road segment
            self.state.cars_present = []
            self.state.car_out_event = None
        if event[0] == EventEnum.SEND_QUERY:
            # if the car is still present and the car is not moving
            if len(self.state.cars_present) > 0 and self.state.cars_present[0].v <= 0.0001:
                # Add a new event to the event queue
                self.addEvent(EventEnum.SEND_QUERY, self.observ_delay)
        return self.state

    def extTransition(self, inputs):
        # get the time since last event
        time_passed = self.elapsed

        # update the time of all events in the event queue
        self.timePassed(time_passed)

        # a car arrives
        if self.car_in in inputs:
            car: Car = inputs[self.car_in]
            self.car_enter(car)

        # upon receiving a query
        if self.Q_recv in inputs:
            # Upon arrival of a Query, the RoadSegment waits for observ_delay time before replying a QueryAck on
            # the Q_sack output port. The outputted QueryAck's t_until_dep equals the remaining time of the current Car
            # on the RoadSegment (which can be infinity if the Car's velocity is 0). If there is no Car, t_until_dep
            # equals zero. Notice that multiple Query events may arrive during this waiting time,
            # all of whom should wait for exactly observ_delay time.
            query: Query = inputs[self.Q_recv]
            self.state.query_ack_reply = QueryAck(ID=query.ID, t_until_dep=self.state.t_until_dep, lane=self.lane, sideways=False)
            if len(self.state.cars_present) > 0:
                self.state.query_ack_reply.t_until_dep = self.state.remaining_x / self.state.cars_present[0].v if self.state.cars_present[0].v > 0.0000001 else INFINITY
            else:
                self.state.query_ack_reply.t_until_dep = 0.0
            self.addEvent(EventEnum.RECEIVED_QUERY, self.observ_delay)

        # Upon arrival of a QueryAck
        if self.Q_rack in inputs:
            query_ack: QueryAck = inputs[self.Q_rack]
            # if the car is still present:
            if len(self.state.cars_present) > 0:
                v_new, decelerate = self.get_car_new_velocity(self.state.cars_present[0], query_ack)
                # update car velocity
                if self.state.time_since_last_query >= 0.0001 and decelerate is False:
                    v_new = max(self.state.previous_v_new, v_new)
                self.state.cars_present[0].v = v_new
            self.state.time_since_last_query = 0.0

        return self.state

    def RemoveCarOutEvent(self):
        self.state.event_queue.remove(self.state.car_out_event)
        self.state.car_out_event = None

    def car_enter(self, car: Car):
        """
        Handles all the logic of a car entering the RoadSegment.

        :param car (Car):
            The Car that enters the RoadSegment.
            Can be called to pre-fill the RoadSegment with a Car.
        """
        self.state.cars_present.append(car)
        self.state.entered_car_count += 1

        # handle the time until departure and remaining distance of the car for this road segment
        if car.v <= 0.0001:
            self.state.t_until_dep = INFINITY
        else:
            self.state.t_until_dep = self.L / car.v
        self.state.remaining_x = self.L

        # If there already was a Car on the RoadSegment, a collision occurs.
        if len(self.state.cars_present) > 1:
            self.state.collisions += 1
            # We will make the incredibly bold assumption
            # that a crash results in total vaporization of both Cars, removing them from the simulation.
            self.state.cars_present = []
            # remove the car out event already in the event queue
            self.RemoveCarOutEvent()
            return
        else:
            # Sends a Query as soon as a new Car arrives on this RoadSegment (if there was no crash).
            self.addEvent(EventEnum.SEND_QUERY, 0.0)

        # Add a new event to the event queue
        self.addCarOutEvent(self.state.t_until_dep)

    def get_car_new_velocity(self, car: Car, query_ack: QueryAck):
        """
        the Car updates its velocity v to v_new as follows:

        - Accelerate or decelerate towards the Car's v_pref.
        - v_new should never exceed v_max, nor should it become less than 0
            (i.e., Cars will always drive forwards, or stand still).
        - A Car can at most accelerate an amount of dv_pos_max. It can also at most decelerate an amount of dv_neg_max.
            This is also applicable to the following bullets.
        - If the QueryAck's sideways flag is false:
            - The QueryAck's t_until_dep indicates the time remaining until the next RoadSegment becomes available.
                To avoid confusion, this value will be called t_no_coll.
            - If the current v_new allows the Car to stay on the RoadSegment as long or longer as t_no_coll,
                v_new becomes the new v.
            - Otherwise, the Car should decelerate as much as possible to avoid a collision.
                Thus, the maximum of v - dv_neg_max and remaining_x / t_no_coll becomes the new v.
        - Otherwise, if the QueryAck's sideways flag is true and priority is false, the Car should decelerate
            as much as possible.
        - Otherwise, if the QueryAck's sideways flag is true and priority is true, no special action should be taken.
        - Note that multiple QueryAcks may be received. If they arrive at the same simulation time
            (this may not necessarily happen during the same function call), the largest possible v_new should be
            used as v. Otherwise, the above description will be recomputed for every new QueryAck.

        :param car (Car):
            The Car that is on the RoadSegment.
        :param query_ack (QueryAck)
            The QueryAck that is received.
        """
        decelerate = False
        v_new = min(car.v_pref, car.v + car.dv_pos_max)

        # if the QueryAck's sideways flag is false
        if query_ack.sideways is False:
            t_no_coll = query_ack.t_until_dep
            # If the current v_new allows the Car to stay on the RoadSegment as long or longer as t_no_coll,
            # v_new becomes the new v.

            if t_no_coll <= self.state.remaining_x / v_new:
                pass
            # Otherwise, the Car should decelerate as much as possible to avoid a collision.
            # Thus, the maximum of v - dv_neg_max and remaining_x / t_no_coll becomes the new v.
            else:
                v_new = max(car.v - car.dv_neg_max, self.state.remaining_x / t_no_coll)

        # if the QueryAck's sideways flag is true
        if query_ack.sideways is True:
            # if priority is false, the Car should decelerate as much as possible
            if not self.priority:
                decelerate = True
                v_new = max(0.0, car.v - car.dv_neg_max)
            # if priority is true, no special action should be taken
            else:
                pass
        new_velocity: float = min(v_new, self.v_max)

        # calculate when the car will exit the road segment with this velocity
        # return 0 in the edge case that the car should leave the road at the same time but this function got called first
        estimated_time_until_exit = self.state.remaining_x / new_velocity if self.state.remaining_x > 0.00001 else 0.0
        self.state.t_until_dep = estimated_time_until_exit

        # overwrite event for car leaving
        self.overwriteCarOutTime(self.state.t_until_dep)
        return new_velocity, decelerate

    def update_car_position(self, time_passed: float):
        """
        Updates the position of the given car.

        :param time_passed (float):
            The time passed since the last event.
        """

        # we need to update self.t_until_dep and self.remaining_x
        # if there is a car on the road segment
        if len(self.state.cars_present) > 0:
            # get the car
            car: Car = self.state.cars_present[0]
            # if the car is not moving
            if car.v <= 0.0001:
                # the car is not moving, so the time until departure is infinity
                self.state.t_until_dep = INFINITY
                # the remaining distance stays the same
            # if the car is moving
            else:
                # we know the previous velocity which is just the current velocity we have and we know how much time has passed.
                # we first calculate the travelled distance:
                distance_traveled = car.v * time_passed
                # decrease the remaining distance
                self.state.remaining_x = max(self.state.remaining_x - distance_traveled, 0.0)
                # if self.state.remaining_x <= 0.0001:
                #     print(f"{10*'#'}car out{10*'#'}")
                #     # the car has left the road segment
                #     self.addEvent(EventEnum.CAR_OUT, 0.0)

                # calculate the new time until departure
                self.state.t_until_dep = self.state.remaining_x / car.v
        else:
            self.state.t_until_dep = 0.0
            self.state.remaining_x = 0.0
