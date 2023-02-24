import enum


class LevelOkMethod(str, enum.Enum):
    CONTESTS_OK = 'contests_ok'
    SCORE_SUM = 'score_sum'


class LevelCountMethod(str, enum.Enum):
    ABSOLUTE = 'absolute'
    PERCENT = 'percent'
