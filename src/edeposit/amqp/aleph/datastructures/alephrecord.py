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
    This structure is returned as response to SearchRequest inside
    SearchResult.

    Attributes:
        base (str): from which base was this record pulled
        library (str): library string, used for downloading documents from
                       Aleph when you know proper docNumber
        docNumber (str): identificator in Aleph. It is not that much unique as
                         it could be, but with .library string, you can fetch
                         documents from Aleph if you know this.
        xml (str): MARC XML source returned from Aleph. Quite complicated
                   stuff.
        epublication (EPublication): parsed .xml to
             :class:`aleph.datastructures.epublication.EPublication` structure
    """
    pass
