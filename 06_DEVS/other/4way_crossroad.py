from typing import List, Union

from pypdevs.DEVS import CoupledDEVS

from components.collector import Collector
from components.fork import Fork
from components.gasstation import GasStation
from components.generator import Generator
from components.roadsegment import RoadSegment
from components.sidemarker import SideMarker
from other.RoadCoupledDEVS import RoadCoupledDEVS
from components.crossroads import CrossRoads

# constants for the crossroad
L = 5  # length of the road segment
v_max = 30  # maximum allowed velocity

IAT_min = 5
IAT_max = 7
v_pref_mu = 30
v_pref_sigma = 10
destinations = ["collector"]
limit = 50

class biDirectionalRoad(RoadCoupledDEVS):
    """
        A bidirectional road, consisting out of 2 road segments
    """
    def __init__(self,name):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(biDirectionalRoad, self).__init__(name)
        # create the 2 road segments
        self.road_segment_1:RoadSegment = self.addSubModel(RoadSegment(f"{name}_segment_1", L, v_max))
        self.road_segment_2: RoadSegment = self.addSubModel(RoadSegment(f"{name}_segment_2", L, v_max))

    def connectBidirectionalRoad(self, other):
        """
            Connects the 2 road segments of this road to the 2 road segments of another road
        """
        self.connectComponents([
            self.road_segment_1,
            other.road_segment_1,
        ])
        self.connectComponents([
            other.road_segment_2,
            self.road_segment_2,
            ])
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
    def __init__(self, name):
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
        self.road_segment_1: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_bidirectional_road_1"))
        self.road_segment_2: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_bidirectional_road_2"))
        self.road_segment_3: biDirectionalRoad = self.addSubModel(biDirectionalRoad(f"{name}_bidirectional_road_3"))

        # connect all components
        self.road_segment_1.connectBidirectionalRoad(self.road_segment_2)
        self.road_segment_2.connectBidirectionalRoad(self.road_segment_3)

        self.road_segment_1.connectSingleRoads(self.collecter,self.generator)

        self.incoming: RoadSegment = self.road_segment_3.road_segment_2
        self.outgoing: RoadSegment = self.road_segment_3.road_segment_1







class fourwayCrossroad(RoadCoupledDEVS):
    """
        A 4-way CrossRoads, linked to 4 Generators and 4 Collectors.
        3 sequential RoadSegments to each input and output branch of the CrossRoads.
    """

    def __init__(self, name, limit=limit):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(fourwayCrossroad, self).__init__(name)
        # create a sequential road for each input and output branch
        self.road_1 = self.addSubModel(sequentialRoad(f"north"))
        self.road_2 = self.addSubModel(sequentialRoad(f"east"))
        self.road_3 = self.addSubModel(sequentialRoad(f"south"))
        self.road_4 = self.addSubModel(sequentialRoad(f"west"))

        # create the crossroad
        self.crossroad: CrossRoads = self.addSubModel(CrossRoads("crossroad"))

        # connect the crossroad to the sequential roads
        self.connectCrossroad([self.road_1, self.road_2, self.road_3, self.road_4])

    def connectCrossroad(self, sequential_roads: List[sequentialRoad]):
        """
            Connects the crossroad to a sequential road
        """
        road:sequentialRoad
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
            self.connectPorts(inp_and_out[0], road.incoming.car_out)
            self.connectPorts(inp_and_out[1], road.incoming.Q_send)
            self.connectPorts(inp_and_out[2], road.incoming.Q_sack)
            self.connectPorts(inp_and_out[3], road.outgoing.car_in)
            self.connectPorts(inp_and_out[4], road.outgoing.Q_recv)
            self.connectPorts(inp_and_out[5], road.outgoing.Q_rack)





    def getCollector(self):
        return self.collector

    def getNumberCrashes(self):
        collisions = 0
        for component in self.road_segments:
            collisions += component.state.collisions
        return collisions

