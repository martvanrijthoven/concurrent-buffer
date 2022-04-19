import sys
WINDOWS = sys.platform == "win32"

if not WINDOWS:
    from multiprocessing.context import ForkServerContext


from multiprocessing.context import ForkServerContext

from concurrentbuffer.commander import get_commander_process_class_object
from concurrentbuffer.info import BufferInfo
from concurrentbuffer.manager import (SharedBufferManager,
                                      SharedBufferManagerNotStarted)
from concurrentbuffer.producer import get_producer_process_class_object
from concurrentbuffer.state import BufferState
from pytest import raises


class TestErrors:
    """This class contains methods to test errors"""

    def test_buffers_error(self):

        with raises(SharedBufferManagerNotStarted):
            cpus = 6
            count = cpus * len(BufferState)
            buffer_shapes = ((12, 284, 284, 3), (12, 284, 284))
            buffer_info = BufferInfo(count=count, shapes=buffer_shapes)
            shared_buffer_manager = SharedBufferManager(buffer_info=buffer_info)
            _ = shared_buffer_manager.buffers

    def test_buffer_state_error(self):

        with raises(SharedBufferManagerNotStarted):
            cpus = 6
            count = cpus * len(BufferState)
            buffer_shapes = ((12, 284, 284, 3), (12, 284, 284))
            buffer_info = BufferInfo(count=count, shapes=buffer_shapes)
            shared_buffer_manager = SharedBufferManager(buffer_info=buffer_info)
            _ = shared_buffer_manager.state_buffer

    if not WINDOWS:
        def test_get_commander_process_class_object(self):
            with raises(ValueError):
                get_commander_process_class_object(ForkServerContext)

        def test_get_producer_process_class_object(self):
            with raises(ValueError):
                get_producer_process_class_object(ForkServerContext)
