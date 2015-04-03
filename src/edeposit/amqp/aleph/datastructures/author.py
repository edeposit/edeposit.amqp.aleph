#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple


# Structures ==================================================================
class Author(namedtuple("Author", ['firstName', 'lastName', 'title'])):
    """
    Informations about author (or person).

    Attributes:
        firstName (str)
        lastName (str)
        title (str)
    """
    pass
