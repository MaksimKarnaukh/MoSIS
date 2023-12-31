from typing import List, Union

from pypdevs.DEVS import CoupledDEVS

from components.fork import Fork
from components.generator import Generator
from components.roadsegment import RoadSegment


class RoadCoupledDEVS(CoupledDEVS):
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

    def connectForkOutput(self, fork: Fork, component, fork_output_port):
        """
        connects the output of the fork to the component.
        :param fork: the fork
        :param component: the component to connect to
        :param fork_output_port: the fork output port to connect to
        """
        self.connectPorts(fork_output_port, component.car_in)
        self.connectPorts(component.Q_send, fork.Q_recv)
        self.connectPorts(fork.Q_sack, component.Q_rack)
