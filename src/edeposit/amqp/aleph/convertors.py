#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from marcxml import MARCXMLRecord
from __init__ import Producent, EPublication, OriginalFile, Author


#= Variables ==================================================================



#= Functions & objects ========================================================
def arrayOrWhat(array, what):
    """
    If len(array) == 0, return what, else array.

    If there is only one element in array, return just the element.
    """
    if len(array) <= 0:
        return what

    return array if len(array) > 1 else array[0]


def toEpublication(marcxml):
    parsed = marcxml
    if not isinstance(marcxml, MARCXMLRecord):
        parsed = MARCXMLRecord(str(marcxml))

    # parse ISBNs
    rest = ""
    clean_ISBNs = []
    for ISBN in parsed.getDataRecords("020", "a", True):
        clean_ISBN, rest = ISBN.split(" ", 1)
        clean_ISBNs.append(clean_ISBN)

    originals = []
    for orig in parsed.getDataRecords("765", "t", False):
        originals.append(orig)

    distributor = ""
    mistoDistribuce = ""
    datumDistribuce = ""

    # parse information about distributors
    distributors = parsed.getCorporations("dst")
    if len(distributors) >= 1:
        mistoDistribuce = distributors[0].place
        datumDistribuce = distributors[0].date
        distributor = distributors[0].name

    # zpracovatel
    zpracovatel = parsed.getDataRecords("040", "a", False)
    if len(zpracovatel) >= 1:
        zpracovatel = zpracovatel[0]
    else:
        zpracovatel = ""

    return EPublication(
        nazev=arrayOrWhat(
            parsed.getDataRecords("245", "a", False),
            ""
        ),
        podnazev=arrayOrWhat(
            parsed.getDataRecords("245", "b", False),
            ""
        ),
        vazba=rest.strip(),
        cena=arrayOrWhat(
            parsed.getDataRecords("020", "c", False),
            ""
        ),
        castDil=arrayOrWhat(
            parsed.getDataRecords("245", "p", False),
            ""
        ),
        nazevCasti=arrayOrWhat(
            parsed.getDataRecords("245", "n", False),
            ""
        ),
        nakladatelVydavatel=arrayOrWhat(
            parsed.getDataRecords("260", "b", False),
            ""
        ),
        datumVydani=arrayOrWhat(
            parsed.getDataRecords("260", "c", False),
            ""
        ),
        poradiVydani=arrayOrWhat(
            parsed.getDataRecords("901", "f", False),
            ""
        ),
        zpracovatelZaznamu=zpracovatel,
        kategorieProRIV="",
        mistoDistribuce=mistoDistribuce,
        distributor=distributor,
        datumDistribuce=datumDistribuce,
        datumProCopyright="",
        format=arrayOrWhat(
            parsed.getDataRecords("300", "c", False),
            ""
        ),
        url="",
        mistoVydani=arrayOrWhat(
            parsed.getDataRecords("260", "a", False),
            ""
        ),
        ISBNSouboruPublikaci=clean_ISBNs,
        autori=map(  # convert Persons to amqp's Authors
            lambda a: Author(
                (a.name + " " + a.second_name).strip(),
                a.surname,
                a.title
            ),
            parsed.getAuthors()
        ),
        originaly=originals,
    )


def fromEpublication(epublication):
    pass


#= Main program ===============================================================
if __name__ == '__main__':
    r = MARCXMLRecord(open("multi_example.xml").read())

    # print r.datafields["910"]
    # print r.leader
    # print r.toXML()

    # print r.getDataRecords("020", "a")
    print toEpublication(r)