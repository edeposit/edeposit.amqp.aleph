#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import os.path

import pytest

from aleph.datastructures import convertor


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
def pasivni_domy_example():
    return read_file("pasivni_domy.xml")


@pytest.fixture
def echa_example():
    return read_file("echa.xml")


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


def test_toSemanticInfo_unix(unix_example):
    semantic_info = convertor.toSemanticInfo(unix_example)

    assert semantic_info

    assert not semantic_info.isClosed

    # normal records doesn't use semantic info
    assert not semantic_info.hasAcquisitionFields
    assert not semantic_info.hasISBNAgencyFields
    assert not semantic_info.hasDescriptiveCatFields
    assert not semantic_info.hasDescriptiveCatReviewFields
    assert not semantic_info.hasSubjectCatFields
    assert not semantic_info.hasSubjectCatReviewFields
    assert not semantic_info.summaryRecordSysNumber
    assert not semantic_info.parsedSummaryRecordSysNumber
    assert not semantic_info.isSummaryRecord
    assert not semantic_info.contentOfFMT


def test_toSemanticInfo_echa(echa_example):
    semantic_info = convertor.toSemanticInfo(echa_example)

    assert semantic_info

    assert not semantic_info.isClosed

    assert not semantic_info.hasAcquisitionFields
    assert not semantic_info.hasISBNAgencyFields
    assert semantic_info.hasDescriptiveCatFields
    assert not semantic_info.hasDescriptiveCatReviewFields
    assert not semantic_info.hasSubjectCatFields
    assert not semantic_info.hasSubjectCatReviewFields
    assert not semantic_info.summaryRecordSysNumber
    assert not semantic_info.parsedSummaryRecordSysNumber
    assert semantic_info.isSummaryRecord
    assert semantic_info.contentOfFMT == "SE"


def test_toSemanticInfo_pasivni_domy(pasivni_domy_example):
    semantic_info = convertor.toSemanticInfo(pasivni_domy_example)

    assert semantic_info

    assert semantic_info.isClosed

    assert semantic_info.hasAcquisitionFields
    assert  semantic_info.hasISBNAgencyFields
    assert semantic_info.hasDescriptiveCatFields
    assert not semantic_info.hasDescriptiveCatReviewFields
    assert not semantic_info.hasSubjectCatFields
    assert not semantic_info.hasSubjectCatReviewFields
    assert semantic_info.summaryRecordSysNumber == "Seriálový záznam viz nkc20150003043"
    assert semantic_info.parsedSummaryRecordSysNumber == "nkc20150003043"
    assert not semantic_info.isSummaryRecord
    assert semantic_info.contentOfFMT == "BK"


def test_toEPublication_unix(unix_example):
    epub = convertor.toEPublication(unix_example)

    author = convertor.Author(
        firstName='Eric S.',
        lastName='Raymond',
        title=''
    )

    assert epub.ISBN == ['80-251-0225-4']
    assert epub.nazev == "Umění programování v UNIXu /"
    assert epub.podnazev == ""
    assert epub.vazba == '(brož.) :'
    assert epub.cena == "Kč 590,00"
    assert epub.castDil == ""
    assert epub.nazevCasti == ""
    assert epub.nakladatelVydavatel == "Computer Press,"
    assert epub.datumVydani == "2004"
    assert epub.poradiVydani == "1. vyd."
    assert epub.zpracovatelZaznamu == "BOA001"
    assert epub.format == "23 cm"
    assert epub.url == ""
    assert epub.mistoVydani == "Brno :"
    assert epub.ISBNSouboruPublikaci == []
    assert epub.autori == [author]
    assert epub.originaly == ['Art of UNIX programming']
    assert epub.internal_url == ""


def test_toEPublication_echa(echa_example):
    epub = convertor.toEPublication(echa_example)

    author = convertor.Author(
        firstName='Jiří',
        lastName='Brabec',
        title=''
    )

    assert epub.ISBN == []
    assert epub.nazev == "Echa ... :"
    assert epub.podnazev == "[fórum pro literární vědu] /"
    assert epub.vazba == ''
    assert epub.cena == ""
    assert epub.castDil == ""
    assert epub.nazevCasti == ""
    assert epub.nakladatelVydavatel == "Institut pro studium literatury,"
    assert epub.datumVydani == "[2014?]-"
    assert epub.poradiVydani == ""
    assert epub.zpracovatelZaznamu == "ABA001"
    assert epub.format == ""
    assert epub.url == "http://edeposit-test.nkp.cz/producents/nakladatelstvi-delta/epublications/echa-2010-2011/echa-2010-2011-eva-jelinkova-michael-spirit-eds.pdf"
    assert epub.mistoVydani == "Praha :"
    assert epub.ISBNSouboruPublikaci == []
    assert epub.autori == [author]
    assert epub.originaly == []
    assert epub.internal_url == "http://aleph.nkp.cz/F/?func=direct&doc_number=000003059&local_base=CZE-DEP"


def test_toEPublication_pasivni_domy(pasivni_domy_example):
    epub = convertor.toEPublication(pasivni_domy_example)

    author = convertor.Author(
        firstName='Jan',
        lastName='Bárta',
        title=''
    )

    assert epub.ISBN == ['978-80-904739-3-5']
    assert epub.nazev == "Pasivní domy 2013 /"
    assert epub.podnazev == ""
    assert epub.vazba == ''
    assert epub.cena == ""
    assert epub.castDil == ""
    assert epub.nazevCasti == ""
    assert epub.nakladatelVydavatel == "Centrum pasivního domu,"
    assert epub.datumVydani == "2013"
    assert epub.poradiVydani == "[1. vyd.]"
    assert epub.zpracovatelZaznamu == "ABA001"
    assert epub.format == ""
    assert epub.url == "http://edeposit-test.nkp.cz/producents/nakladatelstvi-gama/epublications/pasivni-domy-2013/pd2013_sbornik.pdf"
    assert epub.mistoVydani == "Brno :"
    assert epub.ISBNSouboruPublikaci == []
    assert epub.autori == [] # TODO: [author]
    assert epub.originaly == []
    assert epub.internal_url == "http://aleph.nkp.cz/F/?func=direct&doc_number=000003035&local_base=CZE-DEP"
