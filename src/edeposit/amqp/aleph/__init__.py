#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Query workflow
==============

To query Aleph, just create one of the Queries - :class:`ISBNQuery` for example
and put it into :class:`aleph.datastructures.requests.SearchRequest` wrapper
and send the message to the Aleph's exchange::

    isbnq = ISBNQuery("80-251-0225-4")
    request = SearchRequest(isbnq)

    amqp.send(
        message    = serialize(request),
        properties = "..",
        exchange   = "ALEPH'S_EXCHANGE"
    )

and you will get back AMQP message with SearchResult.

Note:
    You don't have to import all structures from :class:`datastructures`, they
    should be automatically imported and made global in ``__init__.py``.

If you want to just get count of how many items is there in Aleph, just wrap
the ISBNQuery with :class:`CountRequest`::

    isbnq = ISBNQuery("80-251-0225-4")
    request = CountRequest(isbnq)

    # rest is same..

and you will get back :class:`aleph.datastructures.results.CountResult`.

Note:
    You should always use CountRequest instead of just calling ``len()`` to
    SearchResult.records - it doesn't put that much load to Aleph. Also Aleph
    is restricted to 150 requests per second.

Here is ASCII flow diagram for you::

 ISBNQuery      ----.                                 ,--> CountResult
 AuthorQuery    ----|                                 |       `- num_of_records
 PublisherQuery ----|          ExportRequest          |
 GenericQuery   ----|      ISBNValidationRequest      |--> SearchResult
                    |                |                |       `- AlephRecord
                    V                |                |
       Count/Search/ExportRequest    |                |--> ISBNValidationResult
                    |                |                |        - ISBN
                    V                |                |
                    |                |                |--> ExportResult
                    V                |                |
               serialize()<----------'           deserialize()
                    |                                 ^
                    V             Client              |
               AMQPMessage ------> AMQP -------> AMQPMessage
                                  |    ^
                                  V    |
                                  |    ^
                                  V    |
                                  |    ^
                                  V    |
               AMQPMessage <------ AMQP <-------- AMQPMessage
                    |             Service              ^
                    |                                  |
                    V                                  |
           reactToAMQPMessage() ............... magic_happens()

Neat, isn't it?

