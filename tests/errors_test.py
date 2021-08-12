from concurrentbuffer.info import BufferInfo
from concurrentbuffer.manager import SharedBufferManager, SharedBufferManagerNotStarted
from concurrentbuffer.state import BufferState
from concurrentbuffer.commander import get_commander_process_class_object
from concurrentbuffer.producer import get_producer_process_class_object
from multiprocessing.context import ForkServerContext
from pytest import raises


class TestErrors:
    def test_buffers_error(self):

        with raises(SharedBufferManagerNotStarted):
            cpus = 6
            count = cpus * len(BufferState)
            buffer_shape = (12, 284, 284, 3)
            buffer_info = BufferInfo(count=count, shape=buffer_shape)
            shared_buffer_manager = SharedBufferManager(buffer_info=buffer_info)
            _ = shared_buffer_manager.buffers

    def test_buffer_state_error(self):

        with raises(SharedBufferManagerNotStarted):
            cpus = 6
            count = cpus * len(BufferState)
            buffer_shape = (12, 284, 284, 3)
            buffer_info = BufferInfo(count=count, shape=buffer_shape)
            shared_buffer_manager = SharedBufferManager(buffer_info=buffer_info)
            _ = shared_buffer_manager.state_buffer


    def test_get_commander_process_class_object(self):
        with raises(ValueError):
            get_commander_process_class_object(ForkServerContext)

    def test_get_producer_process_class_object(self):
        with raises(ValueError):
            get_producer_process_class_object(ForkServerContext)
