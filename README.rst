Introduction
============

This package provides an AMQP middle-ware for communication with Aleph.
Aleph is system used in libraries to store meta-data about books and
authors.

You can read `some
documentation <http://edeposit-amqp-aleph.readthedocs.org/cs/latest/>`__,
but that is based on acceptance test and not really actual.

Actual documentation can be found in docstrings in each .py source file.

Acceptance tests
----------------

They are written using `Robot Framework <http://robotframework.org/>`__
and they are stored at src/edeposit/amqp/aleph/tests directory.

You can run them manually (from the root of the package):

::

    $ pybot -W 100 --pythonpath src/edeposit/amqp/aleph/tests/:src src/edeposit/amqp/aleph/tests/

Or continuously using nosier:

::

    $ nosier -p src -b 'export' "pybot -W 100 --pythonpath src/edeposit/amqp/aleph/tests/ --pythonpath src src/edeposit/amqp/aleph/tests/"

Status of acceptance tests
--------------------------

You can see results of tests at files

http://edeposit-amqp-aleph.readthedocs.org/cs/latest/\_downloads/log.html

http://edeposit-amqp-aleph.readthedocs.org/cs/latest/\_downloads/report.html
