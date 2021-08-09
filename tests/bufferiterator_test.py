import numpy as np
from concurrentbuffer.factory import BufferFactory
from concurrentbuffer.info import BufferInfo
from concurrentbuffer.iterator import BufferIterator
from concurrentbuffer.state import BufferState
from example.instructor import DataInstructor
from example.worker import DataWorker
import time

class TestBufferIterator:
    def test_buffer_iterator_fork(self):
        cpus = 6
        count = cpus * len(BufferState)
        buffer_shape = (12, 284, 284, 3)

        context = 'fork'
        deterministic=False

        instructor = DataInstructor()
        worker = DataWorker(data_shape=buffer_shape)
        buffer_info = BufferInfo(count=count, shape=buffer_shape)

        buffer_factory = BufferFactory(
            cpus=cpus,
            buffer_info=buffer_info,
            instructor=instructor,
            worker=worker,
            context=context,
            deterministic=deterministic,
        )

        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for _ in range(10):
                _ = next(data_buffer_iterator)

    def test_buffer_iterator_spawn(self):
        cpus = 6
        count = cpus * len(BufferState)
        buffer_shape = (12, 284, 284, 3)

        context = 'spawn'
        deterministic=False

        instructor = DataInstructor()
        worker = DataWorker(data_shape=buffer_shape)
        buffer_info = BufferInfo(count=count, shape=buffer_shape)

        buffer_factory = BufferFactory(
            cpus=cpus,
            buffer_info=buffer_info,
            instructor=instructor,
            worker=worker,
            context=context,
            deterministic=deterministic,
        )

        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for _ in range(10):
                _ = next(data_buffer_iterator)



    def test_buffer_iterator_deterministic_fork(self):
        cpus = 6
        count = cpus * len(BufferState)
        buffer_shape = (12, 284, 284, 3)

        context = 'fork'
        deterministic=True

        instructor = DataInstructor()
        worker = DataWorker(data_shape=buffer_shape)
        buffer_info = BufferInfo(count=count, shape=buffer_shape)

        buffer_factory = BufferFactory(
            cpus=cpus,
            buffer_info=buffer_info,
            instructor=instructor,
            worker=worker,
            context=context,
            deterministic=deterministic,
        )


        times = [1, 5, 1, 4, 1, 1, 2, 4, 2, 4]
        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for index in range(10):
                data = next(data_buffer_iterator)
                assert np.all(data == times[index])


    def test_buffer_iterator_deterministic_spawn(self):
        cpus = 6
        count = cpus * len(BufferState)
        buffer_shape = (12, 284, 284, 3)

        context = 'spawn'
        deterministic=True

        instructor = DataInstructor()
        worker = DataWorker(data_shape=buffer_shape)
        buffer_info = BufferInfo(count=count, shape=buffer_shape)

        buffer_factory = BufferFactory(
            cpus=cpus,
            buffer_info=buffer_info,
            instructor=instructor,
            worker=worker,
            context=context,
            deterministic=deterministic,
        )


        times = [1, 5, 1, 4, 1, 1, 2, 4, 2, 4]
        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for index in range(10):
                data = next(data_buffer_iterator)
                assert np.all(data == times[index])
