#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
- Query workflow --------------------------------------------------------------

To query Aleph, just create one of the Queries - ISBNQuery for example and put
it into SearchRequest wrapper. Then encode it by calling toAMQPMessage() and
send the message to the Aleph's exchange.

---
isbnq = ISBNQuery("80-251-0225-4")
request = SearchRequest(isbnq)

amqp.send(
    message    = serialize(request),
    properties = "..",
    exchange   = "ALEPH'S_EXCHANGE"
)
---

and you will get back AMQP message, and after decoding with fromAMQPMessage()
also SearchResult.

If you want to just get count of how many items is there in Aleph, just wrap
the ISBNQuery with CountRequest (you should use this instead of just calling
len() to SearchResult.records - it doesn't put that much load to Aleph):

---
isbnq = ISBNQuery("80-251-0225-4")
request = CountRequest(isbnq)

# rest is same..
---

and you will get back (after decoding) CountResult.

Here is ASCII flow diagram for you:

ISBNQuery      ----.                                 ,--> CountResult
AuthorQuery    ----|                                 |        `- num_of_records
PublisherQuery ----|                                 |
GenericQuery   ----|      ISBNValidationRequest      |--> SearchResult
                   |                |                |        `- AlephRecord
                   V                |                |
         Count/SearchRequest        |                |--> ISBNValidationResult
                   |                |                |        `- ISBN
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

- Export workflow -------------------------------------------------------------
TODO: implement, then write docstring
"""
#= Imports ====================================================================
from collections import namedtuple


import isbn
import aleph
import export
import convertors
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
                    convertors.toEPublication(xml)
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

    For details of base/phrase/.. parameters, see aleph.py : searchInAleph().

    This is used mainly if you want to search by your own parameters and don't
    want to use prepared wrappers (AuthorQuery/ISBNQuery/..).
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


class ISBNQuery(namedtuple("ISBNQuery", ["ISBN"]), _QueryTemplate):
    """
    Query for ISBN.

    Note: ISBN is not unique, so you can get back lot of books with same ISBN.
          Some books also have two or more ISBNs.
    """
    def _getIDs(self):
        return aleph.getISBNsIDs(self.ISBN)

    def _getCount(self):
        return aleph.getISBNCount(self.ISBN)


class AuthorQuery(namedtuple("AuthorQuery", ["author"]), _QueryTemplate):
    def _getIDs(self):
        return aleph.getAuthorsBooksIDs(self.author)

    def _getCount(self):
        return aleph.getAuthorsBooksCount(self.author)


class PublisherQuery(namedtuple("PublisherQuery", ["publisher"]),
                     _QueryTemplate):
    def _getIDs(self):
        return aleph.getPublishersBooksIDs(self.publisher)

    def _getCount(self):
        return aleph.getPublishersBooksCount(self.publisher)


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
def serialize(data):
    """
    Serialize class hierarchy into JSON.
    """
    return convertors.toJSON(data)


def deserialize(data):
    """
    Deserialize classes from JSON data.
    """
    return convertors.fromJSON(data)


def iiOfAny(instance, classes):
    """
    Returns true, if `instance` is instance of any (iiOfAny) of the `classes`.

    This function doesn't use isinstance() check, it just compares the
    classnames.

    This can be generaly dangerous, but it is really useful when you are
    comparing class serialized in one module and deserialized in another.

    This causes, that module paths in class internals are different and
    isinstance() and type() comparsions thus fails.

    Use this function instead, if you wan't to check what type is your
    deserialized message.

    instance -- class instance you want to know the type
    classes -- list of classes, or just the class you want to compare - func
               automatically retypes nonlist/nontuple parameters to list
    """
    if type(classes) not in [list, tuple]:
        classes = [classes]

    return any(map(lambda x: type(instance).__name__ == x.__name__, classes))


#= Functions ==================================================================
def reactToAMQPMessage(message, response_callback, UUID):
    """
    React to given AMQPMessage. Return data thru given callback function.

    message -- message encoded in JSON by serialize()
    response_callback -- function taking exactly ONE parameter - message's body
                         with response. Function take care of sending the
                         response over AMQP.

    Returns result of response_callback() call.

    Raise:
        ValueError if bad type of `message` structure is given.

    TODO:
        React to Export requests.
    """
    req = deserialize(message) if type(message) == str else message

    # TODO: pridat podporu exportnich typu
    if not iiOfAny(req, REQUEST_TYPES):
        raise ValueError(
            "Unknown type of request: '" + str(type(req)) + "'!"
        )

    response = None
    if iiOfAny(req, CountRequest) and iiOfAny(req.query, QUERY_TYPES):
        response = req.query.getCountResult()
    elif iiOfAny(req, SearchRequest) and iiOfAny(req.query, QUERY_TYPES):
        response = req.query.getSearchResult()
    elif iiOfAny(req, ExportRequest):
        raise NotImplementedError("Not implemented yet.")
    elif iiOfAny(req, ISBNValidationRequest):
        response = ISBNValidationResult(isbn.is_valid_isbn(req.ISBN))
    elif iiOfAny(req, ExportRequest):
        export.exportEPublication(req.epublication)
        response = ExportResult(req.epublication.ISBN)
    else:
        raise ValueError(
            "Unknown type of request: '" + str(type(req)) + "' or query: '" +
            str(type(req.query)) + "'!"
        )

    if response is not None:
        return response_callback(serialize(response), UUID)
