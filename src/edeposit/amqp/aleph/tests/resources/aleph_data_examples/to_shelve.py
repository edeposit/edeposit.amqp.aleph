#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import os
import os.path
import shelve  # http://www.py.cz/Shelve

import convertor
from marcxml import MARCXMLRecord


#= Variables ==================================================================
SOURCE_DIR = "aleph_sources"


#= Functions & objects ========================================================
def convertToShelve(filename):
    print filename

    data = open(filename).read()
    epub = convertor.toEPublication(data)

    filename = os.path.basename(filename)

    with open("parsed_outputs/" + filename + ".txt", "wt") as f:
        f.write(str(epub))

    with open("xml_outputs/" + filename, "wt") as f:
        f.write(str(MARCXMLRecord(data)))

    f = shelve.open("shelve_files/" + filename + ".shelve")
    f["data"] = epub
    f.close()


#= Main program ===============================================================
if __name__ == '__main__':
    for fn in filter(lambda x: x.endswith(".xml"), os.listdir(SOURCE_DIR)):
        convertToShelve(SOURCE_DIR + "/" + fn)
