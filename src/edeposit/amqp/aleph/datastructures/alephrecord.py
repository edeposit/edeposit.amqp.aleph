#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
"""
Following structures are used to represent informations returned from Aleph.

API
---
"""
# Imports =====================================================================
from collections import namedtuple

from marcxml_parser import MARCXMLRecord

from semanticinfo import SemanticInfo
from epublication import EPublication


# Structures ==================================================================
class AlephRecord(namedtuple("AlephRecord", ['base',
                                             'library',
                                             'docNumber',
                                             'xml',
                                             'epublication',
                                             'semantic_info'])):
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
        epublication (namedtuple, default None): Parsed :attr:`.xml` to
                     :class:`.EPublication` structure.
        semantic_info (namedtuple, default None): Export progress informations
                      from :attr:`.xml` attribute represented as
                      :class:`.SemanticInfo` structure.

    Note:
        :attr:`semantic_info` and :attr:`epublication` attributes are parsed
        automatically from :attr:`xml` if not provided by user.
    """
    def __new__(cls, base, library, docNumber, xml, epublication=None,
                semantic_info=None):
        if xml.strip():
            parsed = xml
            if not isinstance(parsed, MARCXMLRecord):  # caching
                parsed = MARCXMLRecord(str(parsed))

            if not semantic_info:
                semantic_info = SemanticInfo.from_xml(parsed)

            if not epublication:
                epublication = EPublication.from_xml(parsed)

        return super(AlephRecord, cls).__new__(
            cls,
            base,
            library,
            docNumber,
            str(xml),
            epublication,
            semantic_info
        )
