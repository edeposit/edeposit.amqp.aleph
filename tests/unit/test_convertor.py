#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from aleph.datastructures import convertor


# Tests =======================================================================
def test_parse_summaryRecordSysNumber():
    num = convertor._parse_summaryRecordSysNumber(
        "Souborný záznam viz nkc20150003029."
    )

    assert num == "nkc20150003029"

    num = convertor._parse_summaryRecordSysNumber(
        "Souborný záznam viz 978-80-87899-15-1."
    )

    assert num == "978-80-87899-15-1"
