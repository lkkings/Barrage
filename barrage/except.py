class ParamsError(Exception):
    def __init__(self, message):
        super().__init__(message)


class BarrageError(Exception):
    def __init__(self, message):
        super().__init__(message)
