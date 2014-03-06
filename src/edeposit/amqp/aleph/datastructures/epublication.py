#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from collections import namedtuple


class FormatEnum:
    BROZ = "brož."
    VAZANA = "váz."
    MAPA = "mapa"
    CD = "CD-ROM"
    DVD = "DVD"
    ONLINE = "online"


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
    This structure is returned as result of users SearchRequest. It will be
    also used in exporting new data to aleph, but that is not implemented yet.

    In case of Search/Count requests, this structure is filled with data from
    MARC XML record parsed by marcxml.py.

    Properties:

        .url    -- url specified by publisher (THIS IS NOT INTERNAL URL!)
        .ISBN   -- ISBN of the book
        .cena   -- price of the book
        .nazev  -- name of the book
        .format -- format of the book - see FormatEnum
        .autori     -- list of Author objects
        .castDil    -- which part of the series of books is this
        .podnazev   -- subname of the book
        .originaly  -- list of ISBN's of original books in case of
                       translations
        .nazevCasti -- name of part of the series
        .datumVydani  -- date of publication
        .mistoVydani  -- city/country origin of the publication
        .internal_url -- link to edeposit/kramerius system
        .poradiVydani -- order of publication
        .zpracovatelZaznamu   -- processor/manufacturer of record
        .nakladatelVydavatel  -- publisher's name
        .ISBNSouboruPublikaci -- ISBN of the book series
    """
    pass


class Author(namedtuple("Author", ['firstName', 'lastName', 'title'])):
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
