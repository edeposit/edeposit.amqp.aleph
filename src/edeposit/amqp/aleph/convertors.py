#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from marcxml import MARCXMLRecord
from __init__ import Producent, EPublication, OriginalFile, Author


#= Functions & objects ========================================================
def toEPublication(marcxml):
    """
    Convert MARCXMLRecord object to EPublication named tuple (see __init__.py).

    marcxml -- MARCXMLRecord instance OR string (with <record> tag)

    Returns EPublication named tuple.
    """
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

    # i know, that this is not PEP8, but you dont want to see it without proper
    # formating (it looks bad, really bad)
    return EPublication(
        nazev               = parsed.getName(),
        podnazev            = parsed.getSubname(),
        vazba               = parsed.getBinding()[0],
        cena                = parsed.getPrice(),
        castDil             = parsed.getPart(),
        nazevCasti          = parsed.getPartName(),
        nakladatelVydavatel = parsed.getPublisher(),
        datumVydani         = parsed.getPubDate(),
        poradiVydani        = parsed.getPubOrder(),
        zpracovatelZaznamu  = zpracovatel,
        kategorieProRIV     = "",
        mistoDistribuce     = mistoDistribuce,
        distributor         = distributor,
        datumDistribuce     = datumDistribuce,
        datumProCopyright   = "",
        format              = parsed.getFormat(),
        url                 = "",
        mistoVydani         = parsed.getPubPlace(),
        ISBNSouboruPublikaci= parsed.getISBNs(),
        autori              = map(  # convert Persons to amqp's Authors
            lambda a: Author(
                (a.name + " " + a.second_name).strip(),
                a.surname,
                a.title
            ),
            parsed.getAuthors()
        ),
        originaly=parsed.getOriginals(),
    )


def fromEPublication(epublication):
    raise NotImplementedError("Not implemented yet.")


#= Main program ===============================================================
if __name__ == '__main__':
    r = MARCXMLRecord(open("multi_example.xml").read())

    # print r.datafields["910"]
    # print r.leader
    # print r.toXML()

    # print r.getDataRecords("020", "a")
    print toEPublication(r)
