"""
This package contains the State Event Location logic and
helper classes.
"""

from enum import Enum

class Direction(Enum):
	"""
	Specifies the direction of the level crossing to check.
	"""

	ANY = 0
	"""Any crossing through the level requires an event."""

	FROM_BELOW = 1
	"""Only a crossing from below through the level causes an event."""

	FROM_ABOVE = 2
	"""Only a crossing from above through the level causes an event."""


class StateEvent:
	"""
	Data class that holds all generic state event information.

	Args:
		output_name (str):      The name of the output port to check.
		level (float):          The value that the signal must pass through.
								Defaults to 0.
		direction (Direction):  The direction of the crossing.
								Defaults to :attr:`Direction.ANY`.
		event (callable):       A function that must be executed if the event
								occurs. It takes three arguments: event, time and
								model.
								In this function, it is allowed to alter any
								and all attributes/properties/components of the
								model. Defaults to a no-op.
	"""
	def __init__(self, output_name, level=0.0, direction=Direction.ANY, event=lambda t, m: None):
		self.output_name = output_name
		self.level = level
		self.direction = direction
		self.event = event
		self.fired = False
