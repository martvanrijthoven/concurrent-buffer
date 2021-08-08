from collections.abc import Iterator

from concurrentbuffer.factory import BufferFactory
import numpy as np

class BufferIterator(Iterator):
    """Iterator that goes through the buffers indefinetly
    """

    def __init__(
        self,
        buffer_factory: BufferFactory,
        auto_free_buffer: bool = True,
    ):
        """Init

        Args:
            buffer_factory (BufferFactory): factory in which all the components have been created
            auto_free (bool, optional): frees the previous buffer when new data is requested. Defaults to True.
        """
    
        self._factory = buffer_factory
        self._auto_free_buffer = auto_free_buffer
        self._last_buffer_id = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __next__(self) -> np.ndarray:
        if self._auto_free_buffer and self._last_buffer_id is not None:
            self._factory.buffer_state_memory.update_buffer_id_to_free(
                buffer_id=self._last_buffer_id
            )

        if self._factory.deterministic:
            buffer_id = self._next_deterministic()
        else:
            buffer_id = self._next()

        self._last_buffer_id = buffer_id
        return self._factory.buffer_memory.get_buffer(buffer_id=buffer_id)

    def _next_deterministic(self) -> int:
        next_buffer_id = self._factory.receiver.recv()
        while True:
            buffer_id = (
                self._factory.buffer_state_memory.get_available_buffer_id_from_id(
                    buffer_id=next_buffer_id
                )
            )
            if buffer_id is None:
                continue
            return buffer_id

    def _next(self) -> int:
        while True:
            buffer_id = self._factory.buffer_state_memory.get_available_buffer_id()
            if buffer_id is None:
                continue
            return buffer_id

    def stop(self):
        self._factory.stop()
