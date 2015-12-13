#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
"""
Aleph X-Service wrapper.

This module allows you to query Aleph's X-Services_ module (Aleph server is
defined by :attr:`aleph.settings.ALEPH_URL` in :mod:`settings.py
<aleph.settings>`).

.. _X-Services: http://www.exlibrisgroup.com/category/MetaLibXServer

There are two levels of abstraction.

Lowlevel
========

You can use this functions to access Aleph::

    searchInAleph(base, phrase, considerSimilar, field)
    downloadRecords(search_result, [from_doc])
    getDocumentIDs(aleph_search_result, [number_of_docs])
    downloadMARCXML(doc_id, library)
    downloadMARCOAI(doc_id, base)

Workflow
********

Aleph works in strange way, that he won't allow you to access desired
information directly.

You have to create search request by calling :func:`searchInAleph` first, which
will return dictionary with few important informations about session.

This dictionary can be later used as parameter to :func:`getDocumentIDs`
function, which will give you list of :class:`DocumentID` named tuples.

Note:
    :py:func:`~collections.namedtuple` is used, because to access your
    document, you don't need just `document ID` number, but also `library ID`
    string.

Depending on your system, there may be just only one accessible library, or
multiple ones, and then you will be glad, that you get both of this
informations together.

:class:`DocumentID` can be used as parameter to :func:`downloadMARCXML`.

Lets look at some code::

    ids = getDocumentIDs(searchInAleph("nkc", "test", False, "wrd"))
    for id_num, library in ids:
        XML = downloadMARCXML(id_num, library)

        # processDocument(XML)

High-level
==========

XML wrappers
************
This wrappers returns full XML records from Aleph:

    - :func:`getISBNsXML`
    - :func:`getAuthorsBooksXML`
    - :func:`getPublishersBooksXML`
    - :func:`getBooksTitleXML`
    - :func:`getICZBooksXML`

ID wrappers
***********
There are wrappers, which returns ID's of matching document in Aleph:

    - :func:`getISBNsIDs`
    - :func:`getAuthorsBooksIDs`
    - :func:`getPublishersBooksIDs`
    - :func:`getBooksTitleIDs`
    - :func:`getICZBooksIDs`

You can theh download them using :func:`downloadMARCXML` or
:func:`downloadMARCOAI`.

Count wrappers
**************
Count wrappers returns just the number of records with given parameters are
there in aleph.

    - :func:`getISBNCount`
    - :func:`getAuthorsBooksCount`
    - :func:`getPublishersBooksCount`
    - :func:`getBooksTitleCount`
    - :func:`getICZBooksCount`

Note:
    Counting functions are by one request faster than just counting results
    from standard getters. It is preferred to use them to reduce load to Aleph.

Other noteworthy properties
===========================

List of valid bases can be obtained by calling :func:`getListOfBases`, which
returns list of strings.

There is also defined exception tree - see :class:`AlephException` doc-string
for details.
"""
from collections import namedtuple
from string import Template
from urllib import quote_plus

import dhtmlparser
from httpkie import Downloader

from settings import *


# Variables ===================================================================
# String.Template() variable convention is used
SEARCH_URL_TEMPLATE = "/X?op=find&request=$FIELD=$PHRASE&base=$BASE"
SET_URL_TEMPLATE = "/X?op=ill_get_set&set_number=$SET_NUMBER" + \
                   "&start_point=1&no_docs=$NUMBER_OF_DOCS"
DOC_URL_TEMPLATE = "/X?op=ill_get_doc&doc_number=$DOC_ID&library=$LIBRARY"
OAI_DOC_URL_TEMPLATE = "/X?op=find_doc&doc_num=$DOC_ID&base=$BASE"
RECORD_URL_TEMPLATE = "/X?op=present&set_number=$SET_NUM&set_entry=$RECORD_NUM"

MAX_RECORDS = 30


