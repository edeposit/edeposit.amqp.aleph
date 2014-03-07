#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is used to put data to Aleph.

It is based on custom made webform, which is currently used to report new
books by publishers.

Source code of this form is not available at this moment (it was created by
third party), but it is possible, that it will be in future. This will highly
depend on number of people, which will use this project.

Most important function from this module is exportEPublication(epub), which
will do everything, that is needed to do, to export EPublication structure to
the Aleph.

This whole module is highly dependent on processes, which are defined as import
processes at the Czech National Library.

If you want to use export ability in your library, you should rewrite this and
take care, that you are sending data somewhere, where someone will process
them. Otherwise, you can fill your library's database with crap.
"""
#= Imports ====================================================================
import isbn
import settings
from datastructures import FormatEnum

from httpkie import Downloader


#= Functions & objects ========================================================
class ExportException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidISBNException(ExportException):
    def __init__(self, message):
        super(InvalidISBNException, self).__init__(message)


class ExportRejectedException(ExportException):
    def __init__(self, message):
        super(ExportRejectedException, self).__init__(message)


class PostData:
    """
    This class is used to transform data from EPublication to dictionary, which
    is sent as POST request to Aleph third-party webform.

    http://aleph.nkp.cz/F/?func=file&file_name=service-isbn

    Class is used, because there is 29 POST parameters with internal
    dependencies, which need to be processed and validated before they can be
    passed to webform.
    """
    def __init__(self, epub):
        self._POST = {
            "sid": settings.EDEPOSIT_EXPORT_SIGNATURE,
            "P0100LDR__": "-----nam-a22------a-4500",
            "P0200FMT__": "BK",
            "P0300BAS__a": "30",
            "P0501010__a": "",    # ISBN (uppercase)
            "P0502010__b": "",    # vazba/forma
            "P0504010__d": "",    # cena
            # "P1201901__b": "",    # ean
            "P0601010__a": "",    # ISBN souboru
            "P0602010__b": "",    # same thing
            "P07012001_a": "",    # název
            "P07022001_b": "",    # vyplneno na zaklade vazby/formy
            "P07032001_e": "",    # podnázev
            "P07042001_h": "",    # Část (svazek, díl)
            "P07052001_i": "",    # Název části
            "P1301ZAK__b": "",    # autor
            "P1302ZAK__c": "",    # autor2
            "P1303ZAK__c": "",    # autor3
            "P10012252_a": "",    # edice
            "P10022252_v": "",    # Číslo svazku
            "P110185640u": "",    # URL
            "P0503010__x": "",    # Formát (poze pro epublikace)
            "P0901210__a": "",    # Místo vydání
            "P0902210__c": "",    # Nakladatel
            "P0903210__d": "",    # Měsíc a rok vydání
            "P1401PJM__a": "",    # Vydáno v koedici s
            "P0801205__a": "",    # Pořadí vydání
            "P1501IST1_a": "ow",  # Zpracovatel záznamu (hidden)
            "P1502IST1_b": "",    # Zpracovatel záznamu (viditelna)
            "P1601ISB__a": "",    # ISBN2 - validated (hidden)
            # "REPEAT": "Y",        # predvyplnit zaznam
        }

        self.mapping = {
            "mapa": [
                "-----nem-a22------a-4500",
                "MP",
                "30",
                "kartografický dokument",
                "ow"
            ],
            "CD-ROM": [
                "-----nam-a22------a-4500",
                "BK",
                "30",
                "elektronický zdroj",
                "ow"
            ],
            "online": [
                "-----nam-a22------a-4500",
                "BK",
                "49",
                "elektronický zdroj",
                "ox",
            ],
            "else": [
                "-----nam-a22------a-4500",
                "BK",
                "30",
                "",
                "ow"
            ]
        }
        self.mapping["DVD"] = self.mapping["CD-ROM"]

        self._import_epublication(epub)

    def _import_epublication(self, epub):
        """
        Fill internal property ._POST dictionary with data from EPublication.
        """
        self._POST["P0501010__a"] = epub.ISBN
        self._POST["P07012001_a"] = epub.nazev
        self._POST["P07032001_e"] = epub.podnazev
        self._POST["P0502010__b"] = epub.vazba
        self._POST["P0504010__d"] = epub.cena
        self._POST["P07042001_h"] = epub.castDil
        self._POST["P07052001_i"] = epub.nazevCasti
        self._POST["P0902210__c"] = epub.nakladatelVydavatel
        self._POST["P0903210__d"] = epub.datumVydani
        self._POST["P0801205__a"] = epub.poradiVydani
        self._POST["P1502IST1_b"] = epub.zpracovatelZaznamu
        self._POST["P0503010__x"] = epub.format
        self._POST["P110185640u"] = epub.url
        self._POST["P0901210__a"] = epub.mistoVydani
        self._POST["P0601010__a"] = epub.ISBNSouboruPublikaci

        # FUTURE:
        # self._POST[""] = epub.mistoDistribuce
        # self._POST[""] = epub.distributor
        # self._POST[""] = epub.datumDistribuce
        # self._POST[""] = epub.kategorieProRIV  # TODO: wtf?
        # self._POST[""] = epub.datumProCopyright  # wut

        authors = [x.lastName + ", " + x.firstName for x in epub.autori]
        authors_fields = ["P1301ZAK__b", "P1302ZAK__c", "P1303ZAK__c"]
        for field, author in zip(authors_fields, authors):
            self._POST[field] = author

    def _apply_mapping(self, mapping):
        """
        Map some case specific data to the fields in internal dictionary.
        """
        self._POST["P0100LDR__"] = mapping[0]
        self._POST["P0200FMT__"] = mapping[1]
        self._POST["P0502010__b"] = mapping[2]
        self._POST["P07022001_b"] = mapping[3]
        self._POST["P1501IST1_a"] = mapping[4]

    def _postprocess(self):
        """
        Move data between internal fields, validate them and make sure, that
        everything is as it should be.
        """
        # get ISBN of serie
        series_isbn = self._POST["P0601010__a"]
        if isinstance(series_isbn, list) and len(series_isbn) > 0:
            series_isbn = series_isbn[0]

        # try to validate series ISBN
        if series_isbn != "" and series_isbn != []:
            series_isbn = series_isbn.upper()
            self._POST["P0601010__a"] = series_isbn

            if not isbn.is_valid_isbn(series_isbn):
                raise InvalidISBNException(
                    "%s is has invalid ISBN checksum!" % series_isbn
                )

            self._POST["P0601010__b"] = "soubor : " + series_isbn

        # validate ISBN of the book
        book_isbn = self._POST["P0501010__a"]
        if isinstance(book_isbn, list) and len(book_isbn) > 0:
            book_isbn = book_isbn[0]

        if not isbn.is_valid_isbn(book_isbn):
            raise InvalidISBNException(
                "%s is has invalid ISBN checksum!" % book_isbn
            )
        self._POST["P0501010__a"] = book_isbn
        self._POST["P1601ISB__a"] = book_isbn

        # some fields need to be remapped (depends on type of media)
        self._apply_mapping(
            self.mapping.get(self._POST["P0502010__b"], self.mapping["else"])
        )

        # # clean the dict before you send it
        # for key in self._POST.keys():
        #     if self._POST[key] == "":
        #         del self._POST[key]

    def _check_required_fields(self):
        """
        Make sure, that internal dictionary contains all fields, which are
        requiered by the webform.
        """
        assert(self._POST["P0501010__a"] != "")  # ISBN
        assert(self._POST["P1601ISB__a"] != "")  # hidden ISBN field

        assert(self._POST["P07012001_a"] != "")  # nazev
        assert(self._POST["P0901210__a"] != "")  # Místo vydání

        assert(self._POST["P0903210__d"] != "")  # Měsíc a rok vydání
        assert(self._POST["P0801205__a"] != "")  # Pořadí vydání

        # Zpracovatel záznamu
        assert(self._POST["P1501IST1_a"] != "")  # (hidden)
        assert(self._POST["P1502IST1_b"] != "")  # (visible)

        # vazba/forma
        assert(self._POST["P0502010__b"] != "")

        # Formát (poze pro epublikace)
        if self._POST["P0502010__b"] == FormatEnum.ONLINE:
            assert(self._POST["P0503010__x"] != "")

        assert(self._POST["P0902210__c"] != "")  # Nakladatel

    def get_POST_data(self):
        self._postprocess()
        self._check_required_fields()

        return self._POST


def _sendPostDict(post_dict):
    """
    Send `post_dict` to the settigns.ALEPH_EXPORT_URL.

    It may look strange, to have standalone function to do this, but it is used
    in unittests to test that form rejects invalid data, which can tell us,
    when the webform is broken.
    """
    downer = Downloader()
    data = downer.download(settings.ALEPH_EXPORT_URL, post=post_dict)

    if "Požadavek byl odmítnut" in data:
        raise ExportRejectedException("Export was rejected by Aleph form!")

    return data


def exportEPublication(epub):
    """
    Send `epub` EPublication object to Aleph, where it will be processed by
    librarians.
    """
    post_dict = PostData(epub).get_POST_data()
    # sendPostDict(post_dict)  # TODO: uncoment, when test settings at the webform will be implemented
