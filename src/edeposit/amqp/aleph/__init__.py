#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Workflow is pretty simple:

To query Aleph, just create one of the Queries - ISBNQuery for example and put
it into SearchRequest wrapper with UUID. Then encode it by calling
toAMQPMessage() and send the message to the Aleph exchange.

---
isbnq = ISBNQuery("80-251-0225-4")
request = SearchRequest(isbnq, UUID)

amqp.send(
    toAMQPMessage(request)
    "ALEPH'S_EXCHANGE"
)
---

and you will get back AMQP message, and after decoding with fromAMQPMessage()
also SearchResult.

If you want to just get count of how many items is there in Aleph (you should
use this instead of just calling len() to SearchResult.records - it doesn't put
that much load to Aleph), just wrap the ISBNQuery with CountRequest:

---
isbnq = CountRequest(ISBNQuery("80-251-0225-4"))
# rest is same..
---

and you will get back (after decoding) CountResult.
"""
#= Imports ====================================================================
from collections import namedtuple


import aleph
import convertors


# from .. import AMQPMessage
class AMQPMessage(namedtuple('AMQPMessage',  # TODO: Remove
                             ['data',
                              'headers',
                              'properties'
                              ])):
    """
    data ... serialized main message
    headers
    """
    pass


# Datatypes for searching in Aleph ############################################
class CountRequest(namedtuple("CountRequest", ["query", "UUID"])):
    """
    Put one of the Queries to .query property and it will return just
    number of records, instead of records itself.

    This help to saves some of Aleph resources (yeah, it is restricted to give
    too much queries by licence).

    query -- GenericQuery, ISBNQuery, .. *Query structures in this module
    UUID -- identification of a query, it will be send back in response
            structure for user to be able to pair Request/Response
    """
    pass


class SearchRequest(namedtuple("SearchRequest",
                               ['query',
                                'UUID'])):
    """
    query -- GenericQuery, ISBNQuery, .. *Query structures in this module
    UUID -- identification of a query, will be send back in response structure
    """
    pass


class AlephRecord(namedtuple("AlephRecord",
                             ['library',
                              'docNumber',
                              'xml',
                              'epublication'])):
    """
    This structure is returned as reponse to SearchRequest inside SearchResult.

    library -- library string, used for downloading documents from Aleph when
               you know proper docNumber
    docNumber -- identificator in Aleph. It is not that much unique as it could
                 be, but with .library string, you can fetch documents from
                 Aleph if you know this.
    xml -- MARC XML source returned from Aleph. Quite complicated stuff.
    epublication -- parsed .xml to EPublication structure
    """
    pass


class SearchResult(namedtuple("SearchResult", ['records', 'UUID'])):
    """
    This is response structure, which is sent back when SearchRequest is
    received.

    records -- array of AlephRecord structures
    UUID -- UUID which is used from SearchRequest.UUID
    """
    pass


class CountResult(namedtuple("CountResult",
                             ['num_of_records',
                              'UUID'])):
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
    def getSearchResult(self, UUID):
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

        return SearchResult(records, UUID)

    def getCountResult(self, UUID):
        return CountResult(
            self._getCount(),
            UUID
        )


class GenericQuery(namedtuple("GenericQuery",
                              ['base',
                               'phrase',
                               'considerSimilar',
                               'field']), _QueryTemplate):
    """
    Used for generic queries to aleph.

    For details of base/phrase/.. parameters, see aleph.py : searchInAleph().
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
class Author(namedtuple("Author", ['firstName', 'lastName', 'title'])):
    pass


class Producent(namedtuple("Producent",
                           ['title',
                            'phone',
                            'fax',
                            'email',
                            'url',
                            'identificator',
                            'ico'])):
    pass


class EPublication(namedtuple("EPublication",
                              ['nazev',
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
    see https://e-deposit.readthedocs.org/cs/latest/dm01.html
    """
    pass


class OriginalFile(namedtuple("OriginalFile",
                              ['url', 'format', 'file', 'isbns'])):
    """ type of isbn: ISBN"""
    pass


## Export protocol query wrappers #############################################
class AlephExport(namedtuple("AlephExport",
                             ['epublication',
                              'linkOfEPublication'])):
    """ epublication ... type of EPublication
    linkOfEPublication  ... url with epublication

    User will fill this record.
    """
    pass


class ExportRequest(namedtuple("ExportRequest",
                               ['export',
                                'UUID'])):
    pass


class AlephExportResult(namedtuple("AlephExportResult",
                                   ['docNumber',
                                    'base',
                                    'xml',
                                    'success',
                                    'message'])):
    """ docNumber ... docNumber of a record in Aleph
    base      ... base of Aleph
    success   ... whether import was successfull
    message   ... message of error or success
    """
    pass


class ExportResult(namedtuple("ExportResult",
                              ['result',
                               'UUID'])):
    """
    ... result is type of AlephExportResult
    ... UUID is UUID used in ExportRequest
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


# Functions ###################################################################
def toAMQPMessage(request):
    """
    Serialize nested structure of objects defined in this module into
    AMQPMessage.

    request -- tree consisting of namedtuples and other python datatypes

    Return AMQPMessage with filled .body property with serialized data.
    """
    return AMQPMessage(
        data=convertors.toJSON(request),
        headers="",
        properties=""
    )


def fromAMQPMessage(message):
    """
    Deserialize structures defined in this module from AMQPMessage.

    message -- AMQPMessage, in which .body property is expected to be
               serialized data.

    Returns nested structure of Requests/Results (see other objects defined
    here).
    """
    return convertors.fromJSON(message.body)


def reactToAMQPMessage(message, response_callback):
    """
    React to given AMQPMessage. Return data thru given callback function.

    message -- AMQPMessage instance.
    response_callback -- function taking exactly ONE parameter - AMQPMessage
                         with response. Function take care of sending the
                         response thru AMQP.

    Returns result of response_callback() call.

    Raise:
        ValueError if bad type of |message| structure is given.

    TODO:
        React to Export requests.
    """
    decoded = fromAMQPMessage(message)

    if type(decoded) != SearchRequest:  # TODO: pridat podporu exportnich typu
        raise ValueError("Unknown type of message: '" + type(decoded) + "'!")

    query = decoded.query

    response = None
    if type(query) == CountRequest and query.query in QUERY_TYPES:
        response = query.query.getCountResult(decoded.UUID)
    elif type(query) in QUERY_TYPES:  # react to search requests
        response = query.getSearchResult(decoded.UUID)
    else:
        raise ValueError("Unknown type of query: '" + type(query) + "'!")

    if response is not None:
        return response_callback(toAMQPMessage(response))
