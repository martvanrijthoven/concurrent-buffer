from enum import Enum
from functools import wraps
from multiprocessing import Lock
from multiprocessing.shared_memory import SharedMemory

import numpy as np


class BufferState(Enum):
    """States for the shared buffer memory"""

    FREE = 1
    AVAILABLE = 2
    RESERVED = 3
    PROCESSING = 4


def _lock_state_buffer(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self.lock.acquire()
        out = method(self, *args, **kwargs)
        self.lock.release()
        return out

    return wrapper


class BufferStateMemory:
    """Class that contains the states of buffers"""

    def __init__(self, count: int, dtype: type, lock: Lock, buffer: SharedMemory):
        """Init

        Args:
            count (int): count of buffers
            dtype (type): type of buffers
            buffer (SharedMemory): buffer that contains states
        """

        self._count = count
        self._dtype = dtype
        self._buffer = buffer
        self._lock = lock

        for buffer_id in range(self._count):
            self.update_buffer_id_to_free(buffer_id=buffer_id)

    @property
    def lock(self):
        return self._lock

    def get_state_buffer(self):
        return np.ndarray(
            shape=self._count,
            dtype=self._dtype,
            buffer=self._buffer.buf,
        )

    def _get_buffer_ids_with_state(self, state: BufferState):
        state_buffer = self.get_state_buffer()
        return list(np.where(state_buffer == state.value)[0])

    @_lock_state_buffer
    def _get_buffer_id_with_state(self, state: BufferState, update_state: BufferState):
        buffer_ids = self._get_buffer_ids_with_state(state=state)
        if len(buffer_ids) == 0:
            return None
        self._update_state_buffer(buffer_id=buffer_ids[0], buffer_state=update_state)
        return buffer_ids[0]

    @_lock_state_buffer
    def _from_id_get_buffer_id_with_state(
        self, buffer_id: int, state: BufferState, update_state: BufferState
    ):
        buffer_ids = self._get_buffer_ids_with_state(state)
        if len(buffer_ids) == 0 or buffer_id not in buffer_ids:
            return None
        self._update_state_buffer(buffer_id=buffer_id, buffer_state=update_state)
        return buffer_id

    def _update_state_buffer(self, buffer_id: int, buffer_state: BufferState):
        state_buffer = self.get_state_buffer()
        state_buffer[buffer_id] = buffer_state.value

    def get_free_buffer_id(self):
        return self._get_buffer_id_with_state(
            state=BufferState.FREE, update_state=BufferState.RESERVED
        )

    def get_available_buffer_id(self):
        return self._get_buffer_id_with_state(
            state=BufferState.AVAILABLE, update_state=BufferState.PROCESSING
        )

    def get_available_buffer_id_from_id(self, buffer_id):
        return self._from_id_get_buffer_id_with_state(
            buffer_id=buffer_id,
            state=BufferState.AVAILABLE,
            update_state=BufferState.PROCESSING,
        )

    def update_buffer_id_to_free(self, buffer_id):
        self._update_state_buffer(buffer_id=buffer_id, buffer_state=BufferState.FREE)

    def update_buffer_id_to_available(self, buffer_id):
        self._update_state_buffer(
            buffer_id=buffer_id, buffer_state=BufferState.AVAILABLE
        )
