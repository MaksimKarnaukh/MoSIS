from typing import List

from components.collector import Collector
from components.crossroads import CrossRoads
from components.generator import Generator
from components.roadsegment import RoadSegment
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
        self.road_segment_1_car_out = self.addOutPort("car_out_road_segment_1")
        self.road_segment_1_car_in = self.addInPort("car_in_road_segment_1")
        self.road_segment_1_Q_send = self.addOutPort("Q_send_road_segment_1")
        self.road_segment_1_Q_recv = self.addInPort("Q_recv_road_segment_1")
        self.road_segment_1_Q_sack = self.addOutPort("Q_sack_road_segment_1")
        self.road_segment_1_Q_rack = self.addInPort("Q_rack_road_segment_1")

        self.road_segment_2_car_out = self.addOutPort("car_out_road_segment_2")
        self.road_segment_2_car_in = self.addInPort("car_in_road_segment_2")
        self.road_segment_2_Q_send = self.addOutPort("Q_send_road_segment_2")
        self.road_segment_2_Q_recv = self.addInPort("Q_recv_road_segment_2")
        self.road_segment_2_Q_sack = self.addOutPort("Q_sack_road_segment_2")
        self.road_segment_2_Q_rack = self.addInPort("Q_rack_road_segment_2")

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

    def connectBidirectionalRoad(self, other:'biDirectionalRoad', parent: RoadCoupledDEVS):
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
        self.collecter = self.addSubModel(Collector(f"{name}_collector"))

        # create the 3 road segments
        self.road_segment_1: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_bidirectional_road_1",
                                                                  L=L, v_max=v_max))
        self.road_segment_2: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_bidirectional_road_2",
                                                                  L=L, v_max=v_max))
        self.road_segment_3: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_bidirectional_road_3",
                                                                  L=L, v_max=v_max))

        # connect all components
        self.road_segment_1.connectBidirectionalRoad(self.road_segment_2,parent=self)
        self.road_segment_2.connectBidirectionalRoad(self.road_segment_3, parent=self)

        # connect the generator
        self.connectPorts(self.generator.car_out, self.road_segment_1.road_segment_1_car_in)
        self.connectPorts(self.generator.Q_send, self.road_segment_1.road_segment_1_Q_recv)
        self.connectPorts(self.road_segment_1.road_segment_1_Q_sack, self.generator.Q_rack)

        # connect the collector
        self.connectPorts(self.road_segment_1.road_segment_2_car_out, self.collecter.car_in)

        # create the incoming and outgoing road ports
        self.car_out = self.addOutPort("car_out")
        self.Q_sack = self.addOutPort("Q_sack")
        self.Q_send = self.addOutPort("Q_send")

        self.car_in = self.addInPort("car_in")
        self.Q_recv = self.addInPort("Q_recv")
        self.Q_rack = self.addInPort("Q_rack")

        # connect the incoming and outgoing road ports to the road segments
        self.connectPorts(self.road_segment_3.road_segment_1_car_out, self.car_out)
        self.connectPorts(self.road_segment_3.road_segment_1_Q_send,self.Q_send)
        self.connectPorts(self.Q_recv, self.road_segment_3.road_segment_1_Q_recv)

        self.connectPorts(self.car_in, self.road_segment_3.road_segment_2_car_in )
        self.connectPorts(self.Q_rack, self.road_segment_3.road_segment_2_Q_rack)
        self.connectPorts(self.road_segment_3.road_segment_2_Q_sack, self.Q_sack)

        # self.incoming: RoadSegment = self.road_segment_3.road_segment_2
        # self.outgoing: RoadSegment = self.road_segment_3.road_segment_1
    def __repr__(self):
        return f"sequentialRoad({self.name})"
class fourwayCrossroad(RoadCoupledDEVS):
    """
        A 4-way CrossRoads, linked to 4 Generators and 4 Collectors.
        3 sequential RoadSegments to each input and output branch of the CrossRoads.
    """
    observ_delay_default: float = 0.1

    def __init__(self, name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit, observ_delay=observ_delay_default):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(fourwayCrossroad, self).__init__(name)
        # create a sequential road for each input and output branch
        self.road_north = self.addSubModel(
            sequentialRoad(f"north", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                           v_pref_sigma=v_pref_sigma, destinations=destinations, limit=limit))

        self.road_east = self.addSubModel(
            sequentialRoad(f"east", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                           v_pref_sigma=v_pref_sigma, destinations=destinations, limit=limit))
        self.road_south = self.addSubModel(
            sequentialRoad(f"south", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                           v_pref_sigma=v_pref_sigma, destinations=destinations, limit=limit))
        self.road_west = self.addSubModel(
            sequentialRoad(f"west", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                           v_pref_sigma=v_pref_sigma, destinations=destinations, limit=limit))
        self.destinations = destinations
        # create the crossroad
        self.crossroad: CrossRoads = self.addSubModel(CrossRoads("crossroad", destinations=[['N'],['W'],['S'],['E']], L=L, v_max= v_max, observ_delay=observ_delay))

        # connect the crossroad to the sequential roads
        self.connectCrossroad([self.road_north, self.road_east, self.road_south, self.road_west])

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
            self.connectPorts(road.car_out, inp_and_out[0] )
            self.connectPorts(road.Q_send, inp_and_out[1])
            self.connectPorts(road.Q_sack, inp_and_out[2] )

            self.connectPorts(inp_and_out[3], road.car_in)
            self.connectPorts(inp_and_out[4], road.Q_recv)
            self.connectPorts(inp_and_out[5], road.Q_rack)

    # def getCollector(self):
    #     return self.collector
    #
    # def getNumberCrashes(self):
    #     collisions = 0
    #     for component in self.road_segments:
    #         collisions += component.state.collisions
    #     return collisions
    def __repr__(self):
        return f"fourwayCrossroad({self.name})"

    def getCollectors(self):
        return [self.road_north.collecter, self.road_east.collecter, self.road_south.collecter, self.road_west.collecter]

    def getNumberCrashes(self):
        collisions = 0

        # loop over all components
        for component in self.component_set:
            # if the component is a road segment
            if isinstance(component, RoadSegment):
                # add the collisions to the total amount
                collisions += component.state.collisions
        return collisions