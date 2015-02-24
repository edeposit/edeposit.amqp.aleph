#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Definition of structures, which are used to hold informations about
catalogization process.
"""
# Imports =====================================================================
from collections import namedtuple


# Structures ==================================================================
class SemanticInfo(namedtuple("SemanticInfo", ["hasAcquisitionFields",
                                               "hasISBNAgencyFields",
                                               "hasDescriptiveCatFields",
                                               "hasDescriptiveCatReviewFields",
                                               "hasSubjectCatFields",
                                               "hasSubjectCatReviewFields",
                                               "isClosed"])):
    """
    This structure is used to represent informations about export progress in
    Aleph.

    It contains informations about state of the record, so it can be tracked
    from edeposit project.

    See :func:`.toSemanticInfo` for details of parsing of those attributes.

    Attributes:
        hasAcquisitionFields (bool): Was the record aproved by acquisition?
        hasISBNAgencyFields (bool):  Was the record approved by ISBN agency?
        hasDescriptiveCatFields (bool): Did the record get thru name
                                        description (jmenný popis).
        hasDescriptiveCatReviewFields (bool): Did the record get thru name
                                              revision (jmenná revize).
        hasSubjectCatFields (bool): Did the record get thru subject
                                    description (věcný popis).
        hasSubjectCatReviewFields (bool): Did the record get thru subject
                                          revision (věcná revize).
        isClosed (bool): Was the record closed? This sometimes happen when bad
                         ISBN is given by creator of the record, but different
                         is in the book.
    """
    pass
