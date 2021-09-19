from abc import abstractmethod
from multiprocessing import Queue
from multiprocessing.context import ForkContext, ForkProcess, SpawnContext, SpawnProcess
from typing import List

import numpy as np

from concurrentbuffer.commander import BUFFER_ID_KEY, STOP_MESSAGE
from concurrentbuffer.memory import BufferMemory
from concurrentbuffer.process import SubProcessObject
from concurrentbuffer.state import BufferStateMemory


class Producer(SubProcessObject):
    """Abstract producer class used to create custom producers"""

    @abstractmethod
    def create_data(self, message: dict) -> np.ndarray:
        """This method creates the data based on a message and puts it into a buffer.

        Args:
            message (dict): the message that includes instruction info for the creation of the data.

        Returns:
            np.ndarray: the created data.
        """


class ProducerProcess:
    """Process that creates data and puts in into a shared memory buffer."""

    def __init__(
        self,
        producer: Producer,
        buffer_shapes: tuple,
        buffer_state_memory: BufferStateMemory,
        buffer_memories: List[BufferMemory],
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

        self._producer = producer
        self._buffer_shapes = buffer_shapes
        self._buffer_state_memory = buffer_state_memory
        self._buffer_memories = buffer_memories
        self._message_queue = message_queue

    def run(self):
        self._producer.build()
        for message in iter(self._message_queue.get, STOP_MESSAGE):
            buffer_id = message[BUFFER_ID_KEY]
            data = self._producer.create_data(message=message)
            for idx, buffer_memory in enumerate(self._buffer_memories):
                buffer_memory.update_buffer(buffer_id=buffer_id, data=data[idx])
            self._buffer_state_memory.update_buffer_id_to_available(buffer_id=buffer_id)


class ProducerForkProcess(ProducerProcess, ForkProcess):
    """Producer class based on multiprocessing fork context process"""

    def __init__(self, *args, **kwargs):
        ForkProcess.__init__(self)
        ProducerProcess.__init__(self, *args, **kwargs)


class ProducerSpawnProcess(ProducerProcess, SpawnProcess):
    """Producer class based on multiprocessing spawn context process"""

    def __init__(self, *args, **kwargs):
        SpawnProcess.__init__(self)
        ProducerProcess.__init__(self, *args, **kwargs)


_CONCRETE_PRODUCER_CONTEXT_PROCESSES = {
    ForkContext: ProducerForkProcess,
    SpawnContext: ProducerSpawnProcess,
}

def get_producer_process_class_object(context: type) -> type:
    """Factory function for creating a process class object based on a specific context

    Args:
        context (type): type of context (should be either ForkContext or SpawnContext)

    Raises:
        ValueError: context was not found in supported context processes

    Returns:
        type: producer process with specific context (either ProducerForkProcess or ProducerSpawnProcess)
    """

    try:
        return _CONCRETE_PRODUCER_CONTEXT_PROCESSES[type(context)]
    except KeyError:
        raise ValueError(
            f"cannot find producer process class with context {context}"
        ) from None
