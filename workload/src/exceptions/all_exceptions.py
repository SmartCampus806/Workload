from src.exceptions import MyException


class GroupNotFound(MyException):
    def __init__(self, message: str):
        super().__init__(message)
