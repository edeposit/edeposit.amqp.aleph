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

from remove_hairs import remove_hairs
from marcxml_parser import MARCXMLRecord

from ..aleph import DocumentNotFoundException

from __init__ import Author
from __init__ import EPublication
from __init__ import SemanticInfo


# Functions & objects =========================================================
def _parse_summaryRecordSysNumber(summaryRecordSysNumber):
    """
    Try to parse vague, not likely machine-readable description and return
    first token, which contains enough numbers in it.
    """
    def number_of_digits(token):
        digits = filter(lambda x: x.isdigit(), token)
        return len(digits)

    tokens = map(
        lambda x: remove_hairs(x, r" .,:;<>(){}[]\/"),
        summaryRecordSysNumber.split()
    )

    # pick only tokens that contains 3 digits
    contains_digits = filter(lambda x: number_of_digits(x) > 3, tokens)

    if not contains_digits:
        return ""

    return contains_digits[0]


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
    isClosed = False
    summaryRecordSysNumber = ""
    parsedSummaryRecordSysNumber = ""
    isSummaryRecord = False
    contentOfFMT = ""

    parsed = xml
    if not isinstance(xml, MARCXMLRecord):
        parsed = MARCXMLRecord(str(xml))

    # handle FMT record
    if "FMT" in parsed.controlfields:
        contentOfFMT = parsed["FMT"]

        if contentOfFMT == "SE":
            isSummaryRecord = True

    if "HLD" in parsed.datafields or "HLD" in parsed.controlfields:
        hasAcquisitionFields = True

    # look for catalogization fields
    for status in parsed["ISTa"]:
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

    # look whether the record was 'closed' by catalogizators
    for status in parsed["BASa"]:
        if status == "90":
            isClosed = True

    # detect link to 'new' record, if the old one was 'closed'
    for status in parsed["PJMa"]:
        if status:
            summaryRecordSysNumber = status
            parsedSummaryRecordSysNumber = _parse_summaryRecordSysNumber(
                summaryRecordSysNumber
            )
            break

    return SemanticInfo(
        hasAcquisitionFields=hasAcquisitionFields,
        hasISBNAgencyFields=hasISBNAgencyFields,
        hasDescriptiveCatFields=hasDescriptiveCatFields,
        hasDescriptiveCatReviewFields=hasDescriptiveCatReviewFields,
        hasSubjectCatFields=hasSubjectCatFields,
        hasSubjectCatReviewFields=hasSubjectCatReviewFields,
        isClosed=isClosed,
        isSummaryRecord=isSummaryRecord,
        contentOfFMT=contentOfFMT,
        parsedSummaryRecordSysNumber=parsedSummaryRecordSysNumber,
        summaryRecordSysNumber=summaryRecordSysNumber,
    )


def _first_or_blank_string(items):
    if not items:
        return ""

    return items[0]


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

    # check whether the document was deleted
    if "DEL" in parsed.datafields:
        raise DocumentNotFoundException("Document was deleted.")

    zpracovatel = _first_or_blank_string(parsed["040a"])

    # convert Persons objects to amqp's Authors namedtuple
    authors = map(
        lambda a: Author(
            (a.name + " " + a.second_name).strip(),
            a.surname,
            a.title
        ),
        parsed.get_authors()
    )

    # i know, that this is not PEP8, but you dont want to see it without proper
    # formating (it looks bad, really bad)
    return EPublication(
        ISBN                = parsed.get_ISBNs(),
        nazev               = parsed.get_name(),
        podnazev            = parsed.get_subname(),
        vazba               = _first_or_blank_string(parsed.get_binding()),
        cena                = parsed.get_price(),
        castDil             = parsed.get_part(),
        nazevCasti          = parsed.get_part_name(),
        nakladatelVydavatel = parsed.get_publisher(),
        datumVydani         = parsed.get_pub_date(),
        poradiVydani        = parsed.get_pub_order(),
        zpracovatelZaznamu  = zpracovatel,
        # mistoDistribuce     = mistoDistribuce,  # FUTURE
        # distributor         = distributor,
        # datumDistribuce     = datumDistribuce,
        # datumProCopyright   = "",
        format              = parsed.get_format(),
        url                 = parsed.get_urls(),
        mistoVydani         = parsed.get_pub_place(),
        ISBNSouboruPublikaci= [],
        autori              = authors,
        originaly           = parsed.get_originals(),
        internal_url        = parsed.get_internal_urls()
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
