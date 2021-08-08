import numpy as np

class BufferInfo:
    """Class that contains information about the count, shape and type of the buffers
    """
    
    def __init__(
        self,
        count: int,
        shape: tuple,
        dtype: np.dtype = np.dtype("uint8"),
    ):
        """Init

        Args:
            count (int): count of buffers
            shape (tuple): shape of a single buffer
            dtype (np.dtype, optional): type of the data in the buffers. Defaults to np.dtype("uint8").
        """

        self._count = count
        self._shape = shape
        self._dtype = dtype

    @property
    def count(self) -> int:
        return self._count

    @property
    def shape(self) -> tuple:
        return self._shape

    @property
    def dtype(self) -> np.dtype:
        return self._dtype
