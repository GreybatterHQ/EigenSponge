from enum import Enum

class ErrorCodes(Enum):
    INVALID_REQUEST = '1000'
    AUTHENTICATION_FAILED = '1001'
    DATA_NOT_FOUND = '1002',
    GENERIC_SERVER_ERROR = '1003'