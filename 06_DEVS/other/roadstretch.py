from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY
import random

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



