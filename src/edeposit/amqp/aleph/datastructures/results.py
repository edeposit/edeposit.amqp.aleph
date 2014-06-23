#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
This module provides Result objects, that are sent back as answers to
requests.

All classes defined here are just simple namedtuple data containers, without
any other functionality.
"""

from collections import namedtuple


class ISBNValidationResult(namedtuple("ISBNValidationResult", ["is_valid"])):
    """
    Response to :class:`.ISBNValidationRequest`.

    Attributes:
        is_valid (bool): True, if ISBN is valid.
    """
    pass


class SearchResult(namedtuple("SearchResult", ['records'])):
    """
    This is response structure, which is sent back when :class:`.SearchRequest`
    is received.

    Attributes:
        records (list): Array of AlephRecord structures.
    """
    pass


class CountResult(namedtuple("CountResult", ['num_of_records'])):
    """
    This is returned back to client when he send :class:`.CountRequest`.

    Attributes:
        num_of_records (int): Number of records.
    """
    pass


class ExportResult(namedtuple("ExportResult", ["ISBN"])):
    """
    Sent back as response to :class:`.ExportRequest`.

    This class is blank at the moment, because there is no information, that
    can be sen't back.

    Attributes:
        ISBN (str): ISBN of accepted publication.
    """
    pass
