#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from collections import namedtuple


class FormatEnum:
    """
    Enum used as format in :class:`EPublication`.
    """
    CD = "CD-ROM"
    DVD = "DVD"
    BROZ = "brož."
    MAPA = "mapa"
    VAZANA = "váz."
    ONLINE = "online"


class Author(namedtuple("Author", ['firstName', 'lastName', 'title'])):
    """
    Informations about author (or person).

    Attributes:
        firstName (str)
        lastName (str)
        title (str)
    """
    pass


class EPublication(namedtuple("EPublication", ["ISBN",
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
    requests, this structure is filled with data from MARC XML record parsed
    by :mod:`marcxml.py <aleph.marcxml>`.

    Attributes:
        url    (str): url specified by publisher (THIS IS NOT INTERNAL URL!)
        ISBN   (str): ISBN of the book
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
        zpracovatelZaznamu   (str):  processor/manufacturer of record
        nakladatelVydavatel  (str):  publisher's name
        ISBNSouboruPublikaci (list): list of strings with ISBN of the book
                                     series
    """
    pass


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
