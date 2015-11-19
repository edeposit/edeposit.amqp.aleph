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
                                               "id_number",
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
                                               'format',
                                               'url',
                                               'mistoVydani',
                                               'ISBNSouboruPublikaci',
                                               'autori',
                                               'originaly',
                                               'internal_url',
                                               'anotace'])):
    """
    This structure is returned as result of users :class:`.SearchRequest`.

    In case of :class:`Search <.SearchRequest>`/:class:`Count <.CountRequest>`
    requests, this structure is filled with data from MARC XML record.

    Attributes:
        url    (str): Url specified by publisher (THIS IS NOT INTERNAL URL!).
        ISBN  (list): List of ISBNs for the book.
        cena   (str): Price of the book.
        vazba  (str): Bidding of the book.
        nazev  (str): Name of the book.
        format (str): Format of the book - see :class:`FormatEnum`.
        autori (list): List of :class:`Author` objects.
        castDil (str): Which part of the series of books is this.
        anotace (str): Anotation. Max lenght: 500 chars..
        podnazev (str): Subname of the book.
        id_number  (str): Identification number in aleph - starts.
        originaly (list): List of (str) ISBN's of original books in case of
                          translations.
        nazevCasti (str): Name of part of the series.
        datumVydani (str): Date of publication.
        mistoVydani (str): City/country origin of the publication.
        internal_url (str): Link to edeposit/kramerius system.
        poradiVydani (str): Order of publication.
        invalid_ISBN (list): List of INVALID ISBNs for this book.
        zpracovatelZaznamu   (str): Processor/manufacturer of record.
                             with nkc - ``nkc20150003133``.
        nakladatelVydavatel  (str): Publisher's name.
        ISBNSouboruPublikaci (list): List of strings with ISBN of the book
                                     series.
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
            id_number           = parsed.controlfields.get("001", None),
            nazev               = parsed.get_name(),
            podnazev            = parsed.get_subname(),
            vazba               = _first_or_blank_string(parsed.get_binding()),
            cena                = parsed.get_price(),
            castDil             = parsed.get_part(),
            nazevCasti          = parsed.get_part_name(),
            nakladatelVydavatel = parsed.get_publisher(),
            datumVydani         = parsed.get_pub_date(),
            poradiVydani        = parsed.get_pub_order(),
            zpracovatelZaznamu  = _first_or_blank_string(parsed["040a"]),
            format              = parsed.get_format(),
            url                 = parsed.get_urls(),
            mistoVydani         = parsed.get_pub_place(),
            ISBNSouboruPublikaci= [],
            autori              = authors,
            originaly           = parsed.get_originals(),
            internal_url        = parsed.get_internal_urls(),
            anotace             = None, # TODO: read the annotation
        )
