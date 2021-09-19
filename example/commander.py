from concurrentbuffer.commander import Commander


class DataCommander(Commander):
    """Custom Commander class for testing purposes"""

    def __init__(self, times):
        self._index = 0
        self._times = times

    def create_message(self):
        message = {"values": (self._times[0][self._index], self._times[1][self._index])}
        self._index = (self._index + 1) % len(self._times[0])
        return message
        