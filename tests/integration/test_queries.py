#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from aleph import settings
from aleph import ISBNQuery
from aleph import GenericQuery
from aleph import SearchRequest
from aleph import reactToAMQPMessage


# Tests =======================================================================
def test_GenericQuery():
    result = reactToAMQPMessage(
        SearchRequest(
            GenericQuery(
                base=settings.ALEPH_DEFAULT_BASE,
                phrase="Cestou necestou",
                considerSimilar=True,
                field="wtl",
            ),
        ),
        ""
    )

    assert result


def test_ISBNQuery():
    result = reactToAMQPMessage(
        SearchRequest(
            ISBNQuery(ISBN="80-7169-860-1"),
        ),
        ""
    )

    assert result