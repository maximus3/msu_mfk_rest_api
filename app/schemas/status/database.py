from enum import Enum, unique


@unique
class DatabaseStatus(str, Enum):
    OK = 'OK'
    ALREADY_EXISTS = 'ALREADY_EXISTS'
    NOT_FOUND = 'NOT_FOUND'
    ERROR = 'ERROR'
    MANY_TG_ACCOUNTS_ERROR = 'MANY_TG_ACCOUNTS_ERROR'
