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
        nazev=parsed.getName(),
        podnazev=parsed.getSubname(),
        vazba=parsed.getBinding()[0],
        cena=parsed.getPrice(),
        castDil=parsed.getPart(),
        nazevCasti=parsed.getPartName(),
        nakladatelVydavatel=parsed.getPublisher(),
        datumVydani=parsed.getPubDate(),
        poradiVydani=parsed.getPubOrder(),
        zpracovatelZaznamu=zpracovatel,
        kategorieProRIV="",
        mistoDistribuce=mistoDistribuce,
        distributor=distributor,
        datumDistribuce=datumDistribuce,
        datumProCopyright="",
        format=parsed.getFormat(),
        url="",
        mistoVydani=arrayOrWhat(
            parsed.getDataRecords("260", "a", False),
            ""
        ),
        ISBNSouboruPublikaci=parsed.getISBNs(),
        autori=map(  # convert Persons to amqp's Authors
            lambda a: Author(
                (a.name + " " + a.second_name).strip(),
                a.surname,
                a.title
            ),
            parsed.getAuthors()
        ),
        originaly=parsed.getOriginals(),
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