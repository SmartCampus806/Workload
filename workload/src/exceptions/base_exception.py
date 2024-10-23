class MyException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)

    def get_msg(self) -> str:
        return self.msg
