Požadavky na modul a jeho omezení
----------------------------------------------------------------------------------------------------

Požadavky na funkci modulu
...................................................

Požadavky které jsou kladeny na funkci systému.

#. modul ukládá informace o epublikaci do adresáře
#. z tohoto adresáře si je čte **Aleph**
#. modul je konfigurovatelný (cesta k Aleph pro metadata, ...)
#. modul přijímá zprávy v **RabbitMQ**
#. modul sleduje odpovědi **Alephu** na import
#. modul odešle odpověd z **Alephu** do exchange v **RabbitMQ**
#. modul si pamatuje, jestli už oodpověd z **Alephu** poslal

Omezení systému
............................

#. modul se připojuje k **RabbitMQ**
#. modul je napsaný v jazyce **Python**
#. modul ukládá svá data do adresáře
