from concurrentbuffer.system import BufferSystem
from typing import List

from concurrentbuffer.info import BufferInfo
from concurrentbuffer.manager import SharedBufferManager
from concurrentbuffer.memory import BufferMemory
from concurrentbuffer.instructor import (
    STOP_MESSAGE,
    Instructor,
    InstructorProcess,
    get_instructor_process_class_object,
)
from concurrentbuffer.state import BufferStateMemory
from concurrentbuffer.worker import (
    Worker,
    WorkerProcess,
    get_worker_process_class_object,
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
        instructor: Instructor,
        worker: Worker,
    ):
        """Initialization

        Args:
            cpus (int): number of cpus used for the worker processes
            buffer_info (BufferInfo): info about count, shape and type of the buffers
            deterministic (bool, optional): determines if creation/retreiving of data is determinstic. Defaults to True.
        """

        self._buffer_system = buffer_system
        self._buffer_info = buffer_info
        self._instructor = instructor
        self._worker = worker

        self._InstructorProcessClass = get_instructor_process_class_object(buffer_system.context)
        self._WorkerProcessClass = get_worker_process_class_object(buffer_system.context)

        self._message_queue = self._buffer_system.context.Queue(maxsize=self._buffer_info.count)
        self._receiver, self._sender = (
            self._buffer_system.context.Pipe() if self._buffer_system.deterministic else (None, None)
        )
        self._lock = self._buffer_system.context.Lock()

        self._init_shared_buffer_manager()
        self._init_buffer_state_memory()
        self._init_buffer_memory()
        self._init_message_process()
        self._init_worker_processes()

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
        self._message_process = self._create_instructor_process()
        self._message_process.start()

    def _init_worker_processes(self):
        self._worker_processes = self._create_worker_processes()
        for worker_process in self._worker_processes:
            worker_process.start()

    def shutdown(self):
        # sending stop messages to queues
        for _ in range(self._buffer_system.cpus):
            self._message_queue.put(STOP_MESSAGE)

        # stop worker processes
        for worker_process in self._worker_processes:
            worker_process.terminate()
            worker_process.join()

        # stop message process
        self._message_process.terminate()
        self._message_process.join()

        # close connections
        if self._buffer_system.deterministic:
            self._sender.close()
            self._receiver.close()

        # shutdown manager
        self._shared_buffer_manager.shutdown()

    def _create_instructor_process(self) -> InstructorProcess:
        return self._InstructorProcessClass(
            instructor=self._instructor,
            buffer_state_memory=self._buffer_state_memory,
            message_queue=self._message_queue,
            buffer_id_sender=self.sender,
        )

    def _create_worker_processes(self) -> List[WorkerProcess]:
        worker_processes = []
        for _ in range(self._buffer_system.cpus):
            worker_process = self._WorkerProcessClass(
                worker=self._worker,
                buffer_shape=self._buffer_info.shape,
                buffer_state_memory=self._buffer_state_memory,
                buffer_memory=self._buffer_memory,
                message_queue=self._message_queue,
            )
            worker_processes.append(worker_process)
        return worker_processes
