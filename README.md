# Concurrent Buffer

[![tests](https://github.com/martvanrijthoven/concurrent-buffer/actions/workflows/tests.yml/badge.svg)](https://github.com/martvanrijthoven/concurrent-buffer/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/martvanrijthoven/concurrent-buffer/branch/main/graph/badge.svg?token=0619Z63PMA)](https://codecov.io/gh/martvanrijthoven/concurrent-buffer)
[![docs](https://github.com/martvanrijthoven/concurrent-buffer/actions/workflows/docs.yml/badge.svg)](https://github.com/martvanrijthoven/concurrent-buffer/actions/workflows/docs.yml)



The available number of central processing units (CPUs) in home and server computers can help to parallelize and speed up specific tasks. The python programming language comes with a [multiprocessing package](https://docs.python.org/3/library/multiprocessing.html) that allows running tasks on multiple CPUs. In addition, python 3.8 introduced [shared memory](https://docs.python.org/3/library/multiprocessing.shared_memory.html), allowing for sharing data between processes. A potential use case for this shared memory is to compensate for possible speed variance when transferring data via a buffer.

This package aims to be a general solution for a particular buffer, a concurrent buffer, .i.e., a buffer filled with data using parallel running 'producer' processes.
A commander process controls the produced data via user-defined dictionary messages. At the same time, the main process can consume the data using a BufferIterator in a fast and user-friendly way.

Please see below the [installation instructions](installation-and-dependencies) and an [example](#example-usage) on how to use this package as well as how to create your own commander and producer. For more information please see the [docs](https://martvanrijthoven.github.io/concurrent-buffer/). Feel free to open issue if you have any questions or remarks.

## Installation and Dependencies

This package requires [python>=3.8](https://www.python.org/downloads/) and [numpy](https://github.com/numpy/numpy) 

A binary installer for the latest version is available at the [Python Package Index (PyPI)](https://pypi.org/project/concurrentbuffer/)
```bash
pip install concurrentbuffer
```

## Example usage:

### Easy Usage:

```python     

    from concurrentbuffer.iterator import buffer_iterator_factory

    # the number of cpus/producers
    cpus = 8

    # the buffershape in the shared memory
    buffer_shape = (64, 256, 256, 3)
    
    # the context of multiprocess (spawn or fork)
    context = 'spawn'

    # if the messages from the commander and the produced data are first in first out
    deterministic = True

    # You will have to create your own Commander class, please see instructions below
    # a user defined commander, should subclass the Commander class
    commander = IndexCommander(max_index=10)

    # You will have to create your own Producer class, please see instructions below
    # a user defined producer, should subclass the Producer class
    producer = DataProducer(data_shape=buffer_shape)

    # create a buffer iterator
    buffer_iterator = buffer_iterator_factory(
        cpus=cpus,
        buffer_shape=buffer_shape,
        commander=commander,
        producer=producer,
        context=context,
        deterministic=deterministic,
    )

    # loop through the buffer that is filled concurrently at the same time
    for index in range(10):
        data = next(buffer_iterator)
        
    # always stop the iterator to close all processes and free the shared memory
    buffer_iterator.stop()
        
```

### Advanced Usage:

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
buffer_shape = (64, 256, 256, 3)

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
buffer_info = BufferInfo(count=count, shape=buffer_shape)

# You will have to create your own Commander class, please see instructions below
# a user defined commander, should subclass the Commander class
commander = IndexCommander(max_index=10)

# You will have to create your own Producer class, please see instructions below
# a user defined producer, should subclass the Producer class
producer = DataProducer(data_shape=buffer_shape)

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
        message = {"index": index}
        self._index = (self._index + 1) % self._max_index
        return message
```


#### Creating a Producer
```
import numpy as np
from concurrentbuffer.producer import Producer

class DataProducer(Producer):
    def __init__(self, data_shape: tuple):
        self._data_shape = data_shape

    def create_data(self, message: dict) -> np.ndarray:
        index = message['index']
        return self._time_consuming_processing(index)

    def _time_consuming_processing(self, index) -> np.ndarray:
        ...
        #TODO use index and self._data_shape to create and process a numpy array
```

