#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from test_epublication import read_file


# Variables ===================================================================



# Fixtures ====================================================================
@pytest.fixture
def periodic_example():
    return read_file("periodic.xml")


# Tests =======================================================================
def test_():
    pass
