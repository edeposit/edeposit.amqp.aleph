#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import os.path

import pytest

from aleph.datastructures import Author
from aleph.datastructures import EPublication


# Fixtures ====================================================================
def example_context(fn):
    return os.path.join(os.path.dirname(__file__), "examples", fn)


def read_file(fn):
    with open(example_context(fn)) as f:
        return f.read()


@pytest.fixture
def unix_example():
    return read_file("unix_example.xml")


@pytest.fixture
def echa_example():
    return read_file("echa.xml")


@pytest.fixture
def pasivni_domy_example():
    return read_file("pasivni_domy.xml")


# Tests =======================================================================
def test_toEPublication_unix(unix_example):
    epub = EPublication.from_xml(unix_example)

    author = Author(
        firstName='Eric S.',
        lastName='Raymond',
        title=''
    )

    assert epub.ISBN == ['80-251-0225-4']
    assert epub.nazev == "Umění programování v UNIXu"
    assert epub.podnazev == ""
    assert epub.vazba == 'brož.'
    assert epub.cena == "Kč 590,00"
    assert epub.castDil == ""
    assert epub.nazevCasti == ""
    assert epub.nakladatelVydavatel == "Computer Press"
    assert epub.datumVydani == "2004"
    assert epub.poradiVydani == "1. vyd."
    assert epub.zpracovatelZaznamu == "BOA001"
    assert epub.format == "23 cm"
    assert epub.url == []
    assert epub.mistoVydani == "Brno"
    assert epub.ISBNSouboruPublikaci == []
    assert epub.autori == [author]
    assert epub.originaly == ['Art of UNIX programming']
    assert epub.internal_url == []
    assert epub.id_number == "cpk20051492461"


def test_toEPublication_echa(echa_example):
    epub = EPublication.from_xml(echa_example)

    author = Author(
        firstName='Jiří',
        lastName='Brabec',
        title=''
    )

    assert epub.ISBN == []
    assert epub.nazev == "Echa ..."
    assert epub.podnazev == "fórum pro literární vědu"
    assert epub.vazba == ''
    assert epub.cena == ""
    assert epub.castDil == ""
    assert epub.nazevCasti == ""
    assert epub.nakladatelVydavatel == "Institut pro studium literatury"
    assert epub.datumVydani == "2014?"
    assert epub.poradiVydani == ""
    assert epub.zpracovatelZaznamu == "ABA001"
    assert epub.format == ""
    assert epub.url == []
    assert epub.mistoVydani == "Praha"
    assert epub.ISBNSouboruPublikaci == []
    assert epub.autori == [author]
    assert epub.originaly == []
    assert epub.internal_url == [
        'http://edeposit-test.nkp.cz/producents/nakladatelstvi-delta/epublications/echa-2010-2011/echa-2010-2011-eva-jelinkova-michael-spirit-eds.pdf',
        'http://edeposit-test.nkp.cz/producents/nakladatelstvi-delta/epublications/echa-2010-2011-1/echa-2010-2011-eva-jelinkova-michael-spirit-eds.epub',
        'http://edeposit-test.nkp.cz/producents/nakladatelstvi-delta/epublications/echa-2010-2011-1/echa-2010-2011-eva-jelinkova-michael-spirit-eds.mobi',
        'http://edeposit-test.nkp.cz/producents/nakladatelstvi-delta/epublications/echa-2012-1/echa-2012-eva-jelinkova-michael-spirit-eds.mobi',
        'http://edeposit-test.nkp.cz/producents/nakladatelstvi-delta/epublications/echa-2010-2011/echa-2013-eva-jelinkova-michael-spirit-eds.epub',
        'http://aleph.nkp.cz/F/?func=direct&doc_number=000003059&local_base=CZE-DEP'
    ]
    assert epub.id_number == "nkc20150003059"


def test_toEPublication_pasivni_domy(pasivni_domy_example):
    epub = EPublication.from_xml(pasivni_domy_example)

    assert epub.ISBN == ['978-80-904739-3-5']
    assert epub.nazev == "Pasivní domy 2013"
    assert epub.podnazev == ""
    assert epub.vazba == ''
    assert epub.cena == ""
    assert epub.castDil == ""
    assert epub.nazevCasti == ""
    assert epub.nakladatelVydavatel == "Centrum pasivního domu"
    assert epub.datumVydani == "2013"
    assert epub.poradiVydani == "1. vyd."
    assert epub.zpracovatelZaznamu == "ABA001"
    assert epub.format == ""
    assert epub.url == ["http://edeposit-test.nkp.cz/"]
    assert epub.mistoVydani == "Brno"
    assert epub.ISBNSouboruPublikaci == []
    assert epub.autori == []
    assert epub.originaly == []
    assert epub.internal_url == [
        'http://edeposit-test.nkp.cz/producents/nakladatelstvi-gama/epublications/pasivni-domy-2013/pd2013_sbornik.pdf',
        'http://aleph.nkp.cz/F/?func=direct&doc_number=000003035&local_base=CZE-DEP'
    ]
    assert epub.id_number == "nkc20150003035"