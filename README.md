# Concurrent Buffer


[![PyPI](https://img.shields.io/pypi/v/concurrentbuffer)](https://pypi.org/project/concurrentbuffer/)
[![tests](https://github.com/martvanrijthoven/concurrent-buffer/actions/workflows/tests.yml/badge.svg)](https://github.com/martvanrijthoven/concurrent-buffer/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/martvanrijthoven/concurrent-buffer/badge.svg?branch=main)](https://coveralls.io/github/martvanrijthoven/concurrent-buffer?branch=main)


This package offers a concurrent buffer that allows you to parallelize the creation of [NumPy](https://numpy.org/) arrays by utilizing multiple CPUs. It's built using Python's multiprocessing package and leverages shared memory, introduced in Python 3.8, to share data between processes. The concurrent buffer is filled with data by "producer" processes, while a "commander" process controls the creation of the data using user-defined dictionary messages. The main process can then consume the data efficiently using a BufferIterator. 

Please see below the [installation instructions](#installation-and-dependencies) and an [example](#example-usage) on how to use this package as well as how to [create your own commander](#creating-a-commander) and how to [create your own producer](#creating-a-producer). Feel free to open an issue if you have any questions or remarks.

## Installation and Dependencies

This package requires [python>=3.8](https://www.python.org/downloads/) and [NumPy](https://github.com/numpy/numpy) 

A binary installer for the latest version is available at the [Python Package Index (PyPI)](https://pypi.org/project/concurrentbuffer/)
```bash
pip install concurrentbuffer
```

## Example usage:

Important note: 
 - 'spawn' multiprocessing context will not work in a jupyter notebook/lab, use fork instead when working in a jupyter notebook / jupyter lab


###### Easy Usage:

```python     

    from concurrentbuffer.iterator import buffer_iterator_factory

    # the number of cpus/producers
    cpus = 8

    # the buffershape in the shared memory
    buffer_shapes = ((64, 256, 256, 3),)
    
    # the context of multiprocess (spawn or fork)
    context = 'spawn'

    # if the messages from the commander and the produced data are first in first out
    deterministic = True

    # You will have to create your own Commander class, please see instructions below
    # a user defined commander, should subclass the Commander class
    commander = IndexCommander(max_index=10)

    # You will have to create your own Producer class, please see instructions below
    # a user defined producer, should subclass the Producer class
    producer = DataProducer(data_shapes=buffer_shapes)

    # create a buffer iterator
    buffer_iterator = buffer_iterator_factory(
        cpus=cpus,
        buffer_shapes=buffer_shapes,
        commander=commander,
        producer=producer,
        context=context,
        deterministic=deterministic,
    )

    # loop through the buffer that is filled concurrently
    for index in range(10):
        data = next(buffer_iterator)
        
    # always stop the iterator to close all processes and free the shared memory
    buffer_iterator.stop()
        
```

###### Advanced Usage:

```python

from multiprocessing.context import ForkContext, SpawnContext

from concurrentbuffer.factory import BufferFactory
from concurrentbuffer.info import BufferInfo
from concurrentbuffer.iterator import BufferIterator
from concurrentbuffer.state import BufferState
from concurrentbuffer.system import BufferSystem


# the number of cpus/producers
cpus = 8

# the buffershape in the shared memory
buffer_shapes = ((64, 256, 256, 3),)

# the context of multiprocess (spawn or fork)
context = SpawnContext()

# if the messages from the commander and the produced data are first in first out
deterministic = True

# the number of buffers each with shape of buffer_shape
count = cpus * len(BufferState)

# buffer system contains the information of the system
buffer_system = BufferSystem(
    cpus=cpus, context=context, deterministic=deterministic
)

# buffer info contains the information of the buffers 
buffer_info = BufferInfo(count=count, shapes=buffer_shapes)

# You will have to create your own Commander class, please see instructions below
# a user defined commander, should subclass the Commander class
commander = IndexCommander(max_index=10)

# You will have to create your own Producer class, please see instructions below
# a user defined producer, should subclass the Producer class
producer = DataProducer(data_shapes=buffer_shapes)

# a factor class that builds the buffer components
buffer_factory = BufferFactory(
    buffer_system=buffer_system,
    buffer_info=buffer_info,
    commander=commander,
    producer=producer,
)

# a buffer iterator created with the buffer factory that allows iterating throught the 'concurrent' buffer.
with BufferIterator(buffer_factory=buffer_factory) as data_buffer_iterator:
    for index in range(10):
        data = next(data_buffer_iterator)

```


#### Creating a Commander
```
from concurrentbuffer.commander import Commander
class IndexCommander(Commander):
    def __init__(self, max_index: int):
        self._max_index = max_index
        self._index = 0

    def create_message(self) -> dict:
        message = {"index": self._index}
        self._index = (self._index + 1) % self._max_index
        return message
```


#### Creating a Producer
```
import numpy as np
from concurrentbuffer.producer import Producer

class DataProducer(Producer):
    def __init__(self, data_shapes: tuple):
        self._data_shapes = data_shapes

    def create_data(self, message: dict) -> np.ndarray:
        index = message['index']
        return self._time_consuming_processing(index)

    def _time_consuming_processing(self, index) -> np.ndarray:
        ...
        #TODO use index and self._data_shape to create and process a numpy array
```

