#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from edeposit.amqp.aleph import aleph


# Tests =======================================================================
def test_variables():
    assert "/" in aleph.SEARCH_URL_TEMPLATE
    assert "/" in aleph.SET_URL_TEMPLATE
    assert "/" in aleph.DOC_URL_TEMPLATE
    assert "/" in aleph.OAI_DOC_URL_TEMPLATE
    assert "/" in aleph.RECORD_URL_TEMPLATE

    int(aleph.MAX_RECORDS)


def test_AlephException():
    with pytest.raises(aleph.AlephException):
        raise aleph.AlephException("Xe")


def test_InvalidAlephBaseException():
    with pytest.raises(aleph.InvalidAlephBaseException):
        raise aleph.InvalidAlephBaseException("Xe")


def test_InvalidAlephFieldException():
    with pytest.raises(aleph.InvalidAlephFieldException):
        raise aleph.InvalidAlephFieldException("Xe")


def test_LibraryNotFoundException():
    with pytest.raises(aleph.LibraryNotFoundException):
        raise aleph.LibraryNotFoundException("Xe")


def test_DocumentNotFoundException():
    with pytest.raises(aleph.DocumentNotFoundException):
        raise aleph.DocumentNotFoundException("Xe")


def test_DocumentID():
    did = aleph.DocumentID("someid", "somelibrary", "somebase")

    assert did.id == "someid"
    assert did.library == "somelibrary"
    assert did.base == "somebase"


def test_tryConvertToInt():
    assert aleph._tryConvertToInt("11") == 11
    assert aleph._tryConvertToInt("1s") == "1s"


# def test_alephResultToDict():