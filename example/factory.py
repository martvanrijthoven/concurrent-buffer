from concurrentbuffer.factory import BufferFactory
from typing import List

from concurrentbuffer.message import MessageProcess
from concurrentbuffer.worker import WorkerProcess

from concurrentbufferexample.message import DataMessageProcess
from concurrentbufferexample.worker import DataWorkerProcess

"""
Example BufferIterator
"""


class DataBufferFactory(BufferFactory):
    def _create_message_process(self) -> MessageProcess:
        return DataMessageProcess(
            buffer_state_memory=self._buffer_state_memory,
            message_queue=self._message_queue,
            buffer_id_sender=self.sender,
        )

    def _create_worker_processes(self) -> List[WorkerProcess]:
        worker_processes = []
        for _ in range(self._cpus):
            worker_process = DataWorkerProcess(
                buffer_shape=self._buffer_info.shape,
                buffer_state_memory=self._buffer_state_memory,
                buffer_memory=self._buffer_memory,
                message_queue=self._message_queue,
            )
            worker_processes.append(worker_process)
        return worker_processes
