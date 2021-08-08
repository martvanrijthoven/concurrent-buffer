from concurrentbuffer.info import BufferInfo
from concurrentbuffer.manager import SharedBufferManager, SharedBufferManagerNotStarted
from concurrentbuffer.state import BufferState
from pytest import raises


class TestErrors:
    def test_buffers_error(self):

        with raises(SharedBufferManagerNotStarted):
            cpus = 6
            count = cpus * len(BufferState)
            buffer_shape = (12, 284, 284, 3)
            buffer_info = BufferInfo(count=count, shape=buffer_shape)
            shared_buffer_manager = SharedBufferManager(buffer_info=buffer_info)
            shared_buffer_manager.buffers

    def test_buffer_state_error(self):

        with raises(SharedBufferManagerNotStarted):
            cpus = 6
            count = cpus * len(BufferState)
            buffer_shape = (12, 284, 284, 3)
            buffer_info = BufferInfo(count=count, shape=buffer_shape)
            shared_buffer_manager = SharedBufferManager(buffer_info=buffer_info)
            shared_buffer_manager.state_buffer
