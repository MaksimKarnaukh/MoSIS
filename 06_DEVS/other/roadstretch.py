from typing import List, Union

from pypdevs.DEVS import CoupledDEVS

from components.collector import Collector
from components.fork import Fork
from components.gasstation import GasStation
from components.generator import Generator
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

    # constants for the road stretch

    L = 5  # length of the road segment
    v_max = 30  # maximum allowed velocity

    IAT_min = 5
    IAT_max = 7
    v_pref_mu = 30
    v_pref_sigma = 10
    destinations = ["collector"]
    limit = 50

    def __init__(self, name):
        """
        :param name:
            The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(RoadStretch, self).__init__(name)

        # create the generator
        self.generator = self.addSubModel(
            Generator(name="gen",
                      IAT_min=self.IAT_min, IAT_max=self.IAT_max,
                      v_pref_mu=self.v_pref_mu, v_pref_sigma=self.v_pref_sigma,
                      destinations=self.destinations, limit=self.limit))

        # create the fork<
        self.fork = self.addSubModel(Fork(name="fork", L=self.L, v_max=self.v_max))

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

    def connectComponents(self, components: List[Union[RoadSegment, Fork, Generator]]):
        """
        Connects all components in the list to each other in the order they are given.
        The order matters, as the first component is connected to the second, the second to the third, etc.

        :param components: The components of type RoadSegment, Fork, Generator,
            to connect. Generator and Collector can only be at the start and end respectively.
            Fork will only connect the first car output to the next component.

        """
        for i in range(len(components) - 1):
            self.connectPorts(components[i].car_out, components[i + 1].car_in)
            self.connectPorts(components[i].Q_send, components[i + 1].Q_recv)
            self.connectPorts(components[i + 1].Q_sack, components[i].Q_rack)

    def connectComponentsToGasStation(self, components: list):
        """
        Connects two components of type (RoadSegment, Fork, Generator, Collector) to the gas station.
        The order is component 1, gas station, component 2.
        :param components: The components to connect in order. [ Component 1, GasStation Component , Component 2 ]
        """

        self.connectPorts(components[0].car_out, components[1].car_in)

        self.connectPorts(components[1].car_out, components[2].car_in)
        self.connectPorts(components[1].Q_send, components[2].Q_recv)
        self.connectPorts(components[2].Q_sack, components[1].Q_rack)

    def connectForkOutput(self, fork:Fork, component ,fork_output_port):
        """
        connects the output of the fork to the component.
        :param fork: the fork
        :param component: the component to connect to
        :param fork_output_port: the fork output port to connect to
        """
        self.connectPorts(fork_output_port, component.car_in)
        self.connectPorts(component.Q_send, fork.Q_recv)
        self.connectPorts(fork.Q_sack, component.Q_rack)

    def getCollector(self):
        return self.collector

    def getNumberCrashes(self):
        collisions = 0
        for component in self.road_segments:
            collisions += component.state.collisions
        return collisions