VALID_ALEPH_FIELDS = [
    "wrd",
    "wtl",
    "wau",
    "wkw",
    "txt",
    "wpb",
    "wpp",
    "wyr",
    "ssn",
    "sbn",
    "isn",
    "ob",
    "wpf",
    "wpv",
    "wln",
    "wlo",
    "wtp",
    "sg",
    "bar",
    "cnb",
    "icz",
    "sys",
    "wpk",
]
"""
- ``wrd`` - Všechny údaje [`All fields`]
- ``wtl`` - Název [`Title/name of the book`]
- ``wau`` - Autor (osoba, korporace) [`Author (person, corporation)`]
- ``wkw`` - Předmět (klíčová slova) [`Subject (keywords)`]
- ``txt`` - Slova z obsahu (table of cont.) [`Words from table of content`]
- ``wpb`` - Nakladatel [`Publisher`]
- ``wpp`` - Místo vydání [`Place of publication`]
- ``wyr`` - Rok vydání [`Year of publication`]
- ``ssn`` - ISSN
- ``sbn`` - ISBN / ISMN
- ``isn`` - ISBN / ISMN / ISSN
- ``ob``  - Obsazení (hudební díla) [`Cast (musical works)`]
- ``wpf`` - Periodicita [`Periodicity`]
- ``wpv`` - Kód země vydání [`Country code`]
- ``wln`` - Kód jazyka dokumentu [`Language code`]
- ``wlo`` - Kód jazyka originálu [`Lanugage code of original`]
- ``wtp`` - Druh dokumentu [`Type of document`]
- ``sg``  - Signatura [`Signature`]
- ``bar`` - Čárový kód [`Barcode`]
- ``cnb`` - Číslo národní bibl. [`Number of national bibl.`]
- ``icz`` - Identifikační číslo [`Identification number`]
- ``sys`` - Systémové číslo [`System number`]
- ``wpk``
"""

dhtmlparser.NONPAIR_TAGS = []  # used for parsing XML - see documentation


