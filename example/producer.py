import time

import numpy as np
from concurrentbuffer.producer import Producer


class DataProducer(Producer):
    """Custom Producer class for testing purposes"""

    def __init__(self, data_shapes):
        self._data_shapes = data_shapes

    def create_data(self, message):
        time.sleep(message["values"][0])
        return (
            np.ones(self._data_shapes[0]) * message["values"][0],
            np.ones(self._data_shapes[1]) * message["values"][1],
        )
