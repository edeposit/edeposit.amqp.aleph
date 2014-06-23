#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple


class AlephRecord(namedtuple("AlephRecord", ['base',
                                             'library',
                                             'docNumber',
                                             'xml',
                                             'epublication'])):
    """
    This structure is returned as response to :class:`.SearchRequest` inside
    :class:`.SearchResult`.

    Attributes:
        base (str): Identity of base where this record is stored.
        library (str): Library string, used for downloading documents from
                       Aleph when you know proper `docNumber`.
        docNumber (str): Identificator in Aleph. It is not that much unique as
                         it could be, but with :attr:`library` string, you can
                         fetch documents from Aleph if you know this.
        xml (str): MARC XML source returned from Aleph. Quite complicated
                   stuff.
        epublication (EPublication): Parsed ``.xml`` to :class:`.EPublication`
                                     structure.
    """
    pass
