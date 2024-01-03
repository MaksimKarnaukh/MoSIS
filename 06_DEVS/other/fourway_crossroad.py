from typing import List

from components.collector import Collector
from components.crossroads import CrossRoads, CrossRoadSegment
from components.generator import Generator
from components.roadsegment import RoadSegment
from components.sidemarker import SideMarker
from other.RoadCoupledDEVS import RoadCoupledDEVS


class biDirectionalRoad(RoadCoupledDEVS):
    """
        A bidirectional road, consisting out of 2 road segments
    """

    def __init__(self, name, L, v_max):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(biDirectionalRoad, self).__init__(name)
        # create the 2 road segments
        self.road_segment_1: RoadSegment = self.addSubModel(RoadSegment(f"{name}_incoming", L, v_max))
        self.road_segment_2: RoadSegment = self.addSubModel(RoadSegment(f"{name}_outgoing", L, v_max))

        # create the two road segments
        self.road_segment_1_car_out = self.addOutPort("road_segment_1_car_out")
        self.road_segment_1_car_in = self.addInPort("road_segment_1_car_in")
        self.road_segment_1_Q_send = self.addOutPort("road_segment_1_Q_send")
        self.road_segment_1_Q_recv = self.addInPort("road_segment_1_Q_recv")
        self.road_segment_1_Q_sack = self.addOutPort("road_segment_1_Q_sack")
        self.road_segment_1_Q_rack = self.addInPort("road_segment_1_Q_rack")

        self.road_segment_2_car_out = self.addOutPort("road_segment_2_car_out")
        self.road_segment_2_car_in = self.addInPort("road_segment_2_car_in")
        self.road_segment_2_Q_send = self.addOutPort("road_segment_2_Q_send")
        self.road_segment_2_Q_recv = self.addInPort("road_segment_2_Q_recv")
        self.road_segment_2_Q_sack = self.addOutPort("road_segment_2_Q_sack")
        self.road_segment_2_Q_rack = self.addInPort("road_segment_2_Q_rack")

        # connect the out of the segments with the ports
        self.connectPorts(self.road_segment_1.car_out, self.road_segment_1_car_out)
        self.connectPorts(self.road_segment_1_car_in, self.road_segment_1.car_in)
        self.connectPorts(self.road_segment_1.Q_send, self.road_segment_1_Q_send)
        self.connectPorts(self.road_segment_1_Q_recv, self.road_segment_1.Q_recv)
        self.connectPorts(self.road_segment_1.Q_sack, self.road_segment_1_Q_sack)
        self.connectPorts(self.road_segment_1_Q_rack, self.road_segment_1.Q_rack)

        self.connectPorts(self.road_segment_2.car_out, self.road_segment_2_car_out)
        self.connectPorts(self.road_segment_2_car_in, self.road_segment_2.car_in)
        self.connectPorts(self.road_segment_2.Q_send, self.road_segment_2_Q_send)
        self.connectPorts(self.road_segment_2_Q_recv, self.road_segment_2.Q_recv)
        self.connectPorts(self.road_segment_2.Q_sack, self.road_segment_2_Q_sack)
        self.connectPorts(self.road_segment_2_Q_rack, self.road_segment_2.Q_rack)

    def connectBidirectionalRoad(self, other: 'biDirectionalRoad', parent: RoadCoupledDEVS):
        """
            Connects the 2 road segments of this road to the 2 road segments of another road
        """

        parent.connectPorts(self.road_segment_1_car_out, other.road_segment_1_car_in)
        parent.connectPorts(self.road_segment_1_Q_send, other.road_segment_1_Q_recv)
        parent.connectPorts(other.road_segment_1_Q_sack, self.road_segment_1_Q_rack)

        parent.connectPorts(other.road_segment_2_car_out, self.road_segment_2_car_in)
        parent.connectPorts(other.road_segment_2_Q_send, self.road_segment_2_Q_recv)
        parent.connectPorts(self.road_segment_2_Q_sack, other.road_segment_2_Q_rack)

    def __repr__(self):
        return f"biDirectionalRoad({self.name})"

    def connectSingleRoads(self, road1, road2):
        """
            Connects the 2 road segments of this road to the 2 road segments of another road
        """
        self.connectComponents([
            self.road_segment_1,
            road1,
        ])
        self.connectComponents([
            road2,
            self.road_segment_2,
        ])


