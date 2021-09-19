import numpy as np

class BufferInfo:
    """Class that contains information about the count, shape and type of the buffers
    """

    def __init__(
        self,
        shapes: tuple,
        count: int,
        dtype: type = np.dtype("uint8"),
    ):
        """Init

        Args:
            count (int): count of buffers
            shape (tuple): shape of a single buffer
            dtype (np.dtype, optional): type of the data in the buffers. Defaults to np.dtype("uint8").
        """

        self._shapes = shapes
        self._length = len(shapes)
        self._count = count
        self._dtype = dtype

    def __len__(self):
        return self._length

    @property
    def count(self) -> int:
        return self._count

    @property
    def shapes(self) -> tuple:
        return self._shapes

    @property
    def dtype(self) -> np.dtype:
        return self._dtype
