import sys
from multiprocessing.context import BaseContext, SpawnContext

try:
    from pytest_cov.embed import cleanup_on_sigterm
except ImportError:
    pass
else:
    cleanup_on_sigterm()
WINDOWS = sys.platform == "win32"

if not WINDOWS:
    from multiprocessing.context import ForkContext

import numpy as np
from concurrentbuffer.factory import create_buffer_factory
from concurrentbuffer.info import BufferInfo
from concurrentbuffer.iterator import BufferIterator, buffer_iterator_factory
from concurrentbuffer.state import BufferState
from concurrentbuffer.system import BufferSystem
from example.commander import DataCommander
from example.producer import DataProducer

CPUS = 6
BUFFER_SHAPES = ((12, 284, 284, 3), (12, 284, 284))
TIMES = [[1, 5, 1, 4, 1, 1, 2, 4, 2, 4], [2, 6, 2, 5, 2, 2, 3, 5, 3, 5]]


class TestBufferIterator:
    """This class contains methods to test the buffer iterator"""

    def _iterating(
        self,
        context: BaseContext = SpawnContext(),
        deterministic: bool = True,
    ):
        commander = DataCommander(times=TIMES)
        producer = DataProducer(data_shapes=BUFFER_SHAPES)
        buffer_factory = create_buffer_factory(
            cpus=CPUS * len(BufferState),
            batch_commander=commander,
            batch_producer=producer,
            context=context,
            deterministic=deterministic,
            buffer_shapes=BUFFER_SHAPES,
            buffer_dtype=np.uint8,
        )

        with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
            for index in range(10):
                data = next(data_buffer_iterator)
                if deterministic:
                    assert np.all(data[0] == TIMES[0][index])
                    assert np.all(data[1] == TIMES[1][index])

    if not WINDOWS:

        def test_buffer_iterator_fork(self):
            context = ForkContext()
            deterministic = False
            self._iterating(
                context=context,
                deterministic=deterministic,
            )
        
        def test_buffer_iterator_fork_str(self):
            context = "fork"
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

    def test_buffer_iterator_spawn(self):
        context = SpawnContext()
        deterministic = False
        self._iterating(
            context=context,
            deterministic=deterministic,
        )

    def test_buffer_iterator_spawn_str(self):
        context = "spawn"
        deterministic = False
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

    def test_iterator_factory(self):
        commander = DataCommander(times=TIMES)
        producer = DataProducer(data_shapes=BUFFER_SHAPES)
        deterministic = True
        buffer_iterator = buffer_iterator_factory(
            cpus=CPUS,
            buffer_shapes=BUFFER_SHAPES,
            commander=commander,
            producer=producer,
            context="spawn",
            deterministic=deterministic,
        )

        for index in range(10):
            data = next(buffer_iterator)
            if deterministic:
                assert np.all(data[0] == TIMES[0][index])
                assert np.all(data[1] == TIMES[1][index])