class sequentialRoad(RoadCoupledDEVS):
    """
     An in- and outroad for the crossroad, consisting out of a generator, collector and 3 bidirectionalroad segments
    """

    def __init__(self, name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(RoadCoupledDEVS, self).__init__(name)
        # create the generator
        self.generator = self.addSubModel(
            Generator(name=f"{name}_gen",
                      IAT_min=IAT_min, IAT_max=IAT_max,
                      v_pref_mu=v_pref_mu, v_pref_sigma=v_pref_sigma,
                      destinations=destinations, limit=limit))

        # create the collector
        self.collecter = self.addSubModel(Collector(f"{name}_collector"))

        # create the 3 road segments
        self.last_segment: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_last_segment",
                                                                                  L=L, v_max=v_max))
        self.middle_segment: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_middle_segment",
                                                                                    L=L, v_max=v_max))
        self.core_segment: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_core_segment",
                                                                                  L=L, v_max=v_max))

        # connect all components
        self.last_segment.connectBidirectionalRoad(self.middle_segment, parent=self)
        self.middle_segment.connectBidirectionalRoad(self.core_segment, parent=self)

        # connect the generator
        self.connectPorts(self.generator.car_out, self.last_segment.road_segment_1_car_in)
        self.connectPorts(self.generator.Q_send, self.last_segment.road_segment_1_Q_recv)
        self.connectPorts(self.last_segment.road_segment_1_Q_sack, self.generator.Q_rack)

        # connect the collector
        self.connectPorts(self.last_segment.road_segment_2_car_out, self.collecter.car_in)

        # create the incoming and outgoing road ports
        self.car_out = self.addOutPort("car_out")
        self.Q_rack = self.addInPort("Q_rack")
        self.Q_send = self.addOutPort("Q_send")

        self.car_in = self.addInPort("car_in")
        self.Q_sack = self.addOutPort("Q_sack")
        self.Q_recv = self.addInPort("Q_recv")

        # connect the incoming and outgoing road ports to the road segments
        self.connectPorts(self.core_segment.road_segment_1_car_out, self.car_out)
        self.connectPorts(self.core_segment.road_segment_1_Q_send, self.Q_send)
        self.connectPorts(self.Q_rack, self.core_segment.road_segment_1_Q_rack)

        self.connectPorts(self.car_in, self.core_segment.road_segment_2_car_in)
        self.connectPorts(self.Q_recv, self.core_segment.road_segment_2_Q_recv)
        self.connectPorts(self.core_segment.road_segment_2_Q_sack, self.Q_sack)

    def __repr__(self):
        return f"sequentialRoad({self.name})"

    def markOutgoingAsPriority(self):
        self.core_segment.road_segment_1.priority = True


class fourwayCrossroad(RoadCoupledDEVS):
    """
        A 4-way CrossRoads, linked to 4 Generators and 4 Collectors.
        3 sequential RoadSegments to each input and output branch of the CrossRoads.
    """
    observ_delay_default: float = 0.1

    def __init__(self, name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, limit,
                 observ_delay=observ_delay_default):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(fourwayCrossroad, self).__init__(name)
        self.destinations = ['N', 'W', 'S', 'E']

        self.initializeSequentialRoads(L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, limit)

        # create the crossroad
        self.crossroad: CrossRoads = self.addSubModel(
            CrossRoads("crossroad", destinations=[['N'], ['W'], ['S'], ['E']], L=L, v_max=v_max,
                       observ_delay=observ_delay))

        # connect the crossroad to the sequential roads
        self.connectCrossroad([self.road_north,
                               self.road_west,                               self.road_south,self.road_east
                              ])

    def connectCrossroad(self, sequential_roads: List[sequentialRoad]):
        """
            Connects the crossroad to the sequential roads
        """
        road: sequentialRoad
        for index, road in enumerate(sequential_roads):
            inp_and_out = self.crossroad.inp_and_out_ports[index]

            """
                car_in
                Q_recv
                Q_rack
                car_out
                Q_send
                Q_sack
            """
            print([str(inp_and_out_port.name) for inp_and_out_port in inp_and_out])
            self.connectPorts(road.car_out, inp_and_out[0])
            self.connectPorts(road.Q_send, inp_and_out[1])
            self.connectPorts(road.Q_sack, inp_and_out[2])

            self.connectPorts(inp_and_out[3], road.car_in)
            self.connectPorts(inp_and_out[4], road.Q_recv)
            self.connectPorts(inp_and_out[5], road.Q_rack)


    def __repr__(self):
        return f"fourwayCrossroad({self.name})"

    def getCollectors(self):
        return [
            self.road_north.collecter
            ,self.road_east.collecter, self.road_south.collecter, self.road_west.collecter
        ]

    def getNumberCrashes(self):
        collisions = 0

        # loop over all components
        for component in self.component_set:
            # if the component is a road segment
            if isinstance(component, RoadSegment):
                # add the collisions to the total amount
                collisions += component.state.collisions
        return collisions



    def initializeSequentialRoads(self, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, limit):
        # create a sequential road for each input and output branch
        self.road_north = self.addSubModel(
            sequentialRoad(f"north", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                           v_pref_sigma=v_pref_sigma, destinations=self.destinations, limit=limit))

        self.road_east = self.addSubModel(
            sequentialRoad(f"east", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                           v_pref_sigma=v_pref_sigma, destinations=self.destinations, limit=limit))
        self.road_south = self.addSubModel(
            sequentialRoad(f"south", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                           v_pref_sigma=v_pref_sigma, destinations=self.destinations, limit=limit))
        self.road_west = self.addSubModel(
            sequentialRoad(f"west", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                           v_pref_sigma=v_pref_sigma, destinations=self.destinations, limit=limit))

