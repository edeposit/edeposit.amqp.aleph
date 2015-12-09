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

from epublication import EPublication
from semanticinfo import SemanticInfo

from eperiodical import EPeriodical
from eperiodical_semantic_info import EPeriodicalSemanticInfo


# Structures ==================================================================
class AlephRecord(namedtuple("AlephRecord", ['base',
                                             'library',
                                             'docNumber',
                                             'xml',
                                             'parsed_info',
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
        parsed (namedtuple, default None): Parsed :attr:`.xml` to
            :class:`.EPublication` structure in case of monographic / multimono
            publications, or :class:`.EPeriodical` in case of series.
        semantic_info (namedtuple, default None): Export progress informations
            from :attr:`.xml` attribute represented as :class:`.SemanticInfo`
            structure in case of monographic / multimono publications, or
            :class:`.EPeriodicalSemanticInfo` in case of series.

    Note:
        :attr:`semantic_info` and :attr:`parsed` attributes are parsed
        automatically from :attr:`xml` if not provided by user.
    """
    def __new__(cls, base, library, docNumber, xml, parsed_info=None,
                semantic_info=None):
        if xml.strip():
            parsed = xml
            if not isinstance(parsed, MARCXMLRecord):  # caching
                parsed = MARCXMLRecord(str(parsed))

            if not semantic_info:
                if parsed.is_continuing():
                    semantic_info = EPeriodicalSemanticInfo.from_xml(parsed)
                else:
                    semantic_info = SemanticInfo.from_xml(parsed)

            if not parsed_info:
                if parsed.is_continuing():
                    parsed_info = EPeriodical.from_xml(parsed)
                else:
                    parsed_info = EPublication.from_xml(parsed)

        return super(AlephRecord, cls).__new__(
            cls,
            base=base,
            library=library,
            docNumber=docNumber,
            xml=str(xml),
            parsed_info=parsed_info,
            semantic_info=semantic_info,
        )
