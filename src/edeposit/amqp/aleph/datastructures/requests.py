#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
Request structures, on which :func:`aleph.reactToAMQPMessage` reacts.

All strucutures defined here are simple dataholders, based on `namedtuple`.
"""
from collections import namedtuple


class CountRequest(namedtuple("CountRequest", ["query"])):
    """
    Put one of the Queries to .query property and result will be just the
    number of records, instead of records itself.

    This helps to save some of Aleph resources (yeah, it is restricted to give
    too much queries by license).

    Attributes:
        query (Query object): GenericQuery, ISBNQuery, .. (Any)Query structure
              defined in :class:`aleph` module.

    See Also:
        :func:`aleph.reactToAMQPMessage` returns
        :class:`aleph.datastructures.results.CountResult` as response.
    """
    pass


class SearchRequest(namedtuple("SearchRequest", ['query'])):
    """
    Perform search in Aleph with given `query`.

    Attributes:
        query (Query object): GenericQuery, ISBNQuery, .. (Any)Query structure
              defined in :class:`aleph` module.

    See Also:
        :func:`aleph.reactToAMQPMessage` returns
        :class:`aleph.datastructures.results.SearchResult` as response.
    """
    pass


class ISBNValidationRequest(namedtuple("ISBNValidationRequest", ['ISBN'])):
    """
    Validate given ISBN.

    Attributes:
        ISBN (str): ISBN, which will be validated.

    See Also:
        :func:`aleph.reactToAMQPMessage` returns
        :class:`aleph.datastructures.results.ISBNValidationResult` as response.
    """
    pass


class ExportRequest(namedtuple("AlephExport", ['epublication'])):
    """
    Request to export data to Aleph.

    Attributes:
        epublication: :class:`aleph.datastructures.epublication.EPublication`
                      structure, which will be exported to Aleph

    Warning:
        `ISBN`, `nazev`, `Místo vydání`, `Měsíc a rok vydání`, `Pořadí vydání`,
        `Zpracovatel záznamu`, `vazba/forma`, `Formát (poze pro epublikace)`
        and `Nakladatel` has to be present, or AssertionError will be thrown.

        ISBN has to be valid, or request will be rejected with ExportException.

    See Also:
        :func:`aleph.reactToAMQPMessage` returns
        :class:`aleph.datastructures.results.ExportResult` as response.
    """
    pass
