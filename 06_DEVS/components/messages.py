"""
messages.py
containst the dataclasses for the events that model the Car and their queries
Made by:
    - Maksim Karnaukh
    - Sam Roggeman
"""

from dataclasses import dataclass, field




@dataclass
class Car:
    """
    This is an event traveling passed between RoadSegments.
    It is used to model a car.
    """
    # A unique identifier to uniquely distinguish between cars.
    ID: int
    # The preferred velocity of the car. This is the velocity the car tries to obtain whenever possible.
    v_pref: float
    # The maximal amount of acceleration possible for this Car on a single RoadSegment.
    dv_pos_max: float
    # The maximal amount of deceleration possible for this Car on a single RoadSegment.
    dv_neg_max: float
    # The (simulation) time at which the Car is created.
    departure_time: float = None
    # The total distance that the Car has traveled.
    # distance_traveled: float
    # The current velocity.
    # By default, it is initialized to be the same as v_pref, but may change during the simulation.
    distance_traveled: float = 0.0
    # This value is used for all the distance computations etc.
    v: float = None
    # Indicator that the Car needs gas.
    no_gas: bool = False
    # The target destination of the Car.
    # This will help for path planning etc in a more detailed library.
    # Later on in the assignment, this value will be used for CrossRoads.
    destination: str = None




@dataclass
class Query:
    """
    Represents the driver watching to the RoadSegment in front.
    """
    # The unique identifier of the Car that sends this Query.
    ID: int





@dataclass
class QueryAck:
    """
    Event that answers a Query.
    This is needed to actually obtain the information of the upcoming RoadSegment.
    The Query/QueryAck logic can therefore be seen as "polling".
    """
    # The unique identifier of the Car that queried this data.
    ID: int
    # An estimate for the time until the upcoming RoadSegment is available again.
    t_until_dep: float
    # Indicates which lane the current RoadSegment applies to.
    # If a Car wants to "change lanes" in a Fork, this value is used to identify which QueryAcks to take into account.
    lane: int = None
    # Indicator that this QueryAck does not correspond to the RoadSegment in front
    # but rather another one the Car needs to keep track of.
    # Defaults to false.
    # Allow for merges of RoadSegments.
    sideways: bool = False
