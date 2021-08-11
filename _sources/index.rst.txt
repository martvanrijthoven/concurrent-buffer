Concurrent Buffer Documentation
===============================

The available number of central processing units (CPUs) in home and server computers can help to parallelize and speed up specific tasks. The python programming language comes with a [multiprocessing package](https://docs.python.org/3/library/multiprocessing.html) that allows running tasks on multiple CPUs. In addition, python 3.8 introduced [shared memory](https://docs.python.org/3/library/multiprocessing.shared_memory.html), allowing for sharing data between processes. A potential use case for this shared memory is to compensate for possible speed variance when transferring data via a buffer.

This package aims to be a general solution for a particular buffer, a concurrent buffer, .i.e., a buffer filled with data using parallel running 'producer' processes.
A commander process controls the produced data via user-defined dictionary messages. At the same time, the main process can consume the data using a BufferIterator in a fast and user-friendly way.



 - :doc:`Concurrent Buffer Example <example>`

 - :doc:`Concurrent Buffer API </_autosummary/concurrentbuffer>`



.. toctree::
   :hidden:

   Home page <self>
   