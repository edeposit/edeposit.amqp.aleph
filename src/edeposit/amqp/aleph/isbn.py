#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
This module is providing funcionality to validate ISBN checksums and also
allows to compute ISBN checksum digits.
"""


#= Functions & objects ========================================================
def _clean_isbn(isbn):
    """
    Remove all non-digit and non "x" characters from given string.

    Return list of numbers (if "x" is found, it is converted to 10).
    """
    if type(isbn) == str:
        isbn = list(isbn.lower())

        # filter digits and "x"
        isbn = filter(lambda x: x.isdigit() or x == "x", isbn)

    # convert ISBN to numbers
    return map(lambda x: 10 if x == "x" else int(x), isbn)


def isbn_cleaner(fn):
    """
    Decorator for calling other functions from this modules.
    """
    def wrapper(isbn):
        return fn(_clean_isbn(isbn))

    return wrapper


@isbn_cleaner
def get_isbn10_checksum(isbn):
    """
    Return checksum for given `isbn`.

    Function expects that `isbn` is only 9 digits long.

    Returns: int -- last checksum digit
    """
    return sum([(i + 1) * x for i, x in enumerate(isbn)]) % 11


@isbn_cleaner
def is_isbn10_valid(isbn):
    """Check if given `isbn` is valid."""
    if len(isbn) != 10:
        return False

    return get_isbn10_checksum(isbn[:-1]) == isbn[-1]


@isbn_cleaner
def get_isbn13_checksum(isbn):
    """
    Return `isbn`'s checksum number.

    Function expects that `isbn` is only 12 digits long.

    Returns: int -- last checksum digit
    """
    multipliers = map(lambda x: int(x), list("13" * 6))
    return 10 - sum([i * x for i, x in zip(multipliers, isbn)]) % 10


@isbn_cleaner
def is_isbn13_valid(isbn):
    """Check if given `isbn` is valid."""
    if len(isbn) != 13:
        return False

    return get_isbn13_checksum(isbn[:-1]) == isbn[-1]


@isbn_cleaner
def is_valid_isbn(isbn):
    """
    Validate given `isbn`.

    Function doesn't require `isbn` type to be specified (it can be both 10/13
    isbn's versions).
    """
    length = len(isbn)

    if length == 10:
        return is_isbn10_valid(isbn)
    elif length == 13:
        return is_isbn13_valid(isbn)

    return False

