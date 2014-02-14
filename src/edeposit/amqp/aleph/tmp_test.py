#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import convertors


def testJSONConvertor():
    data = open(
        "tests/resources/aleph_data_examples/aleph_sources/example.xml"
    ).read()

    epub = convertors.toEPublication(data)
    epub2 = convertors.fromJSON(convertors.toJSON(epub))

    assert(epub == epub2)


#= Main program ===============================================================
if __name__ == '__main__':
    testJSONConvertor()

    print "Everything is ok."
