#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time

import pytest

from edeposit.amqp.aleph import aleph


# Variables ===================================================================
# Functions & objects =========================================================
def sleep_some():
    """
    Aleph has it's limits to max. users connected in one second.

    This helps to keep those limits in norm.
    """
    time.sleep(0.2)


# Tests =======================================================================
def test_getListOfBases():
    bases = aleph.getListOfBases()

    assert "nkc" in bases


def test_searchInAleph():
    result = aleph.searchInAleph("nkc", "unixu", False, "wtl")

    assert "session-id" in result
    assert "set_number" in result

    assert "no_records" in result
    assert "no_entries" in result

    assert result["no_records"] >= 1
    assert result["no_entries"] >= 1

    sleep_some()


def test_searchInAleph_fail():
    with pytest.raises(aleph.InvalidAlephFieldException):
        aleph.searchInAleph("nkc", "unixu", False, "azgabash")

    sleep_some()

    result = aleph.searchInAleph("nkc", "azgabash", False, "wtl")

    sleep_some()

    assert "error" in result

    with pytest.raises(aleph.AlephException):
        aleph.searchInAleph("nkf", "unixu", False, "azgabash")

    sleep_some()


def test_downloadRecords():
    result = aleph.searchInAleph("nkc", "unixu", False, "wtl")

    records = aleph.downloadRecords(result)

    assert len(records) >= 5
    assert "xml" in records[0]

    sleep_some()


def test_getDocumentIDs():
    result = aleph.searchInAleph("nkc", "unixu", False, "wtl")

    records = aleph.getDocumentIDs(result)

    assert len(records) >= 5
    assert isinstance(records[0], aleph.DocumentID)

    sleep_some()


def test_downloadMARCXML():
    result = aleph.searchInAleph("nkc", "unixu", False, "wtl")
    records = aleph.getDocumentIDs(result)

    record = aleph.downloadMARCXML(records[0].id, records[0].library)

    assert "MARC21slim" in record
    assert "controlfield" in record
    assert "datafield" in record
    assert "subfield" in record

    sleep_some()


def test_downloadMARCOAI():
    result = aleph.searchInAleph("nkc", "unixu", False, "wtl")
    records = aleph.getDocumentIDs(result)

    record = aleph.downloadMARCOAI(records[0].id, records[0].library)

    assert "<oai_marc" in record
    assert "varfield" in record
    assert "fixfield" in record
    assert "subfield" in record

    sleep_some()


# Tests of highlevel API ======================================================
def test_getISBNsXML():
    result = aleph.getISBNsXML("80-86056-31-7")

    assert len(result) == 1
    assert "Zen a umění Internetu" in result[0]

    sleep_some()


def test_get_ISBNsXML_fail():
    result = aleph.getISBNsXML("80-86056-31-8")

    assert not result

    sleep_some()


def test_getAuthorsBooksXML():
    result = aleph.getAuthorsBooksXML("Brendan Kehoe")

    assert len(result) >= 1
    assert "Zen a umění Internetu" in result[0]

    sleep_some()


def test_getAuthorsBooksXML_fail():
    result = aleph.getAuthorsBooksXML("Brendan Kehoeeeeeeeeeeeee")

    assert not result

    sleep_some()


def test_getPublishersBooksXML():
    result = aleph.getPublishersBooksXML("Nostromo")

    assert len(result) >= 1
    assert "Čakra kentaura" in result[0].lower()

    sleep_some()


def test_getPublishersBooksXML_fail():
    result = aleph.getPublishersBooksXML("Nostromooooo")

    assert not result

    sleep_some()


def test_getBooksTitleXML():
    result = aleph.getBooksTitleXML("Zen a umění Internetu")

    assert len(result) >= 1
    assert "Zen a umění Internetu" in result[0]

    sleep_some()


def test_getBooksTitleXML_fail():
    result = aleph.getBooksTitleXML("azgabash, azgabash, azgabash!")

    assert not result

    sleep_some()


# Test counters ===============================================================
def test_getISBNCount():
    result = aleph.getISBNCount("80-86056-31-7")

    assert result >= 1

    sleep_some()


def test_getISBNCount_fail():
    result = aleph.getISBNCount("80-86056-31-8888888888")

    assert not result

    sleep_some()


def test_getAuthorsBooksCount():
    result = aleph.getAuthorsBooksCount("Brendan Kehoe")

    assert result >= 1

    sleep_some()


def test_getAuthorsBooksCount_fail():
    result = aleph.getAuthorsBooksCount("Brendan Keho8888888888")

    assert not result

    sleep_some()


def test_getPublishersBooksCount():
    result = aleph.getPublishersBooksCount("Nostromo")

    assert result >= 1

    sleep_some()


def test_getPublishersBooksCount_fail():
    result = aleph.getPublishersBooksCount("Nostrom8888888888")

    assert not result

    sleep_some()


def test_getBooksTitleCount():
    result = aleph.getBooksTitleCount("Zen a umění Internetu")

    assert result >= 1

    sleep_some()


def test_getBooksTitleCount_fail():
    result = aleph.getBooksTitleCount("Zen a umění Internet8888888888")

    assert not result

    sleep_some()
