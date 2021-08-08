import numpy as np
from concurrentbuffer.info import BufferInfo
from concurrentbuffer.iterator import BufferIterator
from concurrentbuffer.state import BufferState
from concurrentbufferexample.factory import DataBufferFactory


class TestBufferIterator:
    def test_buffer_iterator(self):
        cpus = 6
        count = cpus * len(BufferState)
        buffer_shape = (12, 284, 284, 3)
        buffer_info = BufferInfo(count=count, shape=buffer_shape)

        buffer_factory = DataBufferFactory(
            cpus=cpus, buffer_info=buffer_info, deterministic=False
        )

        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for _ in range(10):
                _ = next(data_buffer_iterator)

    def test_buffer_iterator_deterministic(self):
        cpus = 6
        count = cpus * len(BufferState)
        buffer_shape = (12, 284, 284, 3)
        buffer_info = BufferInfo(count=count, shape=buffer_shape)

        buffer_factory = DataBufferFactory(
            cpus=cpus, buffer_info=buffer_info, deterministic=False
        )
        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for _ in range(10):
                data = next(data_buffer_iterator)

        buffer_factory = DataBufferFactory(
            cpus=cpus, buffer_info=buffer_info, deterministic=True
        )
        times = [1, 5, 1, 4, 1, 1, 2, 4, 2, 4]
        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for index in range(10):
                data = next(data_buffer_iterator)
                assert np.all(data == times[index])