# Functions & objects =========================================================
class AlephException(Exception):
    """
    Exception tree::

        - AlephException
          |- InvalidAlephBaseException
          |- InvalidAlephFieldException
          |- LibraryNotFoundException
          `- DocumentNotFoundException
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidAlephBaseException(AlephException):
    def __init__(self, message):
        super(InvalidAlephBaseException, self).__init__(message)


class InvalidAlephFieldException(AlephException):
    def __init__(self, message):
        super(InvalidAlephFieldException, self).__init__(message)


class LibraryNotFoundException(AlephException):
    def __init__(self, message):
        super(LibraryNotFoundException, self).__init__(message)


class DocumentNotFoundException(AlephException):
    def __init__(self, message):
        super(DocumentNotFoundException, self).__init__(message)


class DocumentID(namedtuple("DocumentID", ["id", "library", "base"])):
    """
    This structure is used to store `"pointer"` to document in aleph.

    Attributes:
        id (int): ID of document.
        library (str): This can be different for each document, depend on your
                       system.
        base (str): Default "``nkc``", but really depends on what bases you
                    have defined in your Aleph server.
    """
    pass


def getListOfBases():
    """
    This function is here mainly for purposes of unittest

    Returns:
        list of str: Valid bases as they are used as URL parameters in links at
                     Aleph main page.
    """
    downer = Downloader()
    data = downer.download(ALEPH_URL + "/F/?func=file&file_name=base-list")
    dom = dhtmlparser.parseString(data.lower())

    # from default aleph page filter links containing local_base in their href
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
    bases = map(lambda x: x.split("=")[1].strip(), bases)

    return list(set(bases))  # list(set()) is same as unique()


def _tryConvertToInt(s):
    """
    Try convert value from `s` to int.

    Returns:
        int(s): If the value was successfully converted, or `s` when conversion
                failed.
    """
    try:
        return int(s)
    except ValueError:
        return s


def _alephResultToDict(dom):
    """
    Convert part of non-nested XML to :py:class:`dict`.

    Args:
        dom (HTMLElement tree): pre-parsed XML (see dhtmlparser).

    Returns:
        dict: with python data
    """
    result = {}
    for i in dom.childs:
        if not i.isOpeningTag():
            continue

        keyword = i.getTagName().strip()
        value = _tryConvertToInt(i.getContent().strip())

        # if there are multiple tags with same keyword, add values into
        # array, instead of rewriting existing value at given keyword
        if keyword in result:                  # if it is already there ..
            if isinstance(result[keyword], list):  # and it is list ..
                result[keyword].append(value)          # add it to list
            else:                                  # or make it array
                result[keyword] = [result[keyword], value]
        else:                                  # if it is not in result, add it
            result[keyword] = value

    return result


def searchInAleph(base, phrase, considerSimilar, field):
    """
    Send request to the aleph search engine.

    Request itself is pretty useless, but it can be later used as parameter
    for :func:`getDocumentIDs`, which can fetch records from Aleph.

    Args:
        base (str): which database you want to use
        phrase (str): what do you want to search
        considerSimilar (bool): fuzzy search, which is not working at all, so
                               don't use it
        field (str): where you want to look (see: :attr:`VALID_ALEPH_FIELDS`)

    Returns:
        dictionary: consisting from following fields:

            | error (optional): present if there was some form of error
            | no_entries (int): number of entries that can be fetch from aleph
            | no_records (int): no idea what is this, but it is always >= than
                                `no_entries`
            | set_number (int): important - something like ID of your request
            | session-id (str): used to count users for licensing purposes

    Example:
      Returned dict::

        {
         'session-id': 'YLI54HBQJESUTS678YYUNKEU4BNAUJDKA914GMF39J6K89VSCB',
         'set_number': 36520,
         'no_records': 1,
         'no_entries': 1
        }

    Raises:
        AlephException: if Aleph doesn't return any information
        InvalidAlephFieldException: if specified field is not valid
    """
    downer = Downloader()

    if field.lower() not in VALID_ALEPH_FIELDS:
        raise InvalidAlephFieldException("Unknown field '" + field + "'!")

    param_url = Template(SEARCH_URL_TEMPLATE).substitute(
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

    # add informations about base into result
    result["base"] = base

    if "error" not in result:
        return result

    # handle errors
    if result["error"] == "empty set":
        result["no_entries"] = 0  # empty set have 0 entries
        return result
    else:
        raise AlephException(result["error"])


def downloadRecords(search_result, from_doc=1):
    """
    Download `MAX_RECORDS` documents from `search_result` starting from
    `from_doc`.

    Attr:
        search_result (dict): returned from :func:`searchInAleph`.
        from_doc (int, default 1): Start from document number `from_doc`.

    Returns:
        list: List of XML strings with documents in MARC OAI.
    """
    downer = Downloader()

    if "set_number" not in search_result:
        return []

    # set numbers should be probably aligned to some length
    set_number = str(search_result["set_number"])
    if len(set_number) < 6:
        set_number = (6 - len(set_number)) * "0" + set_number

    # download all no_records
    records = []
    for cnt in range(search_result["no_records"]):
        doc_number = from_doc + cnt

        if cnt >= MAX_RECORDS or doc_number > search_result["no_records"]:
            break

        set_data = downer.download(
            ALEPH_URL + Template(RECORD_URL_TEMPLATE).substitute(
                SET_NUM=set_number,
                RECORD_NUM=doc_number,
            )
        )

        records.append(set_data)

    return records


def getDocumentIDs(aleph_search_result, number_of_docs=-1):
    """
    Get IDs, which can be used as parameters for other functions.

    Args:
        aleph_search_result (dict): returned from :func:`searchInAleph`
        number_of_docs (int, optional): how many :class:`DocumentID` from set
                          given by `aleph_search_result` should be returned.
                          Default -1 for all of them.

    Returns:
        list: :class:`DocumentID` named tuples to given `aleph_search_result`.

    Raises:
        AlephException: If Aleph returns unknown format of data.

    Note:
        Returned :class:`DocumentID` can be used as parameters to
        :func:`downloadMARCXML`.
    """
    downer = Downloader()

    if "set_number" not in aleph_search_result:
        return []

    # set numbers should be probably aligned to some length
    set_number = str(aleph_search_result["set_number"])
    if len(set_number) < 6:
        set_number = (6 - len(set_number)) * "0" + set_number

    # limit number of fetched documents, if -1, download all
    if number_of_docs <= 0:
        number_of_docs = aleph_search_result["no_entries"]

    # download data about given set
    set_data = downer.download(
        ALEPH_URL + Template(SET_URL_TEMPLATE).substitute(
            SET_NUMBER=set_number,
            NUMBER_OF_DOCS=number_of_docs,
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

        if "error" in documents:
            raise AlephException("getDocumentIDs: " + documents["error"])

        # convert all document records to DocumentID named tuple and extend
        # them to 'ids' array
        if isinstance(documents["doc-number"], list):
            ids.extend(
                map(
                    lambda x: DocumentID(
                        x,
                        documents["set-library"],
                        aleph_search_result["base"]
                    ),
                    set(documents["doc-number"])
                )
            )
        else:
            ids.append(
                DocumentID(
                    documents["doc-number"],
                    documents["set-library"],
                    aleph_search_result["base"]
                )
            )

    return ids


def downloadMARCXML(doc_id, library, base="nkc"):
    """
    Download MARC XML document with given `doc_id` from given `library`.

    Args:
        doc_id (DocumentID): You will get this from :func:`getDocumentIDs`.
        library (str): "``NKC01``" in our case, but don't worry,
                   :func:`getDocumentIDs` adds library specification into
                   :class:`DocumentID` named tuple.

    Returns:
        str: MARC XML unicode string.

    Raises:
        LibraryNotFoundException
        DocumentNotFoundException
    """
    downer = Downloader()

    data = downer.download(
        ALEPH_URL + Template(DOC_URL_TEMPLATE).substitute(
            DOC_ID=doc_id,
            LIBRARY=library
        )
    )

    dom = dhtmlparser.parseString(data)

    # check if there are any errors
    # bad library error
    error = dom.find("login")
    if error:
        error_msg = error[0].find("error")

        if error_msg:
            raise LibraryNotFoundException(
                "Can't download document doc_id: '" + str(doc_id) + "' " +
                "(probably bad library: '" + library + "')!\nMessage: " +
                "\n".join(map(lambda x: x.getContent(), error_msg))
            )

    # another error - document not found
    error = dom.find("ill-get-doc")
    if error:
        error_msg = error[0].find("error")

        if error_msg:
            raise DocumentNotFoundException(
                "\n".join(map(lambda x: x.getContent(), error_msg))
            )

    return data  # MARCxml of document with given doc_id


def downloadMARCOAI(doc_id, base):
    """
    Download MARC OAI document with given `doc_id` from given (logical) `base`.

    Funny part is, that some documents can be obtained only with this function
    in their full text.

    Args:
        doc_id (str):         You will get this from :func:`getDocumentIDs`.
        base (str, optional): Base from which you want to download Aleph
                              document.
                              This seems to be duplicite with
                              :func:`searchInAleph` parameters, but it's just
                              something Aleph's X-Services wants, so ..

    Returns:
        str: MARC XML Unicode string.

    Raises:
        InvalidAlephBaseException
        DocumentNotFoundException
    """
    downer = Downloader()

    data = downer.download(
        ALEPH_URL + Template(OAI_DOC_URL_TEMPLATE).substitute(
            DOC_ID=doc_id,
            BASE=base
        )
    )

    dom = dhtmlparser.parseString(data)

    # check for errors
    error = dom.find("error")
    if len(error) <= 0:  # no errors
        return data

    if "Error reading document" in error[0].getContent():
        raise DocumentNotFoundException(
            str(error[0].getContent())
        )
    else:
        raise InvalidAlephBaseException(
            error[0].getContent() + "\n" +
            "The base you are trying to access probably doesn't exist."
        )


# High level API ==============================================================
def getISBNsXML(isbn, base=ALEPH_DEFAULT_BASE):
    """
    Download full XML record for given `isbn` in `base`.

    Args:
        isbn (str): ISBN of the books you want to get.
        base (str): Base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: List of strings with full **OAI** XML representation of the \
              record.
    """
    return downloadRecords(
        searchInAleph(
            base,
            isbn,
            False,
            "sbn"
        )
    )


def getISSNsXML(issn, base=ALEPH_DEFAULT_BASE):
    """
    Download full XML record for given `issn` in `base`.

    Args:
        issn (str): ISSN of the books you want to get.
        base (str): Base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: List of strings with full **OAI** XML representation of the \
              record.
    """
    return downloadRecords(
        searchInAleph(
            base,
            issn,
            False,
            "ssn"
        )
    )


def getAuthorsBooksXML(author, base=ALEPH_DEFAULT_BASE):
    """
    Download full XML record for given `author` in `base`.

    Args:
        author (str): Name of the `author` of the books you want to get.
        base (str): Base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: List of strings with full **OAI** XML representation of the \
              record.
    """
    return downloadRecords(
        searchInAleph(
            base,
            author,
            False,
            "wau"
        )
    )


def getPublishersBooksXML(publisher, base=ALEPH_DEFAULT_BASE):
    """
    Download full XML record for given `publisher` in `base`.

    Args:
        publisher (str): Name of the `publisher` of the books you want to get.
        base (str): Base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: List of strings with full **OAI** XML representation of the \
              record.
    """
    return downloadRecords(
        searchInAleph(
            base,
            publisher,
            False,
            "wpb"
        )
    )


def getBooksTitleXML(title, base=ALEPH_DEFAULT_BASE):
    """
    Download full XML record for given `title` in `base`.

    Args:
        title (str): `title` of the books you want to get.
        base (str): Base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: List of strings with full **OAI** XML representation of the \
              record.
    """
    return downloadRecords(
        searchInAleph(
            base,
            title,
            False,
            "wtl"
        )
    )


def getICZBooksXML(icz, base=ALEPH_DEFAULT_BASE):
    """
    Download full XML record for given `icz` (identification number) in `base`.

    Args:
        icz (str): Identification number used to search Aleph.
        base (str): Base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: List of strings with full **OAI** XML representation of the \
              record.
    """
    return downloadRecords(
        searchInAleph(
            base,
            icz,
            False,
            "icz"
        )
    )


# ID getters ==================================================================
def getISBNsIDs(isbn, base=ALEPH_DEFAULT_BASE):
    """
    Get list of :class:`DocumentID` objects of documents with given `isbn`.

    Args:
        isbn (str): ISBN string.
        base (str, optional): Base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: of :class:`DocumentID` objects
    """
    return getDocumentIDs(searchInAleph(base, isbn, False, "sbn"))


def getAuthorsBooksIDs(author, base=ALEPH_DEFAULT_BASE):
    """
    Get list of :class:`DocumentID` objects of documents with given `author`.

    Args:
        author (str): Authors name/lastname in UTF-8.
        base (str, optional): base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: of :class:`DocumentID` objects
    """
    return getDocumentIDs(searchInAleph(base, author, False, "wau"))


def getPublishersBooksIDs(publisher, base=ALEPH_DEFAULT_BASE):
    """
    Get list of :class:`DocumentID` objects of documents with given
    `publisher`.

    Args:
        publisher (str): Name of publisher which will be used to search Aleph.
        base (str, optional): base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: of :class:`DocumentID` objects
    """
    return getDocumentIDs(searchInAleph(base, publisher, False, "wpb"))


def getBooksTitleIDs(title, base=ALEPH_DEFAULT_BASE):
    """
    Get list of :class:`DocumentID` objects of documents with given
    `title`.

    Args:
        title (str): Title (name) of the book which will be used to search in
                     Aleph.
        base (str, optional): base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: of :class:`DocumentID` objects
    """
    return getDocumentIDs(searchInAleph(base, title, False, "wtl"))


def getICZBooksIDs(icz, base=ALEPH_DEFAULT_BASE):
    """
    Get list of :class:`DocumentID` objects of documents with given
    `icz` (identification number).

    Args:
        icz (str): Identification number used to search Aleph.
        base (str, optional): base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        list: of :class:`DocumentID` objects
    """
    return getDocumentIDs(searchInAleph(base, icz, False, "icz"))


# Counters ====================================================================
def getISBNCount(isbn, base=ALEPH_DEFAULT_BASE):
    """
    Get number of records in Aleph which match given `isbn`.

    Args:
        isbn (str): ISBN string.
        base (str, optional): Base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        int: Number of matching documents in Aleph.
    """
    return searchInAleph(base, isbn, False, "sbn")["no_entries"]


def getAuthorsBooksCount(author, base=ALEPH_DEFAULT_BASE):
    """
    Get number of records in Aleph which match given `author`.

    Args:
        author (str): Authors name/lastname in UTF-8.
        base (str, optional): base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        int: Number of matching documents in Aleph.
    """
    return searchInAleph(base, author, False, "wau")["no_entries"]


def getPublishersBooksCount(publisher, base=ALEPH_DEFAULT_BASE):
    """
    Get number of records in Aleph which match given `publisher`.

    Args:
        publisher (str): Name of publisher which will be used to search Aleph.
        base (str, optional): base on which will be search performed. Default
                       :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        int: Number of matching documents in Aleph.
    """
    return searchInAleph(base, publisher, False, "wpb")["no_entries"]


def getBooksTitleCount(title, base=ALEPH_DEFAULT_BASE):
    """
    Get number of records in Aleph which match given `title`.

    Args:
        title (str): Title (name) of book which will be used to search Aleph.
        base (str, optional): base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        int: Number of matching documents in Aleph.
    """
    return searchInAleph(base, title, False, "wtl")["no_entries"]


def getICZBooksCount(icz, base=ALEPH_DEFAULT_BASE):
    """
    Get number of records in Aleph which match given `title`.

    Args:
        icz (str): Identification number used to search Aleph.
        base (str, optional): base on which will be search performed. Default
                    :attr:`aleph.settings.ALEPH_DEFAULT_BASE`.

    Returns:
        int: Number of matching documents in Aleph.
    """
    return searchInAleph(base, icz, False, "icz")["no_entries"]
