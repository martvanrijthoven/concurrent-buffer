from multiprocessing.context import BaseContext, ForkContext, SpawnContext

import numpy as np
from concurrentbuffer.factory import BufferFactory
from concurrentbuffer.info import BufferInfo
from concurrentbuffer.iterator import BufferIterator
from concurrentbuffer.state import BufferState
from concurrentbuffer.system import BufferSystem
from example.instructor import DataInstructor
from example.producer import DataProducer

CPUS = 6
BUFFER_SHAPE = (12, 284, 284, 3)
TIMES = [1, 5, 1, 4, 1, 1, 2, 4, 2, 4]

class TestBufferIterator:
    def _iterating(
        self,
        context: BaseContext = SpawnContext(),
        deterministic: bool = True,
    ):

        count = CPUS * len(BufferState)
        buffer_system = BufferSystem(
            cpus=CPUS, context=context, deterministic=deterministic
        )
        buffer_info = BufferInfo(count=count, shape=BUFFER_SHAPE)

        instructor = DataInstructor(times=TIMES)
        worker = DataProducer(data_shape=BUFFER_SHAPE)

        buffer_factory = BufferFactory(
            buffer_system=buffer_system,
            buffer_info=buffer_info,
            instructor=instructor,
            worker=worker,
        )
        
        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for index in range(10):
                data = next(data_buffer_iterator)
                if deterministic:
                    assert np.all(data == TIMES[index])

    def test_buffer_iterator_fork(self):
        context = ForkContext()
        deterministic = False
        self._iterating(
            context=context,
            deterministic=deterministic,
        )

    def test_buffer_iterator_spawn(self):
        context = SpawnContext()
        deterministic = False
        self._iterating(
            context=context,
            deterministic=deterministic,
        )

    def test_buffer_iterator_deterministic_fork(self):
        context = ForkContext()
        deterministic = True
        self._iterating(
            context=context,
            deterministic=deterministic,
        )

    def test_buffer_iterator_deterministic_spawn(self):
        context = SpawnContext()
        deterministic = True
        self._iterating(
            context=context,
            deterministic=deterministic,
        )
