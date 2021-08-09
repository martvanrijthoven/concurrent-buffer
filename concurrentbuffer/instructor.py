from abc import abstractmethod
from multiprocessing import Queue
from multiprocessing.connection import Connection
from typing import Optional
from multiprocessing.context import SpawnProcess, ForkProcess
from concurrentbuffer.process import SubProcessObject
from concurrentbuffer.state import BufferStateMemory

STOP_MESSAGE = "/stop"
BUFFER_ID_KEY = "/buffer_id"


class Instructor(SubProcessObject):
    @abstractmethod
    def create_message(self) -> dict:
        """This method creates a message that is used to create data in a worker process.

        Returns:
            dict: the message that contains instructions on how to create data
        """


class InstructorProcess:
    """Process that sends messages with information on how to create new data"""

    def __init__(
        self,
        instructor: Instructor,
        buffer_state_memory: BufferStateMemory,
        message_queue: Queue,
        buffer_id_sender: Optional[Connection],
    ):
        """Init

        Args:
            buffer_state_memory (BufferStateMemory): contains the states of the buffers
            message_queue (Queue): queue that is used to send information on how to create data
            buffer_id_sender (Optional[Connection]): connection that is used to send the buffer_id, used to ensure determinstic behaviour.
        """

        super().__init__()
        self.daemon = True

        self._instructor = instructor
        self._buffer_state_memory = buffer_state_memory
        self._message_queue = message_queue
        self._buffer_id_sender = buffer_id_sender

    def run(self):
        self._instructor.build()
        while True:
            buffer_id = self._buffer_state_memory.get_free_buffer_id()
            if buffer_id is None:
                continue
            self._message(buffer_id)

    def _message(self, buffer_id, *args, **kwargs):
        message = self._instructor.create_message(*args, **kwargs)
        message[BUFFER_ID_KEY] = buffer_id
        self._message_queue.put(message)
        if self._buffer_id_sender is not None:
            self._buffer_id_sender.send(buffer_id)


class InstructorForkProcess(InstructorProcess, ForkProcess):
    def __init__(self, *args, **kwargs):
        ForkProcess.__init__(self)
        InstructorProcess.__init__(self, *args, **kwargs)


class InstructorSpawnProcess(InstructorProcess, SpawnProcess):
    def __init__(self, *args, **kwargs):
        SpawnProcess.__init__(self)
        InstructorProcess.__init__(self, *args, **kwargs)


def get_instructor_process_class_object(context) -> type:
    if context == "fork":
        return InstructorForkProcess
    elif context == "spawn":
        return InstructorSpawnProcess