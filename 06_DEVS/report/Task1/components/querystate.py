from enum import Enum
class QueryState(Enum):
    """
    The state of the Query.
    """
    AVAILABLE = 1
    NOT_SENT = 2
    SENT = 3
    ACKNOWLEDGED = 4