#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple


class CountRequest(namedtuple("CountRequest", ["query"])):
    """
    Put one of the Queries to .query property and it will return just
    number of records, instead of records itself.

    This help to saves some of Aleph resources (yeah, it is restricted to give
    too much queries by license).

    query -- GenericQuery, ISBNQuery, .. *Query structures in this module

    reactToAMQPMessage() returns CountResult as response.
    """
    pass


class SearchRequest(namedtuple("SearchRequest", ['query'])):
    """
    Perform search in Aleph with given query.

    query -- GenericQuery, ISBNQuery, .. *Query structures in this module

    reactToAMQPMessage() returns SearchResult as response.
    """
    pass


class ISBNValidationRequest(namedtuple("ISBNValidationRequest", ['ISBN'])):
    """
    Validate given ISBN.

    reactToAMQPMessage() returns ISBNValidationResult as response.
    """
    pass


class ExportRequest(namedtuple("AlephExport", ['epublication'])):
    """
    Request to export data to Aleph.

    ISBN, nazev, Místo vydání, Měsíc a rok vydání, Pořadí vydání, Zpracovatel
    záznamu, vazba/forma, Formát (poze pro epublikace), Nakladatel has to be
    present, or AssertionError will be thrown. ISBN has to be valid, or
    request will be rejected with ExportException.

    epublication -- EPublication structure, which will be exported to Aleph
    """
    pass
