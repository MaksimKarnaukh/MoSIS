from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
from typing import List
from components.messages import Query, QueryAck, Car
from components.querystate import QueryState
from enum import Enum
from components.roadsegment import RoadSegmentState, RoadSegment
from components.roadsegment import EventEnum


class CrossRoadSegment(RoadSegment):
    """
    Acts as if it were a part of a crossroads. I.e.,
    this is a location where two roads merge and split at the same time.
    Combining multiple of these segments together results in a CrossRoad.
    Given that this block inherits from RoadSegment, all aspects discussed there are also applicable.
    """
    def __init__(self, name, L: float, v_max: float, destinations: List[str]):
        """
        :param name (str):
            The name for this model. Must be unique inside a Coupled DEVS.
        :param L (float):
            The length of the RoadSegment.
            Given that the average Car is about 5 meters in length, a good estimate value for L would therefore be 5 meters.
        :param v_max (float):
            The maximal allowed velocity on this RoadSegment.
        :param destinations (list):
            A non-empty list of potential (string) destinations for the Cars.
        """
        super(CrossRoadSegment, self).__init__(name, L, v_max)
        self.destinations: List[str] = destinations

        # Cars can enter on this segment as if it were the normal car_in port.
        # However, this port is only used for Cars that were already on the crossroads.
        self.car_in_cr = self.addInPort("car_in_cr")

        # Outputs the Cars that must stay on the crossroads.
        # In essence, these are all the Cars that have a destination not in this CrossRoadSegment's destinations field.
        self.car_out_cr = self.addOutPort("car_out_cr")

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
            if len(self.state.cars_present) > 0:
                # get the car
                car: Car = self.state.cars_present[0]
                return {
                    self.Q_sack: QueryAck(car.ID, self.state.t_until_dep, self.lane, False)
                }
        elif event[0] == EventEnum.CAR_OUT:
            # get the car
            car: Car = self.state.cars_present[0]

            # car_out_cr : Outputs the Cars that must stay on the crossroads.
            # In essence, these are all the Cars that have a destination not in this CrossRoadSegment's destinations field.

            # if the car's destination is not in the destinations list
            if car.destination not in self.destinations:
                # send the car out
                return {
                    self.car_out_cr: car
                }
            else:
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

        if self.car_in_cr in inputs:
            car: Car = inputs[self.car_in_cr]
            self.car_enter(car)

        # upon receiving a query
        if self.Q_recv in inputs:
            # Upon arrival of a Query, the RoadSegment waits for observ_delay time before replying a QueryAck on
            # the Q_sack output port. The outputted QueryAck's t_until_dep equals the remaining time of the current Car
            # on the RoadSegment (which can be infinity if the Car's velocity is 0). If there is no Car, t_until_dep
            # equals zero. Notice that multiple Query events may arrive during this waiting time,
            # all of whom should wait for exactly observ_delay time.
            query: Query = inputs[self.Q_recv]
            if len(self.state.cars_present) > 0:
                self.state.query_ack_reply.t_until_dep = self.state.cars_present[0].remaining_x / self.state.cars_present[0].v
            else:
                self.state.query_ack_reply.t_until_dep = 0.0
            self.state.query_ack_reply = QueryAck(query.ID, self.state.t_until_dep)
            self.addEvent(EventEnum.RECEIVED_QUERY, self.observ_delay)

        # Upon arrival of a QueryAck
        if self.Q_rack in inputs:
            query_ack: QueryAck = inputs[self.Q_rack]

            # update car velocity
            v_new = self.get_car_new_velocity(self.state.cars_present[0], query_ack)
            if self.state.time_since_last_query >= 0.0001:
                v_new = max(self.state.previous_v_new, v_new)
            self.state.cars_present[0].v = v_new

            self.state.time_since_last_query = 0.0

        return self.state


class CrossRoads(CoupledDEVS):
    """
    Represents a free-for-all n-way crossroads.
    For the sake of readability, the outer ports are here encoded using North (N), East (E), South (S), West (W);
    instead of using indexes.
    """
    def __init__(self, name, destinations: List[List[str]], L: float, v_max: float, observ_delay: float):
        """
        :param name (str):
            The name for this model. Must be unique inside a Coupled DEVS.
        :param destinations (list):
            A list of lists of destinations for the CrossRoads.
            The amount of sub-lists indicates how many branches the CrossRoads has.
            Each sub-list is given to the CrossRoadSegments in order.
        :param L (float):
            The length of the individual CrossRoadSegments.
        :param v_max (float):
            The maximal allowed velocity on the CrossRoads.
        :param observ_delay (float):
            The observ_delay for the CrossRoadSegments.
        """
        super(CrossRoads, self).__init__(name)
        self.L: float = L
        self.v_max: float = v_max
        self.observ_delay: float = observ_delay
        self.destinations = destinations

        # The amount of sub-lists of destinations indicates how many branches the CrossRoads has.
        self.branches_amount = len(destinations)

        # create the crossroad segments and add the segments to the coupled model
        self.segments = []
        for i in range(self.branches_amount):
            cross_road_segment = CrossRoadSegment("segment_" + str(i), L, v_max, destinations[i])
            cross_road_segment.observ_delay = observ_delay
            self.segments.append(cross_road_segment)
            self.addSubModel(cross_road_segment)

        # connect the segments in a circle
        for i in range(self.branches_amount):
            # connect the car_out_cr of the current segment to the car_in_cr of the next segment
            self.connectPorts(self.segments[i].car_out_cr, self.segments[(i + 1) % self.branches_amount].car_in_cr)

            # also connect the Q_send to the Q_recv of the next segment and
            # connect the Q_sack to the Q_rack of the previous segment
            self.connectPorts(self.segments[i].Q_send, self.segments[(i + 1) % self.branches_amount].Q_recv)
            self.connectPorts(self.segments[i].Q_sack, self.segments[(i - 1) % self.branches_amount].Q_rack)

        # add outside input and output ports (per branch)
        self.inp_and_out_ports = []
        for i in range(self.branches_amount):

            self.inp_and_out_ports.append([
                self.addInPort("car_in_" + str(i)),
                self.addInPort("Q_recv_" + str(i)),
                self.addInPort("Q_rack_" + str(i)),
                self.addOutPort("car_out_" + str(i)),
                self.addOutPort("Q_send_" + str(i)),
                self.addOutPort("Q_sack_" + str(i))
            ])

        # connect each branch to its correct outside ports
        for i in range(self.branches_amount):
            self.connectPorts(self.inp_and_out_ports[i][0], self.segments[i].car_in)
            self.connectPorts(self.inp_and_out_ports[i][1], self.segments[i].Q_recv)
            self.connectPorts(self.inp_and_out_ports[i][2], self.segments[(i - 1) % self.branches_amount].Q_rack)
            self.connectPorts(self.segments[(i - 1) % self.branches_amount].car_out, self.inp_and_out_ports[i][3])
            self.connectPorts(self.segments[(i - 1) % self.branches_amount].Q_send, self.inp_and_out_ports[i][4])
            self.connectPorts(self.segments[i].Q_sack, self.inp_and_out_ports[i][5])
