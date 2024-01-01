from typing import List, Union

from pypdevs.DEVS import CoupledDEVS

from components.collector import Collector
from components.fork import Fork
from components.gasstation import GasStation
from components.generator import Generator
from components.roadsegment import RoadSegment
from components.sidemarker import SideMarker
from other.RoadCoupledDEVS import RoadCoupledDEVS


class RoadStretch(RoadCoupledDEVS):
    """
    Create a single RoadStretch (a Coupled DEVS),
    that starts with a Generator, has a variable amount of RoadSegments, and ends in a Collector.
    In the middle of this RoadStretch, there should be a Fork, where the second output goes
    into the sequence of RoadSegment, GasStation, RoadSegment.
    Eventually, this final RoadSegment merges back into the RoadStretch.
    Don't forget the SideMarker! You may use as many layers of hierarchy as desired for a clean,
    easily understandable solution.
    """

    def __init__(self, name, L, v_max, IAT_min, IAT_max, v_pref_mu, v_pref_sigma, destinations, limit):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(RoadStretch, self).__init__(name)
        self.limit = limit

        # create the generator
        self.generator = self.addSubModel(
            Generator(name="gen",
                      IAT_min=IAT_min, IAT_max=IAT_max,
                      v_pref_mu=v_pref_mu, v_pref_sigma=v_pref_sigma,
                      destinations=destinations, limit=limit, v_max=v_max))

        # create the fork<
        self.fork = self.addSubModel(Fork(name="fork", L=L, v_max=v_max))

        # create the collector
        self.collector = self.addSubModel(Collector("collector"))

        # create the side marker
        self.side_marker = self.addSubModel(SideMarker("side_marker"))

        # create the gas station
        self.gas_station = self.addSubModel(GasStation("gas_station"))

        # create the 7 road segments

        # first road segment connected to the generator
        self.road_segment_gen = self.addSubModel(RoadSegment("road_segment_gen", L, v_max))

        # to the right of fork, north from left to right
        self.road_segment_n1 = self.addSubModel(RoadSegment("road_segment_n1", L, v_max))
        self.road_segment_n2 = self.addSubModel(RoadSegment("road_segment_n2", L, v_max))
        self.road_segment_n3 = self.addSubModel(RoadSegment("road_segment_n3", L, v_max, priority=True))
        self.road_segment_n4 = self.addSubModel(RoadSegment("road_segment_n4", L, v_max))

        # to the left of fork, south from left to right
        self.road_segment_s1 = self.addSubModel(RoadSegment("road_segment_s1", L, v_max))
        self.road_segment_s2 = self.addSubModel(RoadSegment("road_segment_s2", L, v_max))

        # put the road segments in a list
        self.road_segments = [
            self.road_segment_gen,
            self.road_segment_n1,
            self.road_segment_n2,
            self.road_segment_n3,
            self.road_segment_n4,
            self.road_segment_s1,
            self.road_segment_s2,
            self.fork
        ]

        # connect all components on the northern line
        self.connectComponents([
            self.generator,
            self.road_segment_gen,
            self.fork,
            self.road_segment_n1,
            self.road_segment_n2,
            self.road_segment_n3,
            self.road_segment_n4,
        ])

        # connect the n4 road segment to the collector
        self.connectPorts(self.road_segment_n4.car_out, self.collector.car_in)

        # connect the second fork - car output of the fork to road segment s1
        self.connectForkOutput(
            self.fork,
            self.road_segment_s1,
            self.fork.car_out2,
        )

        # connect all components of the southern side
        self.connectComponentsToGasStation([
            self.road_segment_s1,
            self.gas_station,
            self.road_segment_s2
        ])

        # connect road segment s2 to road segment n4
        self.connectComponents([
            self.road_segment_s2,
            self.road_segment_n4
        ])

        # connect the side marker to road segment n3 and s2
        self.connectPorts(self.road_segment_n3.Q_sack, self.side_marker.mi)
        self.connectPorts(self.side_marker.mo, self.road_segment_s2.Q_rack)

    def getCollector(self):
        return self.collector

    def getNumberCrashes(self):
        collisions = 0
        for component in self.road_segments:
            collisions += component.state.collisions
        return collisions

