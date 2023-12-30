from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random

from components.collector import Collector
from components.fork import Fork
from components.generator import Generator
from components.gasstation import GasStation
from components.roadsegment import RoadSegment
from components.sidemarker import SideMarker


class RoadStretch(CoupledDEVS):
    """
    Create a single RoadStretch (a Coupled DEVS),
    that starts with a Generator, has a variable amount of RoadSegments, and ends in a Collector.
    In the middle of this RoadStretch, there should be a Fork, where the second output goes
    into the sequence of RoadSegment, GasStation, RoadSegment.
    Eventually, this final RoadSegment merges back into the RoadStretch.
    Don't forget the SideMarker! You may use as many layers of hierarchy as desired for a clean,
    easily understandable solution.
    """

    L = 5 # length of the road segment
    v_max = 30 # maximum allowed velocity

    def __init__(self, name):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(RoadStretch, self).__init__(name)

        # create the generator
        self.generator = self.addSubModel(Generator("gen"))
        # create the fork
        self.fork = self.addSubModel(Fork("fork", self.L, self.v_max))
        # create the collector
        self.collector = self.addSubModel(Collector("collector"))
        # create the side marker
        self.side_marker = self.addSubModel(SideMarker("side_marker"))
        # create the gas station
        self.gas_station = self.addSubModel(GasStation("gas_station"))

        # create the 7 road segments
        # first road segment connected to the generator
        self.road_segment_gen = self.addSubModel(RoadSegment("road_segment_gen", self.L, self.v_max))
        # to the right of fork, north from left to right
        self.road_segment_n1 = self.addSubModel(RoadSegment("road_segment_n1", self.L, self.v_max))
        self.road_segment_n2 = self.addSubModel(RoadSegment("road_segment_n2", self.L, self.v_max))
        self.road_segment_n3 = self.addSubModel(RoadSegment("road_segment_n3", self.L, self.v_max, priority=True))
        self.road_segment_n4 = self.addSubModel(RoadSegment("road_segment_n4", self.L, self.v_max))
        # to the left of fork, south from left to right
        self.road_segment_s1 = self.addSubModel(RoadSegment("road_segment_s1", self.L, self.v_max))
        self.road_segment_s2 = self.addSubModel(RoadSegment("road_segment_s2", self.L, self.v_max))

        # connect all components on the northern line
        self.connectComponentsDefault([
            self.generator,
            self.road_segment_gen,
            self.fork,
            self.road_segment_n1,
            self.road_segment_n2,
            self.road_segment_n3,
            self.road_segment_n4,
            self.collector
            ])

        # connect fork to road segment s1
        self.connectComponentsDefault([
            self.fork,
            self.road_segment_s1,
        ])

        # connect all components of the southern side
        self.connectComponentsToGasStation([
            self.road_segment_s1,
            self.road_segment_s2
        ])

        # connect road segment s2 to road segment n4
        self.connectComponentsDefault([
            self.road_segment_s2,
            self.road_segment_n4
        ])

        # connect the side marker to road segment n3 and s2
        self.connectPorts(self.road_segment_n3.Q_sack, self.side_marker.mi)
        self.connectPorts(self.side_marker.mo, self.road_segment_s2.Q_rack)


    def connectComponentsDefault(self, components: list):
        """
        Connects all components in the list to each other in the order they are given.
        :param components: The components to connect.
        """
        for i in range(len(components) - 1):
            self.connectPorts(components[i].car_out, components[i + 1].car_in)
            self.connectPorts(components[i].Q_send, components[i + 1].Q_recv)
            self.connectPorts(components[i + 1].Q_sack, components[i].Q_rack)

    def connectComponentsToGasStation(self, components: list):
        """
        Connects two components ([road segment 1, road segment 2]) in the list to a gas station.
        The theoretical order is road segment 1, gas station, road segment 2.
        :param components: The components to connect.
        """
        self.connectPorts(components[0].car_out, self.gas_station.car_in)

        self.connectPorts(self.gas_station.car_out, components[1].car_in)
        self.connectPorts(self.gas_station.Q_send, components[1].Q_recv)
        self.connectPorts(components[1].Q_sack, self.gas_station.Q_rack)
