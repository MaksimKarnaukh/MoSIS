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

    road_segment_length = 5
    v_max = 30

    def __init__(self, name):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(RoadStretch, self).__init__(name)

        # create the generator
        self.generator = self.addSubModel(Generator("gen"))
        # create the fork
        self.fork = self.addSubModel(Fork("fork", self.road_segment_length, self.v_max))
        # create the collector
        self.collector = self.addSubModel(Collector("collector"))
        # create the side marker
        self.side_marker = self.addSubModel(SideMarker("side_marker"))
        # create the gas station
        self.gas_station = self.addSubModel(GasStation("gas_station"))

        # create the first road segment
        self.road_segment_1 = self.addSubModel(RoadSegment("road_segment_1", self.road_segment_length, self.v_max))




