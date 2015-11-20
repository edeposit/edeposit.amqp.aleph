#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from test_epublication import read_file

from aleph import EPeriodical


# Fixtures ====================================================================
@pytest.fixture
def periodical_example():
    return read_file("periodical.xml")


# Tests =======================================================================
def test_EPeriodical(periodical_example):
    ep = EPeriodical.from_xml(periodical_example)

    internal_urls = set([
        'http://aleph.nkp.cz/F/?func=direct&doc_number=000003391&local_base=CZE-DEP',
        'http://edeposit-test.nkp.cz/@@redirect-to-uuid/e514091c38cf493d8308611d401407f5'
    ])

    assert not ep.url
    assert not ep.ISSN
    assert ep.nazev == "Cestou necestou"
    assert not ep.anotace
    assert ep.podnazev == "zážitky z cest"
    assert ep.id_number == "cps20150003391"
    assert ep.datumVydani == "2015-"
    assert ep.mistoVydani == "Zámecká Lhota"
    assert set(ep.internal_url) == internal_urls
    assert not ep.invalid_ISSNs
    assert ep.nakladatelVydavatel == "Vydavatelství Stáza"
    assert not ep.ISSNSouboruPublikaci
