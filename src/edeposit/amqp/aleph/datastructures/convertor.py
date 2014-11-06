#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module exists to provide ability to convert from Aleph's data structures
to AMQP data structures, specifically to convert :class:`.MARCXMLRecord` to
:class:`.EPublication` simplified data structure.
"""
# Imports =====================================================================
import dhtmlparser

from ..marcxml import MARCXMLRecord
from __init__ import *
from semanticinfo import SemanticInfo


# Functions & objects =========================================================
def toSemanticInfo(xml):
    """
    Pick informations from :class:`.MARCXMLRecord` object and use it to build
    :class:`.SemanticInfo` structure.

    Args:
        xml (str/MARCXMLRecord): MarcXML which will be converted to
            SemanticInfo. In case of str, ``<record>`` tag is required.

    Returns:
        structure: :class:`.SemanticInfo`.

    """
    hasAcquisitionFields = False
    hasISBNAgencyFields = False
    hasDescriptiveCatFields = False
    hasDescriptiveCatReviewFields = False
    hasSubjectCatFields = False
    hasSubjectCatReviewFields = False

    parsed = xml
    if not isinstance(xml, MARCXMLRecord):
        parsed = MARCXMLRecord(str(xml))

    if "HLD" in parsed.datafields or "HLD" in parsed.controlfields:
        hasAcquisitionFields = True

    # look for catalogization fields
    for status in parsed.getDataRecords("IST", "a", []):
        status = status.replace(" ", "")  # remove spaces

        if status.startswith("jp2"):
            hasDescriptiveCatFields = True
        elif status.startswith("jr2"):
            hasDescriptiveCatReviewFields = True
        elif status.startswith("vp"):
            hasSubjectCatFields = True
        elif status.startswith("vr"):
            hasSubjectCatReviewFields = True
        elif status.startswith("ii2"):
            hasISBNAgencyFields = True

    return SemanticInfo(
        hasAcquisitionFields,
        hasISBNAgencyFields,
        hasDescriptiveCatFields,
        hasDescriptiveCatReviewFields,
        hasSubjectCatFields,
        hasSubjectCatReviewFields,
    )


def toEPublication(xml):
    """
    Convert :class:`.MARCXMLRecord` object to :class:`.EPublication`
    namedtuple.

    Args:
        xml (str/MARCXMLRecord): MarcXML which will be converted to
            EPublication. In case of str, ``<record>`` tag is required.

    Returns:
        structure: :class:`.EPublication` namedtuple with data about \
                   publication.

    See Also:
        :class:`aleph.datastructures.epublication` for details of
        :class:`.EPublication`, structure.
    """
    parsed = xml
    if not isinstance(xml, MARCXMLRecord):
        parsed = MARCXMLRecord(str(xml))

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
    zpracovatel = zpracovatel[0] if zpracovatel else ""

    # url
    url = parsed.getDataRecords("856", "u", False)
    url = url[0] if url else ""

    # internal url
    internal_url = parsed.getDataRecords("998", "a", False)
    internal_url = internal_url[0] if internal_url else ""

    binding = parsed.getBinding()

    # i know, that this is not PEP8, but you dont want to see it without proper
    # formating (it looks bad, really bad)
    return EPublication(
        ISBN                = parsed.getISBNs(),
        nazev               = parsed.getName(),
        podnazev            = parsed.getSubname(),
        vazba               = binding[0] if binding else "",
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
        url                 = url.replace("&amp;", "&"),
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
        internal_url        = internal_url.replace("&amp;", "&")
    )


def getDocNumber(xml):
    """
    Parse <doc_number> tag from `xml`.

    Args:
        xml (str): XML string returned from :func:`aleph.aleph.downloadRecords`

    Returns:
        str: Doc ID as string or "-1" if not found.
    """
    dom = dhtmlparser.parseString(xml)

    doc_number_tag = dom.find("doc_number")

    if not doc_number_tag:
        return "-1"

    return doc_number_tag[0].getContent().strip()
