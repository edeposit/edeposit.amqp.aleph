Introduction
============

This package provides an AMQP middle-ware for communication with Aleph. `Aleph <http://www.exlibrisgroup.com/category/Aleph>`_ is a system used in libraries to store meta-data about books and
authors.

`Full module documentation <http://edeposit-amqp-aleph.readthedocs.org>`_ is hosted at the ReadTheDocs.

Installation
------------

Module is hosted at `PYPI <http://pypi.python.org>`_, and can be easily installed using `PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_:

::

    pip install edeposit.amqp.aleph

Source codes can be found at `GitHub <https://github.com/>`_: https://github.com/jstavel/edeposit.amqp.aleph.

Content
-------
Module provides several submodules:

edeposit.amqp.aleph.__init__
++++++++++++++++++++++++++++
Data structures for (generic, not just AMQP) communication. It contains reaction function ``reactToAMQPMessage()``, which detects what (serialized) structure was given to her, do some low-level interactions with Aleph and returns result structures.

Module provides also serialize/deserialze functions for generic python ``namedtuple`` structures.

edeposit.amqp.aleph.aleph
+++++++++++++++++++++++++
Used for raw communication with Aleph server. Communication is read-only and uses special API provided by Aleph X-Services module.

Can be queried using ``reactToAMQPMessage()`` defined in ``__init__``.

edeposit.amqp.aleph.marcxml
+++++++++++++++++++++++++++
MARC XML (de)serialization class, which provides some higher-level bindings to MARC records.

edeposit.amqp.aleph.convertor
+++++++++++++++++++++++++++++
Convertor from MARC XML records to Epublication structures defined in ``__init__``.

edeposit.amqp.aleph.isbn
++++++++++++++++++++++++
ISBN checksum validator.

Can be queried using ``reactToAMQPMessage()`` defined in ``__init__``.

Acceptance tests
----------------

`Robot Framework <http://robotframework.org/>`__ is used to test the sources, which are stored in ``src/edeposit/amqp/aleph/tests`` directory.

You can run them manually (from the root of the package):

::

    $ pybot -W 80 --pythonpath src/edeposit/amqp/aleph/tests/:src src/edeposit/amqp/aleph/tests/

Or continuously using nosier:

::

    $ nosier -p src -b 'export' "pybot -W 80 --pythonpath src/edeposit/amqp/aleph/tests/ --pythonpath src src/edeposit/amqp/aleph/tests/"

Command to run the test is wrapped in ``run_tests.sh`` in the root of the project.

Status of acceptance tests
++++++++++++++++++++++++++

You can see the results of the tests here:

http://edeposit-amqp-aleph.readthedocs.org/cs/latest/\_downloads/log.html

http://edeposit-amqp-aleph.readthedocs.org/cs/latest/\_downloads/report.html

Results are currently (12.03.2014) outdated, but some form of continuous integration framework will be used in the future.