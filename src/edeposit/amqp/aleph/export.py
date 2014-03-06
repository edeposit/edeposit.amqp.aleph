#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import isbn
import settings
from datastructures import FormatEnum

from httpkie import Downloader


#= Variables ==================================================================



#= Functions & objects ========================================================
class ExportException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidISBNException(ExportException):
    def __init__(self, message):
        super(InvalidISBNException, self).__init__(message)


class ExportData:
    def __init__(self, epub):
        self.__POST = {
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
        self.__POST["P0501010__a"] = epub.ISBN
        self.__POST["P07012001_a"] = epub.nazev
        self.__POST["P07032001_e"] = epub.podnazev
        self.__POST["P0502010__b"] = epub.vazba
        self.__POST["P0504010__d"] = epub.cena
        self.__POST["P07042001_h"] = epub.castDil
        self.__POST["P07052001_i"] = epub.nazevCasti
        self.__POST["P0902210__c"] = epub.nakladatelVydavatel
        self.__POST["P0903210__d"] = epub.datumVydani
        self.__POST["P0801205__a"] = epub.poradiVydani
        self.__POST["P1502IST1_b"] = epub.zpracovatelZaznamu
        self.__POST["P0503010__x"] = epub.format
        self.__POST["P110185640u"] = epub.url
        self.__POST["P0901210__a"] = epub.mistoVydani
        self.__POST["P0601010__a"] = epub.ISBNSouboruPublikaci

        # FUTURE:
        # self.__POST[""] = epub.mistoDistribuce
        # self.__POST[""] = epub.distributor
        # self.__POST[""] = epub.datumDistribuce
        # self.__POST[""] = epub.kategorieProRIV  # TODO: wtf?
        # self.__POST[""] = epub.datumProCopyright  # wut

        authors = [x.lastName + ", " + x.firstName for x in epub.autori]
        authors_fields = ["P1301ZAK__b", "P1302ZAK__c", "P1303ZAK__c"]
        for field, author in zip(authors_fields, authors):
            self.__POST[field] = author

    def _apply_mapping(self, mapping):
        self.__POST["P0100LDR__"] = mapping[0]
        self.__POST["P0200FMT__"] = mapping[1]
        self.__POST["P0502010__b"] = mapping[2]
        self.__POST["P07022001_b"] = mapping[3]
        self.__POST["P1501IST1_a"] = mapping[4]

    def _postprocess(self):
        # get ISBN of serie
        series_isbn = self.__POST["P0601010__a"]
        if isinstance(series_isbn, list) and len(series_isbn) > 0:
            series_isbn = series_isbn[0]

        # try to validate series ISBN
        if series_isbn != "" and series_isbn != []:
            series_isbn = series_isbn.upper()
            self.__POST["P0601010__a"] = series_isbn

            if not isbn.is_valid_isbn(series_isbn):
                raise InvalidISBNException(
                    "%s is has invalid ISBN checksum!" % series_isbn
                )

            self.__POST["P0601010__b"] = "soubor : " + series_isbn

        book_isbn = self.__POST["P0501010__a"]
        if isinstance(book_isbn, list) and len(book_isbn) > 0:
            book_isbn = book_isbn[0]

        if not isbn.is_valid_isbn(book_isbn):
            raise InvalidISBNException(
                "%s is has invalid ISBN checksum!" % book_isbn
            )
        self.__POST["P0501010__a"] = book_isbn
        self.__POST["P1601ISB__a"] = book_isbn

        # some fields need to be remapped (depends on type of media)
        self._apply_mapping(
            self.mapping.get(self.__POST["P0502010__b"], self.mapping["else"])
        )

    def _check_required_fields(self):
        assert(self.__POST["P0501010__a"] != "")  # ISBN
        assert(self.__POST["P1601ISB__a"] != "")  # hidden ISBN field

        assert(self.__POST["P07012001_a"] != "")  # nazev
        assert(self.__POST["P0901210__a"] != "")  # Místo vydání

        assert(self.__POST["P0903210__d"] != "")  # Měsíc a rok vydání
        assert(self.__POST["P0801205__a"] != "")  # Pořadí vydání

        # Zpracovatel záznamu
        assert(self.__POST["P1501IST1_a"] != "")  # (hidden)
        assert(self.__POST["P1502IST1_b"] != "")  # (visible)

        # vazba/forma
        assert(self.__POST["P0502010__b"] != "")

        # Formát (poze pro epublikace)
        if self.__POST["P0502010__b"] == FormatEnum.ONLINE:
            assert(self.__POST["P0503010__x"] != "")

        assert(self.__POST["P0902210__c"] != "")  # Nakladatel

    def get_POST_data(self):
        self._postprocess()
        self._check_required_fields()

        return self.__POST


def exportEpublication(epub):
    # ALEPH_EXPORT_URL

    POST = ExportData(epub).get_POST_data()

    print POST


#= Main program ===============================================================
if __name__ == '__main__':
    f = open("tests/resources/aleph_data_examples/aleph_sources/example4.xml")
    data = f.read()
    f.close()

    import convertors
    epub = convertors.toEPublication(data)

    exportEpublication(epub)
