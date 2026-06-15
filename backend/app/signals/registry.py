from enum import Enum

class SignalType(str, Enum):
    """High-level categories for intelligence signals."""
    HIRING = "HIRING"
    EXECUTIVE = "EXECUTIVE"
    FUNDING = "FUNDING"
    GITHUB = "GITHUB"
    LAUNCH = "LAUNCH"
    PARTNERSHIP = "PARTNERSHIP"
    NEWS = "NEWS"
    SOCIAL = "SOCIAL"
