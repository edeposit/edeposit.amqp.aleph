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
ISBN_TEMPLATE = "/X?op=find&request=sbn=$ISBN&base=$base"
VALID_BASES = [  # see getListOfBases() for details
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

downer = Downloader()


#= Functions & objects ========================================================
class InvalidAlephBaseException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def getListOfBases():
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
    base_links = map(lambda x: x.params["href"].split("&"), base_links)

    # filter only sections containing bases
    bases = map(
        lambda link: filter(lambda base: "local_base" in base, link)[0],
        base_links
    )

    # filter bases from base sections
    bases = map(
        lambda x: x.split("=")[1].strip(),
        bases
    )

    return list(set(bases))


def searchISBN(isbn, base):
    if base.lower() not in VALID_BASES:
        raise InvalidAlephBaseException("Unknown base '" + base + "'!")

    result = downer.download(
        ALEPH_URL + Template(ISBN_TEMPLATE).substitute(ISBN=isbn, base=base)
    )

    dom = dhtmlparser.parseString(result)

    print dom  # TODO


#= Main program ===============================================================
if __name__ == '__main__':
    print searchISBN("978-80-7367-397-0", "nkc")

    # check if VALID_BASES is actual (set assures unordered comparsion)
    assert(set(getListOfBases()) == set(VALID_BASES))
