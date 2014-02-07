#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple
from string import Template
from urllib import quote_plus

from settings import *


import dhtmlparser
from httpkie import Downloader


#= Variables ==================================================================
# String.Template() variable convetion is used
ALEPH_SEARCH_URL_TEMPLATE = "/X?op=find&request=$FIELD=$PHRASE&base=$BASE&adjacent=$SIMILAR"
ALEPH_GET_SET_URL_TEMPLATE = "/X?op=ill_get_set&set_number=$SET_NUMBER&start_point=1&no_docs=$NUMBER_OF_DOCS"

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

DocumentID = namedtuple("DocumentID", ["id", "library"])


#= Functions & objects ========================================================
class AlephException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidAlephBaseException(AlephException):
    def __init__(self, message):
        super(self, message)


class InvalidAlephFieldException(AlephException):
    def __init__(self, message):
        super(self, message)


def _getListOfBases():
    """
    Return list of valid bases as they are used as URL parameters in links at
    aleph main page.

    This function is here mainly for purposes of unittest (see assert in main).
    """
    downer = Downloader()
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


def _tryConvertToInt(s):
    """Try convert value from 's' to int, return int if succes, 's' if fail."""
    try:
        return int(s)
    except ValueError:
        return s


def _alephResultToDict(find): # TODO: docstring, parameters
    result = {}
    for i in find.childs:
        if i.isOpeningTag():
            keyword = i.getTagName().strip()
            value = _tryConvertToInt(i.getContent().strip())

            # if there are multiple tags with same keyword, add values into
            # array, instead of rewriting existing value at given keyword
            if keyword not in result:  # if it is not in result, add it
                result[keyword] = value
            else:  # if it is already there ..
                if isinstance(result[keyword], list):  # and it is list ..
                    result[keyword].append(value)  # add it to list
                else:
                    result[keyword] = [result[keyword], value] # or make it array

    return result


def searchInAleph(base, phrase, considerSimilar, field):
    """
    Send request to the aleph search engine.

    Request itself is pretty useless, but it can be later used as parameter
    getAlephRecords(), which can fetch records from Aleph.

    phrase -- what you want to search
    base -- which database you want to use
    field -- where you want to look
    considerSimilar -- fuzzy search, which is not working at all, so don't use
    it

    Returns:
        aleph_search_record, which is dictionary consisting from those fileds:
            error (optional) -- present if there was some form of error
            no_entries (int) -- number of entries that can be fetch from aleph
            no_records (int) -- no idea what is this, but it is always >= than
                                no_entries
            set_number (int) -- important - something like ID of your request
            session-id (str) -- used to count users for licencing purposes

        example:
            {
             'session-id': 'YLI54HBQJESUTS678YYUNKEU4BNAUJDKA914GMF39J6K89VSCB',
             'set_number': 36520,
             'no_records': 1,
             'no_entries': 1
            }

    TODO:
        - support multiple phrases in one request
    """
    downer = Downloader()

    if base.lower() not in VALID_ALEPH_BASES:
        raise InvalidAlephBaseException("Unknown base '" + base + "'!")

    if field.lower() not in VALID_ALEPH_FIELDS:
        raise InvalidAlephFieldException("Unknown field '" + base + "'!")

    param_url = Template(ALEPH_SEARCH_URL_TEMPLATE).substitute(
        PHRASE=quote_plus(phrase),  # urlencode phrase
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
    result = _alephResultToDict(find)

    if "error" in result:
        if result["error"] == "empty set":
            result["no_entries"] = 0  # empty set have 0 entries
            return result
        else:
            raise AlephException(result["error"])

    return result


def getDocumentIDs(aleph_search_result, number_of_docs=-1):
    """
    Return list of DocumentID named tupples to given 'aleph_search_result'.

    aleph_search_result -- dict returned from searchInAleph()
    number_of_docs -- how much DocumentIDs from set should be returned

    Returned DocumentID can be used as parameters to downloadAlephDocument().
    """
    downer = Downloader()

    # set numbers should be probably aligned to some length
    set_number = str(aleph_search_result["set_number"])
    if len(set_number) < 6:
        set_number = (6 - len(set_number)) * "0" + set_number

    # limit number of fetched documents, if -1, download all
    if number_of_docs <= 0:
        number_of_docs = aleph_search_result["no_entries"]

    # download data about given set
    set_data = downer.download(
        ALEPH_URL + Template(ALEPH_GET_SET_URL_TEMPLATE).substitute(
            SET_NUMBER=set_number,
            NUMBER_OF_DOCS=number_of_docs
        )
    )

    # parse data
    dom = dhtmlparser.parseString(set_data)
    set_data = dom.find("ill-get-set")

    # there should be at least one <ill-get-set> field
    if len(set_data) <= 0:
        raise AlephException("Aleph didn't returned set data.")

    ids = []
    for library in set_data:
        documents = _alephResultToDict(library)

        # convert all document records to DocumentID named tuple and extend
        # them to 'ids' array
        if isinstance(documents["doc-number"], list):
            ids.extend(
                map(
                    lambda x: DocumentID(x, documents["set-library"]),
                    set(documents["doc-number"])
                )
            )
        else:
            ids.append(
                DocumentID(
                    documents["doc-number"],
                    documents["set-library"]
                )
            )

    return ids


def downloadAlephDocument(doc_id, library):
    downer = Downloader()
    ALEPH_GET_DOC_URL_TEMPLATE = "/X?op=ill_get_doc&doc_number=$DOC_NUMBER&library=$LIBRARY"

    data = downer.download(
        ALEPH_URL + Template(ALEPH_GET_DOC_URL_TEMPLATE).substitute(
            DOC_NUMBER=doc_id,
            LIBRARY=library
        )
    )

    print data # MARCxml of document with given doc_id (TODO:  ošetřit errory)


def searchISBN(isbn, base="nkc"):  # TODO: test olny
    return searchInAleph(base, isbn, False, "sbn")


def searchAuthor(author, base="nkc"):
    return searchInAleph(base, author, False, "wau")


#= Main program ===============================================================
if __name__ == '__main__':
    print getDocumentIDs(searchISBN("978-80-7367-397-0"))
    # print getDocumentIDs(searchAuthor("Jiří Kulhánek"))

    # check if VALID_ALEPH_BASES is actual (set assures unordered comparsion)
    assert(set(_getListOfBases()) == set(VALID_ALEPH_BASES))
