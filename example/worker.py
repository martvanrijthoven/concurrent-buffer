import time

import numpy as np
from concurrentbuffer.worker import Worker

"""
Example Worker Process
"""


class DataWorker(Worker):
    def __init__(self, data_shape):
        self._data_shape = data_shape

    def create_data(self, message):
        time.sleep(message["time"])
        return np.ones(self._data_shape) * message["value"]
