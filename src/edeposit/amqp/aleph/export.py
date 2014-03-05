#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from httpkie import Downloader()


#= Variables ==================================================================



#= Functions & objects ========================================================
def exportEpublication(epub):
    addr = "http://aleph.nkp.cz/aleph-cgi/isxn"

    POST_REQUEST = {
        "sid": "AJKL1KPBSQ9ITQ3JY5PG3IPR8X3VU6SIHR37NMHI8PQEG67T2E",
        "P0100LDR__": "-----nam-a22------a-4500",
        "P0200FMT__": "BK",
        "P0300BAS__a": "30",
        "P0502010__b": ["brož.", "váz.", "mapa", "CD-ROM", "DVD", "online"],
        "P0501010__a": "",
        "P0502010__b": "",
        "P0504010__d": "",
        "P1201901__b": "",
        "P0601010__a": "",
        "P0602010__b": "",
        "P07012001_a": "",
        "P07022001_b": "",
        "P07032001_e": "",
        "P07042001_h": "",
        "P07052001_i": "",
        "P1301ZAK__b": "",
        "P1302ZAK__c": "",
        "P1303ZAK__c": "",
        "P10012252_a": "",
        "P10022252_v": "",
        "P110185640u": "",
        "P0503010__x": "",
        "P0901210__a": "",
        "P0902210__c": "",
        "P0903210__d": "",
        "P1401PJM__a": "",
        "P0801205__a": "",
        "P1501IST1_a": "ow",
        "P1502IST1_b": "",
        "P1601ISB__a": "",
        "REPEAT": "Y",
}


#= Main program ===============================================================
if __name__ == '__main__':
    pass
