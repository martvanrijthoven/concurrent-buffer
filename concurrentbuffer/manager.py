from multiprocessing.context import ProcessError
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import managers
from typing import List

import numpy as np

from concurrentbuffer.info import BufferInfo


class SharedBufferManagerNotStarted(ProcessError):
    """ Raised when shared buffer manager is not started. """

    ...


class SharedBufferManager(SharedMemoryManager):
    """Controls the creation, access and deletion of shared memory buffers.
    """

    def __init__(self, buffer_info: BufferInfo, *args, **kwargs):
        """Init

        Args:
            buffer_info (BufferInfo): contains information about the count, shape and type of the buffers
        """

        super().__init__(*args, **kwargs)

        self._buffer_info = buffer_info
        self._state_buffer = None
        self._buffers = None

    def start(self):
        super().start()
        self._create_state_buffer()
        self._create_buffers()

    def _create_state_buffer(self):
        size_holder = np.empty((self._buffer_info.count), dtype=np.dtype("uint8"))
        self._state_buffer = [self.SharedMemory(size=size_holder.nbytes)]

    def _create_buffers(self):
        self._buffers = []
        for idx in range(len(self._buffer_info)):
            self._buffers.append({})
            size_holder = np.empty((self._buffer_info.shapes[idx]), dtype=self._buffer_info.dtype)
            for buffer_id in range(self._buffer_info.count):
                self._buffers[idx][buffer_id] = self.SharedMemory(size=size_holder.nbytes)

    @property
    def state_buffer(self) -> SharedMemory:
        if self._state.value != managers.State.STARTED:
            raise SharedBufferManagerNotStarted()
        return self._state_buffer[0]

    @property
    def buffers(self) -> List[SharedMemory]:
        if self._state.value != managers.State.STARTED:
            raise SharedBufferManagerNotStarted()
        return self._buffers
