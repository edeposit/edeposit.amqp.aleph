#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Query workflow
==============

AQMP is handled by `edeposit.amqp <http://edeposit-amqp.readthedocs.org>`_
module, this package provides just datastructures and
:func:`reactToAMQPMessage` function, which is used in daemon to translate
highlevel requests to lowlevel queries to Aleph's webapi.

AMQP query
----------
To query Aleph thru AMQP, run :class:`.edeposit_amqp_alephdaemon` (from
:mod:`edeposit.amqp` package) and  create one of the Queries -
:class:`ISBNQuery` for example and put it into :class:`.SearchRequest` wrapper
and send the message to the Aleph's exchange::

    request = SearchRequest(
        ISBNQuery("80-251-0225-4")
    )

    amqp.send(  # you can use pika library to send data to AMQP queue
        message    = serialize(request),
        properties = "..",
        exchange   = "ALEPH'S_EXCHANGE"
    )

and you will get back AMQP message with :class:`.SearchResult`.

Note:
    You don't have to import all structures from :class:`datastructures`, they
    should be automatically imported and made global in ``__init__.py``.

Count requests
--------------
If you want to just get count of how many items is there in Aleph, just wrap
the :class:`.ISBNQuery` with :class:`.CountRequest` class::

    isbnq = ISBNQuery("80-251-0225-4")
    request = CountRequest(isbnq)

    # rest is same..

and you will get back :class:`.CountResult`.

Note:
    You should always use :class:`.CountRequest` instead of just calling
    :py:func:`len()` to :attr:`.SearchResult.records` - it doesn't put that
    much load to Aleph. Also Aleph is restricted to 150 requests per second.

Direct queries
--------------
As I said, this module provides only direct access to Aleph, AMQP communication
is handled in :mod:`edeposit.amqp`.

If you want to access module directly, you can use :func:`reactToAMQPMessage`
wrapper, or query :mod:`aleph <aleph.aleph>` submodule directly.

:func:`reactToAMQPMessage` is preferred, because in that case, you don't have
to deal with Aleph lowlevel API, which can be little bit annoying.

Diagrams
--------
Here is ASCII flow diagram for you::

 ISBNQuery      ----.                                 ,--> CountResult
 AuthorQuery    ----|                                 |       `- num_of_records
 PublisherQuery ----|                                 |
 TitleQuery     ----|          ExportRequest          |--> SearchResult
 GenericQuery   ----|      ISBNValidationRequest      |       `- AlephRecord
 DocumentQuery  ----|                |                |
 ICZQuery       ----|                |                |--> ISBNValidationResult
                    |                |                |        - ISBN
                    V                |                |
       Count/Search/ExportRequest    |                |--> ExportResult
                    |                |                |
                    |                |                |
                    |                |                |
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

and here is (pseudo) UML:

.. image:: /_static/reactoamqpmessage.png

Neat, isn't it?

API
---
"""
# Imports =====================================================================
from collections import namedtuple

import isbn_validator

import aleph
import export
import settings
import doc_number
from datastructures import *


# Queries =====================================================================
class _QueryTemplate(object):
    """
    This class is here to just save some effort by using common ancestor with
    same .getSearchResult() and .getCountResult() definition.

    You probably shouldn't use it.
    """
    def getSearchResult(self):
        records = []
        for xml in self._getXML():
            records.append(
                AlephRecord(
                    base=self.base,
                    library=settings.DEFAULT_LIBRARY,
                    docNumber=doc_number.getDocNumber(xml),
                    xml=xml
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
    Used for generic queries to Aleph.

    Args:
        base (str): Which base in Aleph will be queried. This depends on
                    settings of your server. See :func:`aleph.getListOfBases`
                    for details.
        phrase (str): What are you looking for.
        considerSimilar (bool): Don't use this, it usually doesn't work.
        field (str): Which field you want to use for search.
                     See :attr:`aleph.VALID_ALEPH_FIELDS` for list of valid
                     bases.

    For details of base/phrase/.. parameters, see :func:`aleph.searchInAleph`.
    All parameters also serves as properties.

    This is used mainly if you want to search by your own parameters and don't
    want to use prepared wrappers (:class:`AuthorQuery`/:class:`ISBNQuery`/..).
    """
    def _getXML(self):
        return aleph.downloadRecords(
            aleph.searchInAleph(
                self.base,
                self.phrase,
                self.considerSimilar,
                self.field,
            )
        )

    def _getCount(self):
        return aleph.searchInAleph(
            self.base,
            self.phrase,
            self.considerSimilar,
            self.field
        )["no_entries"]


