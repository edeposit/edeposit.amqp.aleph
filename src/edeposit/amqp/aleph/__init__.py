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
GenericQuery   ----|                                 |
                   |                                 |--> SearchResult
                   V                                 |        `- AlephRecord
         Count/SearchRequest                         |
                   |                                 |
                   |                                 |
              serialize()                      deserialize()
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


import aleph
import convertors


# Datatypes for searching in Aleph ############################################
class CountRequest(namedtuple("CountRequest", ["query"])):
    """
    Put one of the Queries to .query property and it will return just
    number of records, instead of records itself.

    This help to saves some of Aleph resources (yeah, it is restricted to give
    too much queries by license).

    query -- GenericQuery, ISBNQuery, .. *Query structures in this module
    """
    pass


class SearchRequest(namedtuple("SearchRequest", ['query'])):
    """
    query -- GenericQuery, ISBNQuery, .. *Query structures in this module
    """
    pass


class AlephRecord(namedtuple("AlephRecord", ['library',
                                             'docNumber',
                                             'xml',
                                             'epublication'])):
    """
    This structure is returned as response to SearchRequest inside
    SearchResult.

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


class _QueryTemplate:
    """
    This class is here to just save some effort by using common ancestor with
    same .getSearchResult() and .getCountResult() definition.

    You probably shouldn't use it.
    """
    def getSearchResult(self):
        records = []
        for doc_id, library in self._getIDs():
            xml = aleph.downloadAlephDocument(doc_id, library)

            records.append(
                AlephRecord(
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
          some books also have two or more ISBNs.
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


class PublisherQuery(namedtuple("PublisherQuery", ["publisher"]), _QueryTemplate):
    def _getIDs(self):
        return aleph.getPublishersBooksIDs(self.publisher)

    def _getCount(self):
        return aleph.getPublishersBooksCount(self.publisher)


###############################################################################
# Add new record to Aleph #####################################################
# TODO: implement exports
#
class Author(namedtuple("Author", ['firstName', 'lastName', 'title'])):
    pass


class Producent(namedtuple("Producent", ['title',
                                         'phone',
                                         'fax',
                                         'email',
                                         'url',
                                         'identificator',
                                         'ico'])):
    pass


class EPublication(namedtuple("EPublication", ['nazev',
                                               'podnazev',
                                               'vazba',
                                               'cena',
                                               'castDil',
                                               'nazevCasti',
                                               'nakladatelVydavatel',
                                               'datumVydani',
                                               'poradiVydani',
                                               'zpracovatelZaznamu',
                                               'kategorieProRIV',
                                               'mistoDistribuce',
                                               'distributor',
                                               'datumDistribuce',
                                               'datumProCopyright',
                                               'format',
                                               'url',
                                               'mistoVydani',
                                               'ISBNSouboruPublikaci',
                                               'autori',
                                               'originaly'])):
    """
    This structure is returned as result of users SearchRequest. It will be
    also used in exporting new data to aleph, but that is not implemented yet.

    In case of Search/Count requests, this structure is filled with data from
    MARC XML record parsed by marcxml.py.
    """
    pass


class OriginalFile(namedtuple("OriginalFile", ['url',
                                               'format',
                                               'file',
                                               'isbns'])):
    """ type of isbn: ISBN"""
    pass


## Export protocol query wrappers #############################################
class ExportRequest(namedtuple("AlephExport", ['epublication',
                                               'linkOfEPublication'])):
    """
    epublication -- type of EPublication
    linkOfEPublication -- url of epublication
    """
    pass


class ExportResult(namedtuple("AlephExportResult", ['docNumber',
                                                    'base',
                                                    'xml',
                                                    'success',
                                                    'message'])):
    """
    docNumber -- docNumber of a record in Aleph
    base      --      base of Aleph
    success   --   whether import was successful
    message   --   message of error or success
    """
    pass


# Interface for an external world #############################################

# Variables ###################################################################
QUERY_TYPES = [
    ISBNQuery,
    AuthorQuery,
    PublisherQuery,
    GenericQuery
]

REQUEST_TYPES = [
    SearchRequest,
    CountRequest,
    ExportRequest
]


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


# Functions ###################################################################
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
    req = deserialize(message)

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
    else:
        raise ValueError(
            "Unknown type of request: '" + str(type(req)) + "' or query: '" +
            str(type(req.query)) + "'!"
        )

    if response is not None:
        return response_callback(serialize(response), UUID)
