from multiprocessing.context import BaseContext, SpawnContext


class BufferSystem:
    """This class contains system information"""

    def __init__(
        self,
        cpus: int,
        context: BaseContext = SpawnContext(),
        deterministic: bool = True,
    ):
        self._cpus = cpus
        self._context = context
        self._deterministic = deterministic

    @property
    def cpus(self):
        return self._cpus

    @property
    def context(self):
        return self._context

    @property
    def deterministic(self):
        return self._deterministic
