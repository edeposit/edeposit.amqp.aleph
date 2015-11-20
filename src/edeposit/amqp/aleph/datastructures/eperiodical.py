#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
# Imports =====================================================================
from collections import namedtuple

from marcxml_parser import MARCXMLRecord

from .author import Author
from .format_enum import FormatEnum

from ..aleph import DocumentNotFoundException


# Structures ==================================================================
class EPeriodical(namedtuple("EPeriodical", ["url",
                                             "ISSN",
                                             "invalid_ISSNs",
                                             "nazev",
                                             "anotace",
                                             "podnazev",
                                             "id_number",
                                             "mistoVydani",
                                             "datumVydani",
                                             "internal_url",
                                             "nakladatelVydavatel",
                                             "ISSNSouboruPublikaci"])):
    """
    This structure is returned as result of users :class:`.SearchRequest`.

    In case of :class:`Search <.SearchRequest>`/:class:`Count <.CountRequest>`
    requests, this structure is filled with data from MARC XML record.

    Attributes:
        url (str): Url specified by publisher (THIS IS NOT INTERNAL URL!).
        ISSN (list): List of ISSNs for the periodical.
        invalid_ISSNs (list): List of INVALID ISSNs for this book.
        nazev (str): Name of the periodical.
        anotace (str): Anotation. Max lenght: 500 chars.
        podnazev (str): Subname of the book.
        id_number  (str): Identification number in aleph.
        mistoVydani (str): City/country origin of the publication.
        datumVydani (str): Date of publication.
        internal_url (str): Link to edeposit/kramerius system.
        nakladatelVydavatel (str): Publisher's name.
        ISSNSouboruPublikaci (list): ISSN links to other things.
    """

    @staticmethod
    def from_xml(xml):
        """
        Convert :class:`.MARCXMLRecord` object to :class:`.EPublication`
        namedtuple.

        Args:
            xml (str/MARCXMLRecord): MARC XML which will be converted to
                EPublication. In case of str, ``<record>`` tag is required.

        Returns:
            structure: :class:`.EPublication` namedtuple with data about \
                       publication.
        """
        parsed = xml
        if not isinstance(xml, MARCXMLRecord):
            parsed = MARCXMLRecord(str(xml))

        # check whether the document was deleted
        if "DEL" in parsed.datafields:
            raise DocumentNotFoundException("Document was deleted.")

        # i know, that this is not PEP8, but you dont want to see it without
        # proper formating (it looks bad, really bad)
        return EPeriodical(
            url=parsed.get_urls(),
            ISSN=parsed.get_ISSNs(),
            nazev=parsed.get_name(),
            anotace=None,  # TODO: read the annotation
            podnazev=parsed.get_subname(),
            id_number=parsed.controlfields.get("001", None),
            datumVydani=parsed.get_pub_date(),
            mistoVydani=parsed.get_pub_place(),
            internal_url=parsed.get_internal_urls(),
            invalid_ISSNs=parsed.get_invalid_ISSNs(),
            nakladatelVydavatel=parsed.get_publisher(),
            ISSNSouboruPublikaci=parsed.get_linking_ISSNs(),
        )
