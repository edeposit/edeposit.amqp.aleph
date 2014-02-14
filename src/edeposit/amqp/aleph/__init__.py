#! /usr/bin/env python
# -*- coding: utf-8 -*-
# This package may contain traces of nuts
from collections import namedtuple
from datetime import datetime


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


def send_to_aleph(epublication):
    pass


###############################################################################
# Query Aleph #################################################################
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


class AlephSearchResult(namedtuple("AlephSearchResult",
                                   ['records',
                                    'UUID_of_request',
                                    ])):
    pass


class AlephRecord(namedtuple("AlephRecord",
                             ['base',
                              'docNumber',
                              'xml',
                              'epub'])):
    pass


class AlephExportRequest(namedtuple("AlephExportRequest",
                                    ['epublication',
                                     'linkOfEPublication'])):
    """ epublication ... type of EPublication
        linkOfEPublication  ... url with epublication

    User will fill this record.
    """
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
