#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from edeposit.amqp.aleph import aleph



# Variables ===================================================================



# Functions & objects =========================================================
def test_getListOfBases():
    bases = aleph.getListOfBases()

    assert "nkc" in bases