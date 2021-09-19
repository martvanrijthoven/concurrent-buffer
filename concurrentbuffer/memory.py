from multiprocessing.shared_memory import SharedMemory
from typing import Dict

import numpy as np


class BufferMemory:
    """Class that contains the buffers
    """
    def __init__(self, shape: tuple, dtype: type, buffers: Dict[int, SharedMemory]):
        """INit

        Args:
            shape (tuple): shape of the buffers
            dtype (type): type of the buffers
            buffers (List[SharedMemory]): the data memory of the buffers
        """

        self._shape = shape
        self._dtype = dtype
        self._buffers = buffers

    def get_buffer(self, buffer_id: int):
        return np.ndarray(
            shape=self._shape,
            dtype=self._dtype,
            buffer=self._buffers[buffer_id].buf,
        ).copy()

    def update_buffer(self, buffer_id: int, data: np.ndarray):
        buffer = np.ndarray(
            shape=self._shape,
            dtype=self._dtype,
            buffer=self._buffers[buffer_id].buf,
        )
        buffer[:] = data[:]
