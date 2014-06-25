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
                                               "hasCatalogizationFields"])):
    """
    This structure is used to represent informations about export progress in
    Aleph.

    It contains informations about state of the record, so it can be tracked
    from edeposit project.

    Attributes:
        hasAcquisitionFields (bool): Was the record aproved by acquisition?
        hasISBNAgencyFields (bool):  Was the record approved by ISBN agency?
        hasCatalogizationFields (bool): Does it have catalogization fileds.
    """
    pass
