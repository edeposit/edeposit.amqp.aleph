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
