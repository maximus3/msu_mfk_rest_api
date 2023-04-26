import enum


class ContestTag(str, enum.Enum):
    NECESSARY = 'NECESSARY'
    FINAL = 'FINAL'
    EARLY_EXAM = 'EARLY_EXAM'
    USUAL = 'USUAL'
