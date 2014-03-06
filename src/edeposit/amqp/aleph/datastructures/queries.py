#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple


# Datatypes for searching in Aleph ############################################
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


class ISBNValidationResult(namedtuple("ISBNValidationResult", ["is_valid"])):
    """
    Response to ISBNValidationRequest.

    is_valid -- bool
    """
    pass


class AlephRecord(namedtuple("AlephRecord", ['base',
                                             'library',
                                             'docNumber',
                                             'xml',
                                             'epublication'])):
    """
    This structure is returned as response to SearchRequest inside
    SearchResult.

    base -- from which base was this record pulled
    library -- library string, used for downloading documents from Aleph when
               you know proper docNumber
    docNumber -- identificator in Aleph. It is not that much unique as it could
                 be, but with .library string, you can fetch documents from
                 Aleph if you know this.
    xml -- MARC XML source returned from Aleph. Quite complicated stuff.
    epublication -- parsed .xml to EPublication structure
    """
    pass


class SearchResult(namedtuple("SearchResult", ['records'])):
    """
    This is response structure, which is sent back when SearchRequest is
    received.

    records -- array of AlephRecord structures
    """
    pass


class CountResult(namedtuple("CountResult", ['num_of_records'])):
    """
    This is returned back to client when he send CountRequest.
    """
    pass
