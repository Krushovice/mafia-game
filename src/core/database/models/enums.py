import enum


class CharacterRole(str, enum.Enum):
    THUG = "thug"
    HACKER = "hacker"
    NEGOTIATOR = "negotiator"
    CAPO = "capo"  # универсальный боец, стартовый персонаж


class CharacterTrait(str, enum.Enum):
    HOT = "hot"
    QUIET = "quiet"
    GREEDY = "greedy"


class MissionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_EVENT = "waiting_event"  # миссия ждёт выбора игрока по событию
    SUCCESS = "success"
    COMPLETED = "completed"
    FAILED = "failed"


class EventChoiceType(str, enum.Enum):
    """Типы выбора игрока при событии."""

    PAYOFF = "payoff"  # откупиться деньгами
    FIGHT = "fight"  # бой (зависит от оружия и силы)
    TALK = "talk"  # заговорить зубы (зависит от влияния)
    DO_NOTHING = "do_nothing"  # бездействие (провал/штраф)


class MissionEventType(str, enum.Enum):
    POLICE_RAID = "police_raid"
    COMPETITOR_ATTACK = "competitor_attack"
    RANDOM_LUCK = "random_luck"


class MissionDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MissionStatType(str, enum.Enum):
    """Главный стат миссии — от него зависит награда."""

    FORCE = "force"  # сила + оружие
    STEALTH = "stealth"  # ловкость + инструменты
    DIPLOMACY = "diplomacy"  # интеллект


class MissionType(str, enum.Enum):
    """Тип миссии."""

    REGULAR = "regular"  # обычная, без таймера
    FLASH = "flash"  # всплывающая, ограничена по времени
    TERRITORY = "territory"  # захват территории (3 слота, hard)
    RETURN = "return"  # возвратная миссия после отсутствия


class TerritoryType(str, enum.Enum):
    """Тип территории."""

    DISTRICT = "district"
    NEIGHBORHOOD = "neighborhood"
    BOROUGH = "borough"
