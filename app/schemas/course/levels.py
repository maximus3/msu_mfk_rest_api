import enum


class LevelOkMethod(enum.Enum):
    CONTESTS_OK = 'contests_ok'
    SCORE_SUM = 'score_sum'


class LevelCountMethod(enum.Enum):
    ABSOLUTE = 'absolute'
    PERCENT = 'percent'
