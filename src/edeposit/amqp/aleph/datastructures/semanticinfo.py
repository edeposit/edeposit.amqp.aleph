#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Definition of structures, which are used to hold informations about
catalogization process.
"""
# Imports =====================================================================
from collections import namedtuple


from remove_hairs import remove_hairs
from marcxml_parser import MARCXMLRecord


# Functions ===================================================================
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


# Structures ==================================================================
class SemanticInfo(namedtuple("SemanticInfo", ["hasAcquisitionFields",
                                               "acquisitionFields",
                                               "ISBNAgencyFields",
                                               "descriptiveCatFields",
                                               "descriptiveCatReviewFields",
                                               "subjectCatFields",
                                               "subjectCatReviewFields",
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

    See :func:`.toSemanticInfo` for details of parsing of those attributes.

    Attributes:
        hasAcquisitionFields (bool): Was the record aproved by acquisition?
        acquisitionFields (list): Acquisition fields if it the record was
            signed.
        ISBNAgencyFields (list): Was the record approved by ISBN agency?
            Contains list of signs if it the record was signed.
        descriptiveCatFields (list): Did the record get thru name description
            (jmenný popis). Contains list of signs if it the record was signed.
        descriptiveCatReviewFields (list): Did the record get thru name
            revision (jmenná revize). Contains list of signs if it the record
            was signed.
        subjectCatFields (list): Did the record get thru subject description
            (věcný popis). Contains list of signs if it the record was signed.
        subjectCatReviewFields (list): Did the record get thru subject revision
            (věcná revize). Contains list of signs if the record was signed.
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
        ISBNAgencyFields = []
        descriptiveCatFields = []
        descriptiveCatReviewFields = []
        subjectCatFields = []
        subjectCatReviewFields = []
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

            if sign.startswith("jp2"):
                descriptiveCatFields.extend(sign_and_author(orig_sign))
            elif sign.startswith("jr2"):
                descriptiveCatReviewFields.extend(sign_and_author(orig_sign))
            elif sign.startswith("vp"):
                subjectCatFields.extend(sign_and_author(orig_sign))
            elif sign.startswith("vr"):
                subjectCatReviewFields.extend(sign_and_author(orig_sign))
            elif sign.startswith("ii2"):
                ISBNAgencyFields.extend(sign_and_author(orig_sign))

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

        return SemanticInfo(
            hasAcquisitionFields=hasAcquisitionFields,
            acquisitionFields=acquisitionFields,
            ISBNAgencyFields=ISBNAgencyFields,
            descriptiveCatFields=descriptiveCatFields,
            descriptiveCatReviewFields=descriptiveCatReviewFields,
            subjectCatFields=subjectCatFields,
            subjectCatReviewFields=subjectCatReviewFields,
            isClosed=isClosed,
            isSummaryRecord=isSummaryRecord,
            contentOfFMT=contentOfFMT,
            parsedSummaryRecordSysNumber=parsedSummaryRecordSysNumber,
            summaryRecordSysNumber=summaryRecordSysNumber,
        )
