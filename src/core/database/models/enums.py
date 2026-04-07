import enum


class CharacterRole(str, enum.Enum):
    THUG = "thug"
    HACKER = "hacker"
    NEGOTIATOR = "negotiator"


class CharacterTrait(str, enum.Enum):
    HOT = "hot"
    QUIET = "quiet"
    GREEDY = "greedy"


class MissionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"