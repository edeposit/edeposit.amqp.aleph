#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is providing funcionality to validate ISBN checksums and also
allows to compute ISBN's checksum digits.a
"""

from functools import wraps


#= Functions & objects ========================================================
def _clean_isbn(isbn):
    """
    Remove all non-digit and non "x" characters from given string.

    Args:
        isbn (str): isbn string, which will be cleaned.

    Returns:
        list: array of numbers (if "x" is found, it is converted to 10).
    """
    if type(isbn) == str:
        isbn = list(isbn.lower())

        # filter digits and "x"
        isbn = filter(lambda x: x.isdigit() or x == "x", isbn)

    # convert ISBN to numbers
    return map(lambda x: 10 if x == "x" else int(x), isbn)


def _isbn_cleaner(fn):
    """
    Decorator for calling other functions from this modules. Purpose of this
    decorator is to clean the ISBN string from garbage and return list.

    Args:
        fn (function): function in which will be :func:`_clean_isbn(isbn)` call
                       wrapped.
    """
    @wraps(fn)
    def wrapper(isbn):
        return fn(_clean_isbn(isbn))

    return wrapper


@_isbn_cleaner
def get_isbn10_checksum(isbn):
    """
    Args:
        isbn (str/list): ISBN number as string or list of digits

    Warning:
        Function expects that `isbn` is only 9 digits long.

    Returns:
        int: last checksum digit for given `isbn`.
    """
    return sum([(i + 1) * x for i, x in enumerate(isbn)]) % 11


@_isbn_cleaner
def is_isbn10_valid(isbn):
    """
    Check if given `isbn` 10 is valid.

    Args:
        isbn (str/list): ISBN number as string or list of digits

    Returns:
        bool: True if ISBN is valid
    """
    if len(isbn) != 10:
        return False

    return get_isbn10_checksum(isbn[:-1]) == isbn[-1]


@_isbn_cleaner
def get_isbn13_checksum(isbn):
    """
    Args:
        isbn (str/list): ISBN number as string or list of digits

    Warning:
        Function expects that `isbn` is only 12 digits long.

    Returns:
        int: last checksum digit for given `isbn`.
    """
    multipliers = map(lambda x: int(x), list("13" * 6))
    return 10 - sum([i * x for i, x in zip(multipliers, isbn)]) % 10


@_isbn_cleaner
def is_isbn13_valid(isbn):
    """
    Check if given `isbn` 13 is valid.

    Args:
        isbn (str/list): ISBN number as string or list of digits

    Returns:
        bool: True if ISBN is valid
    """
    if len(isbn) != 13:
        return False

    return get_isbn13_checksum(isbn[:-1]) == isbn[-1]


@_isbn_cleaner
def is_valid_isbn(isbn):
    """
    Validate given `isbn`.

    Args:
        isbn (str/list): ISBN number as string or list of digits

    Note:
        Function doesn't require `isbn` type to be specified (it can be both
        10/13 isbn's versions).

    Returns:
        bool: True if ISBN is valid
    """
    length = len(isbn)

    if length == 10:
        return is_isbn10_valid(isbn)
    elif length == 13:
        return is_isbn13_valid(isbn)

    return False
