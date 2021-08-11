from concurrentbuffer.commander import Commander


"""
Example Message Process
"""

class DataCommander(Commander):
    def __init__(self, times):
        self._index = 0
        self._times = times


    def create_message(self):
        message = {"value": self._times[self._index], "time": self._times[self._index]}
        self._index = (self._index + 1) % len(self._times)
        return message