#! /usr/bin/env python
# -*- coding: utf-8 -*-
# This package may contain traces of nuts
from collections import namedtuple

###############################################################################
# Add new record to Aleph #####################################################
###############################################################################
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


###############################################################################
# Search Aleph ################################################################
###############################################################################
class AlephQuery(namedtuple("AlephQuery",
                            ['base',
                             'phrase',
                             'considerSimilar',
                             'field'])):
    """
    base ... base in Aleph
    NKC, ...
    see:  http://aleph.nkp.cz/F/?func=file&file_name=base-list
    """
    pass


class SearchRequest(namedtuple("QueryRequest",
                              ['query',
                               'UUID'
                           ])):
    """
    UUID is used as identification of a query in a result response
    query is type of AlephQuery
    """

class AlephRecord(namedtuple("AlephRecord",
                             ['base',
                              'docNumber',
                              'xml',
                              'epub'])):
    pass

class SearchResult(namedtuple("SearchResult",
                              ['records',
                               'UUID',
                           ])):
    pass
    """ result of search request """



###############################################################################
# Count Aleph #################################################################
###############################################################################

class CountRequest(AlephQueryRequest):
    """
    The same structure as aleph query request.
    It is used for count requests. Application wants to know number of records only.
    """
    pass



class CountResult(namedtuple("AlephCountResult",
                             ['num_of_records',
                              'UUID',
                          ])):
    pass

###############################################################################
# Export to Aleph #############################################################
###############################################################################

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


###############################################################################
#  Interface for an external world  ###########################################
###############################################################################

def toAMQPMessage(request):
    """ returns  edeposit.amqp.AMQPMessage """
    pass


def fromAMQPMessage(message):
    """ returns message of given type
    message       is type of edeposit.amqp.AMQPMessage
    returns structure depending on data in message.
    """
    pass