class SequentialRoadOutRoadExposed(sequentialRoad):
    """
        A sequential road, consisting out of a generator, collector and 3 bidirectionalroad segments
        All the ports of the outgoing road segment are exposed to the parent coupled model (car_in, Q_recv, Q_sack)
    """

    def __init__(self, name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit):
        super().__init__(name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit)

        # create the incoming and outgoing road ports
        self.outgoingroad_car_in = self.addInPort("outgoingroad_car_in")
        self.outgoingroad_Q_recv = self.addInPort("outgoingroad_Q_recv")
        self.outgoingroad_Q_sack = self.addOutPort("outgoingroad_Q_sack")

        # connect the incoming and outgoing road ports to the ports of the respectable road segment
        self.connectPorts(self.outgoingroad_car_in, self.core_segment.road_segment_1_car_in)
        self.connectPorts(self.outgoingroad_Q_recv, self.core_segment.road_segment_1_Q_recv)
        self.connectPorts(self.core_segment.road_segment_1_Q_sack, self.outgoingroad_Q_sack)


class VoorangVanRechtsCrossRoad(fourwayCrossroad):
    def __init__(self, name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, limit):
        super().__init__(name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, limit)

        # create the sidemarkers
        self.sidemarker_north: SideMarker = self.addSubModel(SideMarker(f"sidemarker_north"))
        self.sidemarker_east: SideMarker = self.addSubModel(SideMarker(f"sidemarker_east"))
        self.sidemarker_south: SideMarker = self.addSubModel(SideMarker(f"sidemarker_south"))
        self.sidemarker_west: SideMarker = self.addSubModel(SideMarker(f"sidemarker_west"))
        seq_road: sequentialRoad
        # mark the outgoing road (incoming to the crossroad) of each sequential road as priority
        for seq_road in [self.road_north, self.road_east, self.road_south, self.road_west]:
            seq_road.markOutgoingAsPriority()
        """

            car_in
            Q_recv
            Q_rack
            car_out
            Q_send
            Q_sack
        """
        # connect the crossroad to the sidemarkers
        # a car from the east has priority over a car from the south


        directionlist = ['W', 'S', 'E', 'N']
        sidemarkers = [self.sidemarker_west, self.sidemarker_south, self.sidemarker_east, self.sidemarker_north]
        roads = [self.road_west, self.road_south, self.road_east, self.road_north]


        for i in range(4):
            direction = directionlist[i]
            sidemarker = sidemarkers[i]
            priority_road = roads[i]
            non_priority_road_ports = self.crossroad.getInAndOutPorts(direction)

            self.connectSidemarker(sidemarker, priority_road, non_priority_road_ports)





    def connectSidemarker(self, sidemarker:SideMarker, priority_road, non_priority_road_ports):
        prioritized_side_q_sack = priority_road.outgoingroad_Q_sack
        prioritized_side_q_recv = priority_road.outgoingroad_Q_recv
        non_prio_Q_send = non_priority_road_ports["Q_send"]
        non_prio_Q_rack = non_priority_road_ports["Q_rack"]
        self.connectSidemarkerPorts(sidemarker=sidemarker,
                               prioritized_side_q_sack=prioritized_side_q_sack,
                               prioritized_side_q_recv=prioritized_side_q_recv,
                               non_prio_Q_send=non_prio_Q_send,
                               non_prio_Q_rack=non_prio_Q_rack)
    def connectSidemarkerPorts(self, sidemarker, prioritized_side_q_sack, prioritized_side_q_recv, non_prio_Q_send,
                          non_prio_Q_rack):
        self.connectPorts(prioritized_side_q_sack, sidemarker.mi)
        self.connectPorts(sidemarker.mo, non_prio_Q_rack)
        self.connectPorts(non_prio_Q_send, prioritized_side_q_recv)

    def initializeSequentialRoads(self, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, limit):

        # create a sequential road for each input and output branch with their outgoing road ports exposed
        self.road_north: SequentialRoadOutRoadExposed = self.addSubModel(
            SequentialRoadOutRoadExposed(f"north", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max,
                                         v_pref_mu=v_pref_mu,
                                         v_pref_sigma=v_pref_sigma, destinations=self.destinations, limit=limit))

        self.road_east: SequentialRoadOutRoadExposed = self.addSubModel(
            SequentialRoadOutRoadExposed(f"east", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max,
                                         v_pref_mu=v_pref_mu,
                                         v_pref_sigma=v_pref_sigma, destinations=self.destinations, limit=limit))
        self.road_south: SequentialRoadOutRoadExposed = self.addSubModel(
            SequentialRoadOutRoadExposed(f"south", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max,
                                         v_pref_mu=v_pref_mu,
                                         v_pref_sigma=v_pref_sigma, destinations=self.destinations, limit=limit))
        self.road_west = self.addSubModel(
            SequentialRoadOutRoadExposed(f"west", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max,
                                         v_pref_mu=v_pref_mu,
                                         v_pref_sigma=v_pref_sigma, destinations=self.destinations, limit=limit))
