from abc import abstractmethod
from multiprocessing import Queue
from multiprocessing.context import ForkContext, ForkProcess, SpawnContext, SpawnProcess

import numpy as np

from concurrentbuffer.instructor import BUFFER_ID_KEY, STOP_MESSAGE
from concurrentbuffer.memory import BufferMemory
from concurrentbuffer.process import SubProcessObject
from concurrentbuffer.state import BufferStateMemory


class Worker(SubProcessObject):
    @abstractmethod
    def create_data(self, message: dict) -> np.ndarray:
        """This method creates the data based on a message and puts it into a buffer.

        Args:
            message (dict): the message that includes instruction info for the creation of the data.

        Returns:
            np.ndarray: the created data.
        """


class WorkerProcess:
    """Process that creates data and puts in into a shared memory buffer."""

    def __init__(
        self,
        worker: Worker,
        buffer_shape: tuple,
        buffer_state_memory: BufferStateMemory,
        buffer_memory: BufferMemory,
        message_queue: Queue,
    ):
        """Initialization

        Args:
            buffer_shape (tuple): shape of the data in the buffers, needs to be used when creating new data
            buffer_state_memory (BufferStateMemory): buffer that contains the states of the buffer memory
            buffer_memory (BufferMemory): contains the buffers
            message_queue (Queue): queue that receives messages from a MessageProcess that can be used to construct data
        """

        self.daemon = True

        self._worker = worker
        self._buffer_shape = buffer_shape
        self._buffer_state_memory = buffer_state_memory
        self._buffer_memory = buffer_memory
        self._message_queue = message_queue

    def run(self):
        self._worker.build()
        for message in iter(self._message_queue.get, STOP_MESSAGE):
            buffer_id = message[BUFFER_ID_KEY]
            data = self._worker.create_data(message=message)
            self._buffer_memory.update_buffer(buffer_id=buffer_id, data=data)
            self._buffer_state_memory.update_buffer_id_to_available(buffer_id=buffer_id)


class WorkerForkProcess(WorkerProcess, ForkProcess):
    def __init__(self, *args, **kwargs):
        ForkProcess.__init__(self)
        WorkerProcess.__init__(self, *args, **kwargs)


class WorkerSpawnProcess(WorkerProcess, SpawnProcess):
    def __init__(self, *args, **kwargs):
        SpawnProcess.__init__(self)
        WorkerProcess.__init__(self, *args, **kwargs)


def get_worker_process_class_object(context) -> type:
    if isinstance(context, ForkContext):
        return WorkerForkProcess
    if isinstance(context, SpawnContext):
        return WorkerSpawnProcess
