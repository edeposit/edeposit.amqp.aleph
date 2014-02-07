#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from string import Template
from settings import *


import dhtmlparser
from httpkie import Downloader


#= Variables ==================================================================
# String.Template() variable convetion is used
ISBN_TEMPLATE = "/X?op=find&request=$FIELD=$PHRASE&base=$BASE&adjacent=$SIMILAR"

VALID_ALEPH_BASES = [  # see getListOfBases() for details
    'ksl',
    'nkc',
    'nkok',
    'anl',
    'nak',
    'mobil-nkc',
    'stt',
    'kkl',
    'aut-z',
    'cnb',
    'aut',
    'skc',
    'slk',
    'ktd',
    'adr',
    'kzk',
    'skcp'
]

VALID_ALEPH_FIELDS = [
    "wrd",  # slova ze všech popisných údaju
    "wtl",  # slova z názvových údajů (název, název části, edice, originál atd)
    "wau",  # slova z údajů o autorech
    "wpb",  # slova z údajů o nakladateli
    "wpp",  # slova z údajů o místě vydání
    "wyr",  # rok vydání
    "wkw",  # předmět (klíčová slova)
    "sbn",  # ISBN/ISMN
    "ssn",  # ISSN
    "icz",  # identifikační číslo záznamu
    "cnb",  # číslo ČNB
    "sg"  # signatura
]

downer = Downloader()  # used for working with webapi


#= Functions & objects ========================================================
class AlephException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidAlephBaseException(AlephException):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidAlephFieldException(AlephException):
    def __init__(self, message):
        Exception.__init__(self, message)


def _getListOfBases():
    """
    Return list of valid bases as they are used as URL parameters in links at
    aleph main page.

    This function is here mainly for purposes of unittest (see assert in main).
    """
    data = downer.download(ALEPH_URL + "/F/?func=file&file_name=base-list")
    dom = dhtmlparser.parseString(data.lower())

    # from deafult aleph page filter links containing local_base in their href
    base_links = filter(
        lambda x: "href" in x.params and "local_base" in x.params["href"],
        dom.find("a")
    )

    # split links by & - we will need only XXX from link.tld/..&local_base=XXX
    base_links = map(
        lambda x: x.params["href"].replace("?", "&", 1).split("&"),
        base_links
    )

    # filter only sections containing bases
    bases = map(
        lambda link: filter(lambda base: "local_base=" in base, link)[0],
        base_links
    )

    # filter bases from base sections
    bases = map(
        lambda x: x.split("=")[1].strip(),
        bases
    )

    return list(set(bases))  # list(set()) is same as unique()


def searchInAleph(base, phrase, considerSimilar, field):  # TODO: podporu vice phrases najednou
    if base.lower() not in VALID_ALEPH_BASES:
        raise InvalidAlephBaseException("Unknown base '" + base + "'!")

    if field.lower() not in VALID_ALEPH_FIELDS:
        raise InvalidAlephFieldException("Unknown field '" + base + "'!")

    param_url = Template(ISBN_TEMPLATE).substitute(
        PHRASE=phrase,
        BASE=base,
        FIELD=field,
        SIMILAR="Y" if considerSimilar else "N"
    )
    result = downer.download(ALEPH_URL + param_url)

    dom = dhtmlparser.parseString(result)

    find = dom.find("find")  # find <find> element :)
    if len(find) <= 0:
        raise AlephException("Aleph didn't returned any information.")
    find = find[0]

    # convert aleph result into dictionary
    result = {}
    for i in find.childs:
        if i.isOpeningTag():
            result[i.getTagName()] = i.getContent()

    if "error" in result:
        if result["error"] == "empty set":
            return []  # TODO: dodělat
        else:
            raise AlephException(result["error"])

    return result


def searchISBN(isbn, base="nkc"):  # TODO: test olny
    return searchInAleph(base, isbn, False, "sbn")


#= Main program ===============================================================
if __name__ == '__main__':
    print searchISBN("978-80-7367-397-0")

    # check if VALID_ALEPH_BASES is actual (set assures unordered comparsion)
    assert(set(_getListOfBases()) == set(VALID_ALEPH_BASES))
