#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
# This work is licensed under a Creative Commons 3.0 Unported License
# (http://creativecommons.org/licenses/by/3.0/).
#
#= Imports ====================================================================
from __init__ import Producent, EPublication, OriginalFile, Author
import dhtmlparser


#= Variables ==================================================================



#= Functions & objects ========================================================
class MARCXmlRecord:
    def __init__(self, xml=None):
        self.controlfields = {}
        self.datafields = {}

        if xml is not None:
            self.parseString(xml)

    def parseString(self, xml):
        if not isinstance(xml, dhtmlparser.HTMLElement):
            xml = dhtmlparser.parseString(str(xml))

        record = xml.find("record")

        if len(record) <= 0:
            raise ValueError("There is no <record> in your MARCXML document!")

        record = record[0]  # TODO: možná opravit na postupné rozparsování?

        self.__parseControlFields(record.find("controlfield"))
        self.__parseDataFields(record.find("datafield"))

    def __parseControlFields(self, fields):
        for field in fields:
            params = field.params
            if "tag" not in params:
                continue

            self.controlfields[params["tag"]] = field.getContent().strip()

    def __parseDataFields(self, fields):
        for field in fields:
            params = field.params

            if "tag" not in params:
                continue

            tag = params["tag"]
            self.controlfields[tag] = {
                "i1": "" if "i1" not in params else params["i1"],
                "i2": "" if "i2" not in params else params["i2"],
            }

            for subfield in field.find("subfield"):
                if "code" not in subfield.params:
                    continue
                code = subfield.params["code"]

                self.controlfields[tag][code] = subfield.getContent().strip()




def toEpublication(marcxml):
    pass


def fromEpublication(epublication):
    pass


#= Main program ===============================================================
if __name__ == '__main__':
    r = MARCXmlRecord(open("example.xml").read())

    print r.controlfields["245"]["a"]
