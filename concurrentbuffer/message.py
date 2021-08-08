from abc import abstractmethod
from multiprocessing import Process, Queue
from multiprocessing.connection import Connection
from typing import Optional

from concurrentbuffer.state import BufferStateMemory

STOP_MESSAGE = "/stop"
BUFFER_ID_KEY = "/buffer_id"

class MessageProcess(Process):
    """Process that sends messages with information on how to create new data
    """

    def __init__(
        self,
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

        self._buffer_state_memory = buffer_state_memory
        self._message_queue = message_queue
        self._buffer_id_sender = buffer_id_sender

    def run(self):
        while True:
            buffer_id = self._buffer_state_memory.get_free_buffer_id()
            if buffer_id is None:
                continue
            self._message(buffer_id)

    def _message(self, buffer_id, *args, **kwargs):
        message = self.create_message(*args, **kwargs)
        message[BUFFER_ID_KEY] = buffer_id
        self._message_queue.put(message)
        if self._buffer_id_sender is not None:
            self._buffer_id_sender.send(buffer_id)

    @abstractmethod
    def create_message(self) -> dict:
        """This method creates a message that is used to create data in a worker process.

        Returns:
            dict: the message that contains instructions on how to create data
        """

