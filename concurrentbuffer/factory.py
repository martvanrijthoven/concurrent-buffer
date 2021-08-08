from abc import abstractmethod
from multiprocessing import Pipe, Queue
from typing import List

from concurrentbuffer.info import BufferInfo
from concurrentbuffer.manager import SharedBufferManager
from concurrentbuffer.memory import BufferMemory
from concurrentbuffer.message import STOP_MESSAGE, MessageProcess
from concurrentbuffer.state import BufferStateMemory
from concurrentbuffer.worker import WorkerProcess


class BufferFactory:
    """Factory that builds all the components"""


    def __init__(self, cpus: int, buffer_info: BufferInfo, deterministic: bool = True):
        """Initialization

        Args:
            cpus (int): number of cpus used for the worker processes
            buffer_info (BufferInfo): info about count, shape and type of the buffers
            deterministic (bool, optional): determines if creation/retreiving of data is determinstic. Defaults to True.
        """

        self._cpus = cpus
        self._buffer_info = buffer_info
        self._deterministic = deterministic

        self._message_queue = Queue(maxsize=self._buffer_info.count)
        self._receiver, self._sender = Pipe() if self._deterministic else (None, None)

        self._init_shared_buffer_manager()
        self._init_buffer_state_memory()
        self._init_buffer_memory()
        self._init_message_process()
        self._init_worker_processes()

    @property
    def deterministic(self):
        return self._deterministic

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
            buffer=self._shared_buffer_manager.state_buffer,
        )

    def _init_buffer_memory(self):
        self._buffer_memory = BufferMemory(
            shape=self._buffer_info.shape,
            dtype=self._buffer_info.dtype,
            buffers=self._shared_buffer_manager.buffers,
        )

    def _init_message_process(self):
        self._message_process = self._create_message_process()
        self._message_process.start()

    def _init_worker_processes(self):
        self._worker_processes = self._create_worker_processes()
        for worker_process in self._worker_processes:
            worker_process.start()

    def stop(self):
        # sending stop messages to queues
        for _ in range(self._cpus):
            self._message_queue.put(STOP_MESSAGE)

        # stop worker processes
        for worker_process in self._worker_processes:
            worker_process.terminate()
            worker_process.join()

        # stop message process
        self._message_process.terminate()
        self._message_process.join()

        # close connections
        if self._deterministic:
            self._sender.close()
            self._receiver.close()

        # shutdown manager
        self._shared_buffer_manager.shutdown()

    @abstractmethod
    def _create_message_process(self) -> MessageProcess:
        """[summary]"""

    @abstractmethod
    def _create_worker_processes(self) -> List[WorkerProcess]:
        """[summary]"""
