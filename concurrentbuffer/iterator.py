import multiprocessing
from collections.abc import Iterator

import numpy as np

from concurrentbuffer.commander import Commander
from concurrentbuffer.factory import BufferFactory
from concurrentbuffer.info import BufferInfo
from concurrentbuffer.producer import Producer
from concurrentbuffer.state import BufferState
from concurrentbuffer.system import BufferSystem


class BufferIterator(Iterator):
    """Iterator that goes through the buffers indefinetly"""

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

        self._buffer_factory = buffer_factory
        self._auto_free_buffer = auto_free_buffer
        self._last_buffer_id = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __next__(self) -> np.ndarray:
        if self._auto_free_buffer and self._last_buffer_id is not None:
            self._buffer_factory.buffer_state_memory.update_buffer_id_to_free(
                buffer_id=self._last_buffer_id
            )

        if self._buffer_factory.buffer_system.deterministic:
            buffer_id = self._next_deterministic()
        else:
            buffer_id = self._next()

        self._last_buffer_id = buffer_id
        
        data = []
        for buffer_memory in self._buffer_factory.buffer_memories:
            data.append(buffer_memory.get_buffer(buffer_id=buffer_id))
        return data

    def _next_deterministic(self) -> int:
        next_buffer_id = self._buffer_factory.receiver.recv()
        while True:
            buffer_id = self._buffer_factory.buffer_state_memory.get_available_buffer_id_from_id(
                buffer_id=next_buffer_id
            )
            if buffer_id is None:
                continue
            return buffer_id

    def _next(self) -> int:
        while True:
            buffer_id = (
                self._buffer_factory.buffer_state_memory.get_available_buffer_id()
            )
            if buffer_id is None:
                continue
            return buffer_id

    def stop(self):
        self._buffer_factory.shutdown()


def buffer_iterator_factory(
    cpus: int,
    buffer_shapes: tuple,
    commander: Commander,
    producer: Producer,
    context: str,
    deterministic: bool,
    buffer_dtype: type = np.uint16,
    buffer_iterator_class: type = BufferIterator,
    *args,
    **kwargs
):
    count = cpus * len(BufferState)

    mp_context = multiprocessing.get_context(context)
    buffer_system = BufferSystem(
        cpus=cpus, context=mp_context, deterministic=deterministic
    )

    buffer_info = BufferInfo(count=count, shapes=buffer_shapes, dtype=buffer_dtype)

    buffer_factory = BufferFactory(
        buffer_system=buffer_system,
        buffer_info=buffer_info,
        commander=commander,
        producer=producer,
    )

    return buffer_iterator_class(buffer_factory=buffer_factory, *args, **kwargs)
