#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from edeposit.amqp.aleph import settings
from edeposit.amqp.aleph import GenericQuery
from edeposit.amqp.aleph import SearchRequest
from edeposit.amqp.aleph import reactToAMQPMessage


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