AQMP is handled by `edeposit.amqp <http://edeposit-amqp.readthedocs.org>`_
module, edeposit.aqmp.aleph provides just datastructures and
:func:`reactToAMQPMessage`.
"""
#= Imports ====================================================================
from collections import namedtuple


import isbn
import aleph
import export
import settings
import convertor
from datastructures import *


#= Queries ====================================================================
class _QueryTemplate:
    """
    This class is here to just save some effort by using common ancestor with
    same .getSearchResult() and .getCountResult() definition.

    You probably shouldn't use it.
    """
    def getSearchResult(self):
        records = []
        for doc_id, library, base in self._getIDs():
            xml = aleph.downloadMARCXML(doc_id, library)

            records.append(
                AlephRecord(
                    base,
                    library,
                    doc_id,
                    xml,
                    convertor.toEPublication(xml)
                )
            )

        return SearchResult(records)

    def getCountResult(self):
        return CountResult(self._getCount())


class GenericQuery(namedtuple("GenericQuery", ['base',
                                               'phrase',
                                               'considerSimilar',
                                               'field']),
                   _QueryTemplate):
    """
    Used for generic queries to aleph.

    Args:
        base (str)
        phrase (str)
        considerSimilar (bool)
        field (str)

    For details of base/phrase/.. parameters, see :func:`aleph.searchInAleph`.
    All parameters also serves as properties.

    This is used mainly if you want to search by your own parameters and don't
    want to use prepared wrappers (:class:`AuthorQuery`/:class:`ISBNQuery`/..).
    """
    def _getIDs(self):
        return aleph.getDocumentIDs(
            aleph.searchInAleph(
                self.base,
                self.phrase,
                self.considerSimilar,
                self.field
            )
        )

    def _getCount(self):
        return aleph.searchInAleph(
            self.base,
            self.phrase,
            self.considerSimilar,
            self.field
        )["no_entries"]


class ISBNQuery(namedtuple("ISBNQuery", ["ISBN", "base"]), _QueryTemplate):
    """
    Query Aleph to get books by ISBN.

    Args:
        ISBN (str)
        base (str, optional): if not set, ``settings.ALEPH_DEFAULT_BASE`` is
                              used

    Note:
        ISBN is not unique, so you can get back lot of books with same ISBN.
        Some books also have two or more ISBNs.
    """
    def __new__(self, ISBN, base=settings.ALEPH_DEFAULT_BASE):
        return super(ISBNQuery, self).__new__(self, ISBN, base)

    def _getIDs(self):
        return aleph.getISBNsIDs(self.ISBN, base=self.base)

    def _getCount(self):
        return aleph.getISBNCount(self.ISBN, base=self.base)


class AuthorQuery(namedtuple("AuthorQuery", ["author", "base"]),
                  _QueryTemplate):
    """
    Query Aleph to get books by Author.

    Args:
        author (str): Author's name/lastname in UTF
        base (str, optional): if not set, ``settings.ALEPH_DEFAULT_BASE`` is
                              used

    """
    def __new__(self, author, base=settings.ALEPH_DEFAULT_BASE):
        return super(AuthorQuery, self).__new__(self, author, base)

    def _getIDs(self):
        return aleph.getAuthorsBooksIDs(self.author, base=self.base)

    def _getCount(self):
        return aleph.getAuthorsBooksCount(self.author, base=self.base)


class PublisherQuery(namedtuple("PublisherQuery", ["publisher", "base"]),
                     _QueryTemplate):
    """
    Query Aleph to get books by Publisher.

    Args:
        publisher (str): publisher's name in UTF
        base (str, optional): if not set, ``settings.ALEPH_DEFAULT_BASE`` is
                              used

    """
    def __new__(self, publisher, base=settings.ALEPH_DEFAULT_BASE):
        return super(PublisherQuery, self).__new__(self, publisher, base)

    def _getIDs(self):
        return aleph.getPublishersBooksIDs(self.publisher, base=self.base)

    def _getCount(self):
        return aleph.getPublishersBooksCount(self.publisher, base=self.base)


#= Variables ==================================================================
QUERY_TYPES = [
    ISBNQuery,
    AuthorQuery,
    PublisherQuery,
    GenericQuery
]

REQUEST_TYPES = [
    SearchRequest,
    CountRequest,
    ExportRequest,
    ISBNValidationRequest
]


#= Interface for an external world ============================================
def _iiOfAny(instance, classes):
    """
    Returns true, if `instance` is instance of any (_iiOfAny) of the `classes`.

    This function doesn't use isinstance() check, it just compares the
    classnames.

    This can be generaly dangerous, but it is really useful when you are
    comparing class serialized in one module and deserialized in another.

    This causes, that module paths in class internals are different and
    isinstance() and type() comparsions thus fails.

    Use this function instead, if you wan't to check what type is your
    deserialized message.

    Args:
        instance (object): class instance you want to know the type
        classes (list): classes, or just the class you want to compare - func
                        automatically converts nonlist/nontuple parameters to
                        list

    Returns:
        bool: True if `instance` is instance of any of the `classes`.
    """
    if type(classes) not in [list, tuple]:
        classes = [classes]

    return any(map(lambda x: type(instance).__name__ == x.__name__, classes))


#= Functions ==================================================================
def reactToAMQPMessage(req, UUID):
    """
    React to given (AMQP) message. Return data thru given callback function.

    Args:
        req (Request class): any of the Request class from
                             :class:`aleph.datastructures.requests`
        UUID (str): unique ID of received message

    Returns:
        result of search in Aleph.

    Raises:
        ValueError: if bad type of `req` structure is given.
    """
    # TODO: pridat podporu exportnich typu
    if not _iiOfAny(req, REQUEST_TYPES):
        raise ValueError(
            "Unknown type of request: '" + str(type(req)) + "'!"
        )

    if _iiOfAny(req, CountRequest) and _iiOfAny(req.query, QUERY_TYPES):
        return req.query.getCountResult()
    elif _iiOfAny(req, SearchRequest) and _iiOfAny(req.query, QUERY_TYPES):
        return req.query.getSearchResult()
    elif _iiOfAny(req, ISBNValidationRequest):
        return ISBNValidationResult(isbn.is_valid_isbn(req.ISBN))
    elif _iiOfAny(req, ExportRequest):
        export.exportEPublication(req.epublication)
        return ExportResult(req.epublication.ISBN)

    raise ValueError(
        "Unknown type of request: '" + str(type(req)) + "' or query: '" +
        str(type(req.query)) + "'!"
    )
