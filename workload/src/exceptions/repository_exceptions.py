from src.exceptions.base_exception import MyException


class UniqueConstraintViolationException(MyException):
    def __init__(self, message: str):
        super().__init__(message)


class NotNullConstraintViolationException(MyException):
    def __init__(self, message: str):
        super().__init__(message)
