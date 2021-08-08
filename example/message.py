from concurrentbuffer.message import MessageProcess


"""
Example Message Process
"""


class DataMessageProcess(MessageProcess):
    def run(self):
        self._index = 0
        self._times = [1, 5, 1, 4, 1, 1, 2, 4, 2, 4]
        super().run()

    def create_message(self):
        message = {"value": self._times[self._index], "time": self._times[self._index]}
        self._index = (self._index + 1) % len(self._times)
        return message