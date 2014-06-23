#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
This module exists to provide ability to convert from AMQP data structures to
Aleph's data structures, specifically to convert :class:`.MARCXMLRecord` to
:class:`.EPublication` simplified data structure.
"""
from marcxml import MARCXMLRecord
from datastructures import *
from __init__ import *


#= Functions & objects ========================================================
def toEPublication(marcxml):
    """
    Convert MARCXMLRecord object to :class:`.EPublication` named tuple.

    Args:
        marcxml (str/MARCXMLRecord): MarcXML which will be converted to
                EPublication. In case of str, <record> tag is required.

    Returns:
        EPublication: named tuple with data about publication.

    See Also:
        :class:`aleph.datastructures.epublication` for details of
        :class:`.EPublication`, structure.
    """
    parsed = marcxml
    if not isinstance(marcxml, MARCXMLRecord):
        parsed = MARCXMLRecord(str(marcxml))

    # distributor = ""  # FUTURE
    # mistoDistribuce = ""
    # datumDistribuce = ""

    # # parse information about distributors
    # distributors = parsed.getCorporations("dst")
    # if len(distributors) >= 1:
    #     mistoDistribuce = distributors[0].place
    #     datumDistribuce = distributors[0].date
    #     distributor = distributors[0].name

    # zpracovatel
    zpracovatel = parsed.getDataRecords("040", "a", False)
    zpracovatel = zpracovatel[0] if len(zpracovatel) >= 1 else ""

    # url
    url = parsed.getDataRecords("856", "u", False)
    url = url[0] if len(url) >= 1 else ""

    binding = parsed.getBinding()

    # i know, that this is not PEP8, but you dont want to see it without proper
    # formating (it looks bad, really bad)
    return EPublication(
        ISBN                = parsed.getISBNs(),
        nazev               = parsed.getName(),
        podnazev            = parsed.getSubname(),
        vazba               = binding[0] if len(binding) > 0 else "",
        cena                = parsed.getPrice(),
        castDil             = parsed.getPart(),
        nazevCasti          = parsed.getPartName(),
        nakladatelVydavatel = parsed.getPublisher(),
        datumVydani         = parsed.getPubDate(),
        poradiVydani        = parsed.getPubOrder(),
        zpracovatelZaznamu  = zpracovatel,
        # mistoDistribuce     = mistoDistribuce,  # FUTURE
        # distributor         = distributor,
        # datumDistribuce     = datumDistribuce,
        # datumProCopyright   = "",
        format              = parsed.getFormat(),
        url                 = url,
        mistoVydani         = parsed.getPubPlace(),
        ISBNSouboruPublikaci= [],
        autori              = map(  # convert Persons to amqp's Authors
            lambda a: Author(
                (a.name + " " + a.second_name).strip(),
                a.surname,
                a.title
            ),
            parsed.getAuthors()
        ),
        originaly           = parsed.getOriginals(),
        internal_url        = ""  # TODO
    )
