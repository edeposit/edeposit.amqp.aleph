Introduction
============

This package provides an AMQP middleware for communication with Aleph.

You can read [full documentation](http://edeposit-amqp-aleph.readthedocs.org/cs/latest/ "Full Documentation")


Acceptance tests
-----------------

They are written using Robot Framework.

All tests are stored at src/tests directory.

You can run them manually

    jan@jan-XPS-L421X:~/work/edeposit.amqp.aleph$ pybot -W 100 --pythonpath src --pythonpath src/edeposit/amqp/aleph/tests/ src/edeposit/amqp/aleph/tests/


... or continuously running using nosier:

    jan@jan-XPS-L421X:~/work/edeposit.amqp.aleph$ nosier -p src -b 'export' "pybot -W 100 --pythonpath src/edeposit/amqp/aleph/tests/ --pythonpath src src/edeposit/amqp/aleph/tests/"


Status of acceptance tests
--------------------------

You can see results of tests at files 

http://edeposit-amqp-aleph.readthedocs.org/cs/latest/_downloads/log.html
http://edeposit-amqp-aleph.readthedocs.org/cs/latest/_downloads/report.html
