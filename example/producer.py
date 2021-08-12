import time

import numpy as np
from concurrentbuffer.producer import Producer


class DataProducer(Producer):
    def __init__(self, data_shape):
        self._data_shape = data_shape

    def create_data(self, message):
        time.sleep(message["time"])
        return np.ones(self._data_shape) * message["value"]
