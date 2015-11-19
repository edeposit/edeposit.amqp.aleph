#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Definition of structures, which are used to hold informations about
catalogization process of periodical publications.
"""
# Imports =====================================================================
from collections import namedtuple

from remove_hairs import remove_hairs
from marcxml_parser import MARCXMLRecord

from semanticinfo import _parse_summaryRecordSysNumber


# Structures ==================================================================
class EPeriodicalSemanticInfo(namedtuple("EPeriodicalSemanticInfo", [
                                               "hasAcquisitionFields",
                                               "acquisitionFields",
                                               "isClosed",
                                               "isSummaryRecord",
                                               "contentOfFMT",
                                               "parsedSummaryRecordSysNumber",
                                               "summaryRecordSysNumber"])):
    """
    This structure is used to represent informations about export progress in
    Aleph.

    It contains informations about state of the record, so it can be tracked
    from edeposit project.

    Attributes:
        hasAcquisitionFields (bool): Was the record aproved by acquisition?
        acquisitionFields (list): Acquisition fields if it the record was
            signed.
        isClosed (bool): Was the record closed? This sometimes happen when bad
            ISBN is given by creator of the record, but different is in the
            book.
        isSummaryRecord (bool): Is the content of FMT == "SE"?
        contentOfFMT (str, default ""): Content of FMT subrecord.
        parsedSummaryRecordSysNumber (str): Same as
            :attr:`summaryRecordSysNumber` but without natural language
            details.
        summaryRecordSysNumber (str): Identificator of the new record if
            `.isClosed` is True. Format of the string is not specified and can
            be different for each record.
    """

    @staticmethod
    def from_xml(xml):
        """
        Pick informations from :class:`.MARCXMLRecord` object and use it to
        build :class:`.SemanticInfo` structure.

        Args:
            xml (str/MARCXMLRecord): MarcXML which will be converted to
                SemanticInfo. In case of str, ``<record>`` tag is required.

        Returns:
            structure: :class:`.SemanticInfo`.
        """
        hasAcquisitionFields = False
        acquisitionFields = []
        isClosed = False
        isSummaryRecord = False
        contentOfFMT = ""
        parsedSummaryRecordSysNumber = ""
        summaryRecordSysNumber = ""

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

            if "STZ" in parsed.datafields:
                acquisitionFields.extend(parsed["STZa"])
                acquisitionFields.extend(parsed["STZb"])

        def sign_and_author(sign):
            """
            Sign is stored in ISTa, author's name is in ISTb.

            Sign is MarcSubrecord obj with pointers to other subrecords, so it
            is possible to pick references to author's name from signs.
            """
            return [sign.replace(" ", "")] + sign.other_subfields.get("b", [])

        # look for catalogization fields
        for orig_sign in parsed["ISTa"]:
            sign = orig_sign.replace(" ", "")  # remove spaces

            if sign.startswith("sk"):
                hasAcquisitionFields = True
                acquisitionFields.extend(sign_and_author(orig_sign))

        # look whether the record was 'closed' by catalogizators
        for status in parsed["BASa"]:
            if status == "90":
                isClosed = True

        # if multiple PJM statuses are present, join them together
        status = "\n".join([x for x in parsed["PJMa"]])

        # detect link to 'new' record, if the old one was 'closed'
        if status.strip():
            summaryRecordSysNumber = status
            parsedSummaryRecordSysNumber = _parse_summaryRecordSysNumber(
                summaryRecordSysNumber
            )

        return EPeriodicalSemanticInfo(
            hasAcquisitionFields=hasAcquisitionFields,
            acquisitionFields=acquisitionFields,
            isClosed=isClosed,
            isSummaryRecord=isSummaryRecord,
            contentOfFMT=contentOfFMT,
            parsedSummaryRecordSysNumber=parsedSummaryRecordSysNumber,
            summaryRecordSysNumber=summaryRecordSysNumber,
        )
