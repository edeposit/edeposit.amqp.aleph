.. _usage:

Použití
--------------------

.. toctree::
   :maxdepth: 2

   usage-keywords

Export dat do *Alephu*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Probíhá přes soubory ve složce, ze které si Aleph stahuje informace SSH. 
Konkrétní příklad je možné najít v test resources 
(:file:`src/edeposit/amqp/aleph/tests/resources`).

Diagramy komunikace:

`Datový model pro komunikaci se systémem Aleph <https://e-deposit.readthedocs.org/cs/latest/middleware/dm03.html>`_ a
`Sekvenční diagram popisující způsob komunikace <https://e-deposit.readthedocs.org/cs/latest/middleware/seq02.html>`_.

.. robot_tests::
   :source: ../src/edeposit/amqp/aleph/tests/test_export.txt

Dotaz do *Alephu*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Konkrétní způsob dotazování Aleph API je popsaný 
:download:`zde<downloads/propojeni-do-katalogu-aleph.html>`.

`Datový model pro komunikaci se systémem Aleph <https://e-deposit.readthedocs.org/cs/latest/middleware/dm03.html>`_ a
`Sekvenční diagram popisující způsob komunikace <https://e-deposit.readthedocs.org/cs/latest/middleware/seq02.html>`_.


.. robot_tests::
   :source: ../src/edeposit/amqp/aleph/tests/test_search.txt


