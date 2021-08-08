import time

import numpy as np
from concurrentbuffer.worker import WorkerProcess

"""
Example Worker Process
"""


class DataWorkerProcess(WorkerProcess):
    def create_data(self, message):
        time.sleep(message["time"])
        return np.ones(self._buffer_shape) * message["value"]