class DocumentQuery(namedtuple("DocumentQuery", ["doc_id", "library"])):
    """
    Query Aleph when you know the Document ID.

    Args:
        doc_id (str): ID number as string.
        library (str, default settings.DEFAULT_LIBRARY): Library.
    """
    def __new__(cls, doc_id, library=settings.DEFAULT_LIBRARY):
        return super(DocumentQuery, cls).__new__(
            cls,
            doc_id,
            library
        )

    def getSearchResult(self):
        """
        Returns:
            object: :class:`SearchResult` document with given `doc_id`.

        Raises:
            aleph.DocumentNotFoundException: When document is not found.
        """
        xml = aleph.downloadMARCOAI(self.doc_id, self.library)

        return SearchResult([
            AlephRecord(
                None,
                self.library,
                self.doc_id,
                xml
            )
        ])

    def getCountResult(self):
        """
        Returns:
            int: 0/1 whether the document is found or not.
        """
        try:
            self.getSearchResult()
        except aleph.DocumentNotFoundException:
            return 0

        return 1


class ISBNQuery(namedtuple("ISBNQuery", ["ISBN", "base"]), _QueryTemplate):
    """
    Used to query Aleph to get books by ISBN.

    Args:
        ISBN (str): ISBN 10/13.
        base (str, optional): If not set, :attr:`settings.ALEPH_DEFAULT_BASE`
                              is used.

    Note:
        ISBN is not unique, so you can get back lot of books with same ISBN.
        Some books also have two or more ISBNs.
    """
    def __new__(self, ISBN, base=settings.ALEPH_DEFAULT_BASE):
        return super(ISBNQuery, self).__new__(self, ISBN, base)

    def _getXML(self):
        return aleph.getISBNsXML(self.ISBN, base=self.base)

    def _getCount(self):
        return aleph.getISBNCount(self.ISBN, base=self.base)


class AuthorQuery(namedtuple("AuthorQuery", ["author", "base"]),
                  _QueryTemplate):
    """
    Used to query Aleph to get books by Author.

    Args:
        author (str): Author's name/lastname in UTF-8.
        base (str, optional): If not set, :attr:`settings.ALEPH_DEFAULT_BASE`
                              is used.
    """
    def __new__(self, author, base=settings.ALEPH_DEFAULT_BASE):
        return super(AuthorQuery, self).__new__(self, author, base)

    def _getXML(self):
        return aleph.getAuthorsBooksXML(self.author, base=self.base)

    def _getCount(self):
        return aleph.getAuthorsBooksCount(self.author, base=self.base)


class PublisherQuery(namedtuple("PublisherQuery", ["publisher", "base"]),
                     _QueryTemplate):
    """
    Used to query Aleph to get books by Publisher.

    Args:
        publisher (str): Publisher's name in UTF-8.
        base (str, optional): If not set, :attr:`settings.ALEPH_DEFAULT_BASE`
                              is used.
    """
    def __new__(self, publisher, base=settings.ALEPH_DEFAULT_BASE):
        return super(PublisherQuery, self).__new__(self, publisher, base)

    def _getXML(self):
        return aleph.getPublishersBooksXML(self.publisher, base=self.base)

    def _getCount(self):
        return aleph.getPublishersBooksCount(self.publisher, base=self.base)


class TitleQuery(_QueryTemplate,
                 namedtuple("TitleQuery", ["title", "base"])):
    """
    Used to query Aleph to get books by book's title/name.

    Args:
        title (str): Book's title in UTF-8.
        base (str, optional): If not set, :attr:`settings.ALEPH_DEFAULT_BASE`
                              is used.
    """
    def __new__(self, title, base=settings.ALEPH_DEFAULT_BASE):
        return super(TitleQuery, self).__new__(self, title, base)

    def _getXML(self):
        return aleph.getBooksTitleXML(self.title, base=self.base)

    def _getCount(self):
        return aleph.getBooksTitleCount(self.title, base=self.base)


