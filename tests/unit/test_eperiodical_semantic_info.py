#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from test_eperiodical import periodical_example

from aleph import EPeriodicalSemanticInfo


# Tests =======================================================================
def test_from_xml(periodical_example):
    epsi = EPeriodicalSemanticInfo.from_xml(periodical_example)

    assert epsi.hasAcquisitionFields
    assert set(epsi.acquisitionFields) == set(['sk20151111', 'pepe'])
    assert not epsi.isClosed
    assert epsi.isSummaryRecord
    assert epsi.contentOfFMT == "SE"
    assert not epsi.parsedSummaryRecordSysNumber
    assert not epsi.summaryRecordSysNumber
