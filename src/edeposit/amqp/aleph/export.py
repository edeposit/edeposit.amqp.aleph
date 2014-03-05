#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import isbn
import settings

from httpkie import Downloader()


#= Variables ==================================================================



#= Functions & objects ========================================================
class ExportException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidISBNException(ExportException):
    def __init__(self, message):
        super(InvalidAlephBaseException, self).__init__(message)


class ExportData:
    def __init__(self):
        self.__POST = {
            "sid": settings.EDEPOSIT_EXPORT_SIGNATURE,
            "P0100LDR__": "-----nam-a22------a-4500",
            "P0200FMT__": "BK",
            "P0300BAS__a": "30",
            "P0501010__a": "",    # ISBN (uppercase)
            "P0502010__b": ["brož.", "váz.", "mapa", "CD-ROM", "DVD", "online"],  # vazba/forma
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
            "P1601ISB__a": "",    # Zpracovatel záznamu (hidden)
            # "REPEAT": "Y",        # predvyplnit zaznam
        }

        self. mapping = {
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

    def _postprocess(self):
        isbn_ = self.__POST["P0601010__a"]
        self.__POST["P0601010__a"] = isbn_.upper()

        if not isbn.is_valid_isbn(isbn_):
            raise InvalidISBNException("%s is has invalid checksum!" % isbn_)

        self.__POST["P0601010__b"] = "soubor : " + isbn_

        # some fields need to be remapped (depends on type of media)
        self._apply_mapping(
            self.mapping.get(self.__POST["P0502010__b"], self.mapping["else"])
        )

    def _apply_mapping(self, mapping):
        self.__POST["P0100LDR__"] = maping[0]
        self.__POST["P0502010__b"] = maping[1]
        self.__POST["P07022001_b"] = maping[2]
        self.__POST["P1501IST1_a"] = maping[3]

    def get_POST_data(self):
        return self.__POST



def exportEpublication(epub):
    addr = "http://aleph.nkp.cz/aleph-cgi/isxn"


#= Main program ===============================================================
if __name__ == '__main__':
    pass