class ICZQuery(_QueryTemplate, namedtuple("ICZQuery", ["icz", "base"])):
    """
    Used to query Aleph to get books by record's identification number `icz`.

    Args:
        icz (str): Identification number (``nkc20150003029`` for example).
        base (str, optional): If not set, :attr:`settings.ALEPH_DEFAULT_BASE`
                              is used.
    """
    def __new__(self, icz, base=settings.ALEPH_DEFAULT_BASE):
        return super(ICZQuery, self).__new__(self, icz, base)

    def _getXML(self):
        return aleph.getICZBooksXML(self.icz, base=self.base)

    def _getCount(self):
        return aleph.getICZBooksCount(self.icz, base=self.base)


# Variables ===================================================================
QUERY_TYPES = [
    ISBNQuery,
    AuthorQuery,
    PublisherQuery,
    TitleQuery,
    GenericQuery,
    DocumentQuery,
    ICZQuery,
]

REQUEST_TYPES = [
    SearchRequest,
    CountRequest,
    ExportRequest,
    ISBNValidationRequest,
]


# Interface for an external world =============================================
def _iiOfAny(instance, classes):
    """
    Returns true, if `instance` is instance of any (_iiOfAny) of the `classes`.

    This function doesn't use :func:`isinstance` check, it just compares the
    class names.

    This can be generally dangerous, but it is really useful when you are
    comparing class serialized in one module and deserialized in another.

    This causes, that module paths in class internals are different and
    :func:`isinstance` and :func:`type` comparsions thus fails.

    Use this function instead, if you want to check what type is your
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


# Functions ===================================================================
def reactToAMQPMessage(req, send_back):
    """
    React to given (AMQP) message.

    This function is used by :mod:`edeposit.amqp.alephdaemon`. It works as
    highlevel wrapper for whole module.

    Example:
        >>> import aleph

        >>> request = aleph.SearchRequest(
        ...     aleph.ISBNQuery("80-251-0225-4")
        ... )
        >>> request
        SearchRequest(query=ISBNQuery(ISBN='80-251-0225-4', base='nkc'))

        >>> response = aleph.reactToAMQPMessage(request, None)

        >>> response  # formated by hand for purposes of example
        SearchResult(
            records=[
                AlephRecord(
                    base='nkc',
                    library='NKC01',
                    docNumber=1492461,
                    xml='HERE IS WHOLE MARC OAI RECORD',
                    epublication=EPublication(
                        ISBN=['80-251-0225-4'],
                        nazev='Umění programování v UNIXu /',
                        podnazev='',
                        vazba='(bro\xc5\xbe.) :',
                        cena='K\xc4\x8d 590,00',
                        castDil='',
                        nazevCasti='',
                        nakladatelVydavatel='Computer Press,',
                        datumVydani='2004',
                        poradiVydani='1. vyd.',
                        zpracovatelZaznamu='BOA001',
                        format='23 cm',
                        url='',
                        mistoVydani='Brno :',
                        ISBNSouboruPublikaci=[],
                        autori=[
                            Author(
                                firstName='Eric S.',
                                lastName='Raymond',
                                title=''
                            )
                        ],
                        originaly=[
                            'Art of UNIX programming'
                        ],
                        internal_url=''
                    )
                )
            ]
        )

    Args:
        req (Request class): Any of the Request class from
                          :class:`aleph.datastructures.requests`.
        send_back (fn reference): Reference to function for responding. This is
                  useful for progress monitoring for example. Function takes
                  one parameter, which may be response structure/namedtuple, or
                  string or whatever would be normally returned.

    Returns:
        Result class: Result of search in Aleph. \
                      See :mod:`aleph.datastructures.results` submodule.

    Raises:
        ValueError: If bad type of `req` structure is given.
    """
    if not _iiOfAny(req, REQUEST_TYPES):
        raise ValueError(
            "Unknown type of request: '" + str(type(req)) + "'!"
        )

    if _iiOfAny(req, CountRequest) and _iiOfAny(req.query, QUERY_TYPES):
        return req.query.getCountResult()

    elif _iiOfAny(req, SearchRequest) and _iiOfAny(req.query, QUERY_TYPES):
        return req.query.getSearchResult()

    elif _iiOfAny(req, ISBNValidationRequest):
        ISBN = req.ISBN

        if _iiOfAny(ISBN, ISBNQuery):
            ISBN = ISBN.ISBN

        return ISBNValidationResult(isbn_validator.is_valid_isbn(ISBN))

    elif _iiOfAny(req, ExportRequest):
        export.exportEPublication(req.epublication)
        return ExportResult(req.epublication.ISBN)

    raise ValueError(
        "Unknown type of request: '" + str(type(req)) + "' or query: '" +
        str(type(req.query)) + "'!"
    )