class Roundabout(fourwayCrossroad):
    def __init__(self, name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, limit):
        super().__init__(name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, limit)

        # create the sidemarkers
        self.sidemarker_north: SideMarker = self.addSubModel(SideMarker(f"sidemarker_north"))
        self.sidemarker_east: SideMarker = self.addSubModel(SideMarker(f"sidemarker_east"))
        self.sidemarker_south: SideMarker = self.addSubModel(SideMarker(f"sidemarker_south"))
        self.sidemarker_west: SideMarker = self.addSubModel(SideMarker(f"sidemarker_west"))

        # mark the outgoing road (incoming to the crossroad) of each sequential road as priority
        for seq_road in [self.road_north, self.road_east, self.road_south, self.road_west]:
            seq_road.markOutgoingAsPriority()

        directionlist = ['W', 'S', 'E', 'N']
        sidemarkers = [self.sidemarker_west, self.sidemarker_south, self.sidemarker_east, self.sidemarker_north]
        roads = [self.road_west, self.road_south, self.road_east, self.road_north]


        for i in range(4):
            direction = directionlist[i]
            sidemarker = sidemarkers[i]
            priority_road = roads[i]
            non_priority_road_ports = self.crossroad.getInAndOutPorts(direction)

            self.connectSidemarker(sidemarker, priority_road, non_priority_road_ports)





    def connectSidemarker(self, sidemarker:SideMarker, priority_road_ports: dict, non_priority_road: sequentialRoad):
        prioritized_side_q_sack = priority_road_ports["Q_sack"]
        prioritized_side_q_recv = priority_road_ports["Q_recv"]
        non_prio_Q_send = non_priority_road.Q_send
        non_prio_Q_rack = non_priority_road.Q_rack
        self.connectSidemarkerPorts(sidemarker=sidemarker,
                               prioritized_side_q_sack=prioritized_side_q_sack,
                               prioritized_side_q_recv=prioritized_side_q_recv,
                               non_prio_Q_send=non_prio_Q_send,
                               non_prio_Q_rack=non_prio_Q_rack)
