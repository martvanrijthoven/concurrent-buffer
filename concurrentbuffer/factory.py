from concurrentbuffer.iterator import BufferIterator
import multiprocessing
from concurrentbuffer.system import BufferSystem
from typing import List

from concurrentbuffer.info import BufferInfo
from concurrentbuffer.state import BufferState
from concurrentbuffer.manager import SharedBufferManager
from concurrentbuffer.memory import BufferMemory
from concurrentbuffer.commander import (
    STOP_MESSAGE,
    Commander,
    CommanderProcess,
    get_commander_process_class_object,
)
from concurrentbuffer.state import BufferStateMemory
from concurrentbuffer.producer import (
    Producer,
    ProducerProcess,
    get_producer_process_class_object,
)


# use spawn with pickable object
# use spawn with build function
# use fork
# use fork with build function


class BufferFactory:
    """Factory that builds all the components"""

    def __init__(
        self,
        buffer_system: BufferSystem,
        buffer_info: BufferInfo,
        commander: Commander,
        producer: Producer,
    ):
        """Initialization

        Args:
            cpus (int): number of cpus used for the producer processes
            buffer_info (BufferInfo): info about count, shape and type of the buffers
            deterministic (bool, optional): determines if creation/retreiving of data is determinstic. Defaults to True.
        """

        self._buffer_system = buffer_system
        self._buffer_info = buffer_info
        self._commander = commander
        self._producer = producer

        self._CommanderProcessClass = get_commander_process_class_object(
            buffer_system.context
        )
        self._ProducerProcessClass = get_producer_process_class_object(
            buffer_system.context
        )

        self._message_queue = self._buffer_system.context.Queue(
            maxsize=self._buffer_info.count
        )
        self._receiver, self._sender = (
            self._buffer_system.context.Pipe()
            if self._buffer_system.deterministic
            else (None, None)
        )
        self._lock = self._buffer_system.context.Lock()

        self._init_shared_buffer_manager()
        self._init_buffer_state_memory()
        self._init_buffer_memory()
        self._init_message_process()
        self._init_producer_processes()

    @property
    def buffer_system(self):
        return self._buffer_system

    @property
    def buffer_state_memory(self):
        return self._buffer_state_memory

    @property
    def buffer_memory(self):
        return self._buffer_memory

    @property
    def receiver(self):
        return self._receiver

    @property
    def sender(self):
        return self._sender

    def _init_shared_buffer_manager(self):
        self._shared_buffer_manager = SharedBufferManager(buffer_info=self._buffer_info)
        self._shared_buffer_manager.start()

    def _init_buffer_state_memory(self):
        self._buffer_state_memory = BufferStateMemory(
            count=self._buffer_info.count,
            dtype=self._buffer_info.dtype,
            lock=self._lock,
            buffer=self._shared_buffer_manager.state_buffer,
        )

    def _init_buffer_memory(self):
        self._buffer_memory = BufferMemory(
            shape=self._buffer_info.shape,
            dtype=self._buffer_info.dtype,
            buffers=self._shared_buffer_manager.buffers,
        )

    def _init_message_process(self):
        self._message_process = self._create_commander_process()
        self._message_process.start()

    def _init_producer_processes(self):
        self._producer_processes = self._create_producer_processes()
        for producer_process in self._producer_processes:
            producer_process.start()

    def shutdown(self):
        # sending stop messages to queues
        for _ in range(self._buffer_system.cpus):
            self._message_queue.put(STOP_MESSAGE)

        # stop producer processes
        for producer_process in self._producer_processes:
            producer_process.terminate()
            producer_process.join()

        # stop message process
        self._message_process.terminate()
        self._message_process.join()

        # close connections
        if self._buffer_system.deterministic:
            self._sender.close()
            self._receiver.close()

        # shutdown manager
        self._shared_buffer_manager.shutdown()

    def _create_commander_process(self) -> CommanderProcess:
        return self._CommanderProcessClass(
            commander=self._commander,
            buffer_state_memory=self._buffer_state_memory,
            message_queue=self._message_queue,
            buffer_id_sender=self.sender,
        )

    def _create_producer_processes(self) -> List[ProducerProcess]:
        producer_processes = []
        for _ in range(self._buffer_system.cpus):
            producer_process = self._ProducerProcessClass(
                producer=self._producer,
                buffer_shape=self._buffer_info.shape,
                buffer_state_memory=self._buffer_state_memory,
                buffer_memory=self._buffer_memory,
                message_queue=self._message_queue,
            )
            producer_processes.append(producer_process)
        return producer_processes


