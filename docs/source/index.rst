.. simple-imaging documentation master file, created by
   sphinx-quickstart on Tue Mar 16 13:28:54 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

simple-imaging
==============
This is the place where you can find information about how to use the methods as 
well as examples of application.

**simple-imaging** was developed during the Digital Imaging Processing course, 
and as such should not be considered producion capable yet. 

New features and improvements are on the way.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


File reading and writing
========================

For the reading and writing of files two utility functions have been created.

There are also functions to deal with RGB channel splitting and merging.

.. automodule:: simple_imaging.image
   :members:

Image class
===========

This is where the processing operations are contained. Most of said methods accept
the `inplace` argument, a boolean that controls if the result should be generated 
as a new Image instance or if the operation should modify the current values.

The contents of the image are represented as a `list[list[Pixel]]`, where `Pixel`
is an abstraction for the Grayscale and RGB case. This allows for future extending 
of those custom types (like the RGBA, and RGB with alpha channel, for example).

.. autoclass:: Image
   :members:
   :special-members: __init__
   :private-members: _generate_working_copy,_kernel_filter,_return_result,_sliding_window

Custom Types
============
For this project we defined a base abstract Pixel class using `Python's Protocol`.

This allowed for the definition of abstract basic pixel operations 
(like, `darken`, `lighten` and `negative`) and ensuring that there's no heavy 
couplling between `Image` and the Pixel type

.. autoclass:: Pixel
   :members:

.. automodule:: simple_imaging.types
   :members:
   :special-members: __init__

Utilities
=========
There're many utility functions used to parse, validate and process the input 
file before the image operations. They are documented below.

.. automodule:: simple_imaging.utils
   :members:
   :private-members:
   :undoc-members:

Exceptions
==========
A set of custom Exceptions has been screated to allow for more specific errors
when dealing with the validations.

.. automodule:: simple_imaging.errors
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
