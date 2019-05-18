class NoSeatException(Exception):
    def __init__(self):
        super().__init__('Chair has no seat! You cannot add any feet or backrest!')


class NoFeetException(Exception):
    def __init__(self):
        super().__init__('Chair has no feet! You cannot add any stabilizer bar!')


class CannotBePackedException(Exception):
    def __init__(self):
        super().__init__('Chair is not ready to be packed!')


class BufferFullException(Exception):
    def __init__(self):
        super().__init__('Requested buffer is full!')


class BufferEmptyException(Exception):
    def __init__(self):
        super().__init__('Requested buffer is empty!')
