#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple


# Structures ==================================================================
class SemanticInfo(namedtuple("SemanticInfo", ["hasAcquisitionFields",
                                               "hasISBNAgencyFields",
                                               "hasDescriptiveCatFields",
                                               "hasDescriptiveCatReviewFields",
                                               "hasSubjectCatFields",
                                               "hasSubjectCatReviewFields"])):
    """
    This structure is used to represent informations about export progress in
    Aleph.

    It contains informations about state of the record, so it can be tracked
    from edeposit project.

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
    """
    pass
