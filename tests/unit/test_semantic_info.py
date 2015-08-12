#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from aleph.datastructures.semanticinfo import _parse_summaryRecordSysNumber
from aleph.datastructures.semanticinfo import SemanticInfo

from test_epublication import unix_example
from test_epublication import echa_example
from test_epublication import pasivni_domy_example


# Tests =======================================================================
def test_parse_summaryRecordSysNumber():
    num = _parse_summaryRecordSysNumber(
        "Souborný záznam viz nkc20150003029."
    )

    assert num == "nkc20150003029"

    num = _parse_summaryRecordSysNumber(
        "Souborný záznam viz 978-80-87899-15-1."
    )

    assert num == "978-80-87899-15-1"


def test_parse_summaryRecordSysNumber_multiple_PJM():
    num = _parse_summaryRecordSysNumber(
        "V zamčených záznamech při opravě pole 260 na 264 jsou následně vyžadována pole 336, 337, 338\n"
        "Souborný záznam viz nkc20150003133"
    )

    assert num == "nkc20150003133"


def test_toSemanticInfo_unix(unix_example):
    semantic_info = SemanticInfo.from_xml(unix_example)

    assert semantic_info

    assert not semantic_info.isClosed

    # normal records doesn't use semantic info
    assert not semantic_info.hasAcquisitionFields
    assert not semantic_info.ISBNAgencyFields
    assert not semantic_info.descriptiveCatFields
    assert not semantic_info.descriptiveCatReviewFields
    assert not semantic_info.subjectCatFields
    assert not semantic_info.subjectCatReviewFields
    assert not semantic_info.summaryRecordSysNumber
    assert not semantic_info.parsedSummaryRecordSysNumber
    assert not semantic_info.isSummaryRecord
    assert not semantic_info.contentOfFMT


def test_toSemanticInfo_echa(echa_example):
    semantic_info = SemanticInfo.from_xml(echa_example)

    assert semantic_info

    assert not semantic_info.isClosed

    assert not semantic_info.hasAcquisitionFields
    assert not semantic_info.ISBNAgencyFields
    assert semantic_info.descriptiveCatFields == ['jp20150312', 'kola']
    assert not semantic_info.descriptiveCatReviewFields
    assert not semantic_info.subjectCatFields
    assert not semantic_info.subjectCatReviewFields
    assert not semantic_info.summaryRecordSysNumber
    assert not semantic_info.parsedSummaryRecordSysNumber
    assert semantic_info.isSummaryRecord
    assert semantic_info.contentOfFMT == "SE"


def test_toSemanticInfo_pasivni_domy(pasivni_domy_example):
    semantic_info = SemanticInfo.from_xml(pasivni_domy_example)

    assert semantic_info

    assert semantic_info.isClosed

    assert semantic_info.hasAcquisitionFields
    assert semantic_info.ISBNAgencyFields == ['ii20150224', 'anje']
    assert semantic_info.descriptiveCatFields == ['jp20150225', 'kola']
    assert not semantic_info.descriptiveCatReviewFields
    assert not semantic_info.subjectCatFields
    assert not semantic_info.subjectCatReviewFields
    assert semantic_info.summaryRecordSysNumber == "Seriálový záznam viz nkc20150003043"
    assert semantic_info.parsedSummaryRecordSysNumber == "nkc20150003043"
    assert not semantic_info.isSummaryRecord
    assert semantic_info.contentOfFMT == "BK"
