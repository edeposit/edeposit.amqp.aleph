#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple

from marcxml_parser import MARCXMLRecord

from .author import Author
from .format_enum import FormatEnum

from ..aleph import DocumentNotFoundException


# Functions ===================================================================
def _first_or_blank_string(items):
    """
    Return first `item` from `items` or blank string.

    Args:
        items (list/tuple): Indexable object.

    Returns:
        str: Content of first item, or blank string.
    """
    if not items:
        return ""

    return items[0]


# Structures ==================================================================
class EPublication(namedtuple("EPublication", ["ISBN",
                                               "invalid_ISBN",
                                               'nazev',
                                               'podnazev',
                                               'vazba',
                                               'cena',
                                               'castDil',
                                               'nazevCasti',
                                               'nakladatelVydavatel',
                                               'datumVydani',
                                               'poradiVydani',
                                               'zpracovatelZaznamu',
                                               # 'mistoDistribuce',  # FUTURE
                                               # 'distributor',
                                               # 'datumDistribuce',
                                               # 'datumProCopyright',
                                               'format',
                                               'url',
                                               'mistoVydani',
                                               'ISBNSouboruPublikaci',
                                               'autori',
                                               'originaly',
                                               'internal_url'])):
    """
    This structure is returned as result of users :class:`.SearchRequest`. It
    will be also used in exporting new data to aleph, but that is not
    implemented yet.

    In case of :class:`Search <.SearchRequest>`/:class:`Count <.CountRequest>`
    requests, this structure is filled with data from MARC XML record.

    Attributes:
        url    (str): url specified by publisher (THIS IS NOT INTERNAL URL!)
        ISBN  (list): List of ISBNs for the book
        cena   (str): price of the book
        vazba  (str): bidding of the book
        nazev  (str): name of the book
        format (str): format of the book - see :class:`FormatEnum`
        autori (list): list of :class:`Author` objects
        castDil (str): which part of the series of books is this
        podnazev (str): subname of the book
        originaly (list): list of (str) ISBN's of original books in case of
                          translations
        nazevCasti (str): name of part of the series
        datumVydani (str): date of publication
        mistoVydani (str): city/country origin of the publication
        internal_url (str): link to edeposit/kramerius system
        poradiVydani (str): order of publication
        invalid_ISBN (list): List of INVALID ISBNs for this book.
        zpracovatelZaznamu   (str):  processor/manufacturer of record
        nakladatelVydavatel  (str):  publisher's name
        ISBNSouboruPublikaci (list): list of strings with ISBN of the book
                                     series
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

        # i know, that this is not PEP8, but you dont want to see it without
        # proper formating (it looks bad, really bad)
        return EPublication(
            ISBN                = parsed.get_ISBNs(),
            invalid_ISBN        = parsed.get_invalid_ISBNs(),
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


# class Producent(namedtuple("Producent", ['title',
#                                          'phone',
#                                          'fax',
#                                          'email',
#                                          'url',
#                                          'identificator',
#                                          'ico'])):
#     pass


# class OriginalFile(namedtuple("OriginalFile", ['url',
#                                                'format',
#                                                'file',
#                                                'isbns'])):
#     """ type of isbn: ISBN"""
#     pass
