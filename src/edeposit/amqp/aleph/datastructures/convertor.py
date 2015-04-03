#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module exists to provide ability to convert from Aleph's data structures
to AMQP data structures, specifically to convert :class:`.MARCXMLRecord` to
:class:`.EPublication` simplified data structure.
"""
# Imports =====================================================================
import dhtmlparser


# Functions & objects =========================================================
def getDocNumber(xml):
    """
    Parse <doc_number> tag from `xml`.

    Args:
        xml (str): XML string returned from :func:`aleph.aleph.downloadRecords`

    Returns:
        str: Doc ID as string or "-1" if not found.
    """
    dom = dhtmlparser.parseString(xml)

    doc_number_tag = dom.find("doc_number")

    if not doc_number_tag:
        return "-1"

    return doc_number_tag[0].getContent().strip()
