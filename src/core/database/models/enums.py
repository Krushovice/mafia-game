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
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    COMPLETED = "completed"
    FAILED = "failed"

class MissionEventType(str, enum.Enum):
    POLICE_RAID = "police_raid"
    COMPETITOR_ATTACK = "competitor_attack"
    RANDOM_LUCK = "random_luck"

class MissionDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"