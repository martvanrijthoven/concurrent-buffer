Concurrent Buffer Example
=========================

#### Example Usage

##### easy usage

.. code-block:: python

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
    producer = DataProducer(data_shape=BUFFER_SHAPE)

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


##### advanced usage

.. code-block:: python

    from multiprocessing.context import ForkContext, SpawnContext

    from concurrentbuffer.factory import BufferFactory
    from concurrentbuffer.info import BufferInfo
    from concurrentbuffer.iterator import BufferIterator
    from concurrentbuffer.state import BufferState
    from concurrentbuffer.system import BufferSystem


    # the number of cpus/producers
    CPUS = 8

    # the buffershape in the shared memory
    BUFFER_SHAPE = (64, 256, 256, 3)

    # the context of multiprocess (spawn or fork)
    CONTEXT = SpawnContext()

    # if the messages from the commander and the produced data are first in first out
    DETERMINISTIC = True

    # the number of buffers each with shape of BUFFERSHAPE
    count = CPUS * len(BufferState)

    # buffer system contains the information of the system
    buffer_system = BufferSystem(
        cpus=CPUS, context=CONTEXT, deterministic=DETERMINISTIC
    )

    # buffer info contains the information of the buffers 
    buffer_info = BufferInfo(count=count, shape=BUFFER_SHAPE)

    # You will have to create your own Commander class, please see instructions below
    # a user defined commander, should subclass the Commander class
    commander = IndexCommander(max_index=10)

    # You will have to create your own Producer class, please see instructions below
    # a user defined producer, should subclass the Producer class
    producer = DataProducer(data_shape=BUFFER_SHAPE)

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


##### Creating a Commander

.. code-block:: python

    from concurrentbuffer.commander import Commander
    class IndexCommander(Commander):
        def __init__(self, max_index: int):
            self._max_index = max_index
            self._index = 0

        def create_message(self) -> dict:
            message = {"index": index}
            self._index = (self._index + 1) % self._max_index
            return message


##### Creating a Producer

.. code-block:: python

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