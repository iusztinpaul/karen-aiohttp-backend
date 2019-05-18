from common.exceptions import NoSeatException, NoFeetException, CannotBePackedException


class Chair:
    SEAT = 0
    FEET = 1
    BACKREST = 2
    STABILIZE_BAR = 3
    PACKED = 4

    def __init__(self):
        self._states = [False, False, False, False, False]

    def has_seat(self):
        return self._states[self.SEAT]

    def has_feet(self):
        return self._states[self.FEET]

    def has_backrest(self):
        return self._states[self.BACKREST]

    def has_stabilizer_bar(self):
        return self._states[self.STABILIZE_BAR]

    def is_packet(self):
        return self._states[self.PACKED]

    @property
    def is_in_progress(self):
        return not self.is_ready

    @property
    def is_ready(self):
        return all(self._states)

    def __str__(self):
        status = 'NOT ready' if self.is_in_progress else 'READY'
        return f'Chair is ' + status + ' ----- In the following state ' + str(self._states)

    def build_seat(self):
        self._states[self.SEAT] = True

    def build_feet(self):
        if not self.has_seat:
            raise NoSeatException()

        self._states[self.FEET] = True

    def build_backrest(self):
        if not self.has_seat:
            raise NoSeatException()

        self._states[self.BACKREST] = True

    def build_stabilizer_bar(self):
        if not self.has_feet:
            raise NoFeetException()

        self._states[self.STABILIZE_BAR] = True

    def pack(self):
        if not self.has_stabilizer_bar or not self.has_backrest:
            raise CannotBePackedException()

        self._states[self.PACKED] = True
