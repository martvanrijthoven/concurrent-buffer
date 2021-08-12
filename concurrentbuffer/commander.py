from abc import abstractmethod
from multiprocessing import Queue
from multiprocessing.connection import Connection
from multiprocessing.context import ForkContext, ForkProcess, SpawnContext, SpawnProcess
from typing import Optional

from concurrentbuffer.process import SubProcessObject
from concurrentbuffer.state import BufferStateMemory

STOP_MESSAGE = "/stop"
BUFFER_ID_KEY = "/buffer_id"


class Commander(SubProcessObject):
    """Abstract commander class used to create a custom commander"""

    @abstractmethod
    def create_message(self) -> dict:
        """This method creates a message that is used to create data in a worker process.

        Returns:
            dict: the message that contains instructions on how to create data
        """


class CommanderProcess:
    """Process that sends messages with information on how to create new data"""

    def __init__(
        self,
        commander: Commander,
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

        self._commander = commander
        self._buffer_state_memory = buffer_state_memory
        self._message_queue = message_queue
        self._buffer_id_sender = buffer_id_sender

    def run(self):
        self._commander.build()
        while True:
            buffer_id = self._buffer_state_memory.get_free_buffer_id()
            if buffer_id is None:
                continue
            self._message(buffer_id)

    def _message(self, buffer_id, *args, **kwargs):
        message = self._commander.create_message(*args, **kwargs)
        message[BUFFER_ID_KEY] = buffer_id
        self._message_queue.put(message)
        if self._buffer_id_sender is not None:
            self._buffer_id_sender.send(buffer_id)


class CommanderForkProcess(CommanderProcess, ForkProcess):
    """Commander class based on multiprocessing fork context process"""

    def __init__(self, *args, **kwargs):
        ForkProcess.__init__(self)
        CommanderProcess.__init__(self, *args, **kwargs)


class CommanderSpawnProcess(CommanderProcess, SpawnProcess):
    """Commander class based on multiprocessing spawn context process"""

    def __init__(self, *args, **kwargs):
        SpawnProcess.__init__(self)
        CommanderProcess.__init__(self, *args, **kwargs)


_concrete_context_processes = {
    ForkContext: CommanderForkProcess,
    SpawnContext: CommanderSpawnProcess,
}


def get_commander_process_class_object(context) -> type:
    """Factory function for creating a process class object based on a specific context

    Args:
        context (type): type of context (should be either ForkContext or SpawnContext)

    Raises:
        ValueError: context was not found in supported context processes

    Returns:
        type: producer process with specific context (either CommanderForkProcess or CommanderSpawnProcess)
    """

    try:
        return _concrete_context_processes[type(context)]
    except KeyError:
        raise ValueError(
            f"cannot find commander process class with context {context}"
        ) from None
