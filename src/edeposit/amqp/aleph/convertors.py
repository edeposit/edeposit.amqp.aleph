#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
This module exists to provide ability to convert from AMQP data structures to
Aleph's data structures.

It can convert MARCXMLRecord to EPublication simplified data structure. It can
also serialize any namedtuple to JSON.
"""
import json


from marcxml import MARCXMLRecord
from datastructures import *
from __init__ import *


#= Functions & objects ========================================================
def toEPublication(marcxml):
    """
    Convert MARCXMLRecord object to EPublication named tuple (see __init__.py).

    Args:
        marcxml (str/MARCXMLRecord): MarcXML which will be converted to
                EPublication. In case of str, <record> tag is required.

    Returns:
        EPublication: named tuple with data about publication.

    See Also:
        :class:`aleph.datastructures.epublication` for details of EPublication
        structure.
    """
    parsed = marcxml
    if not isinstance(marcxml, MARCXMLRecord):
        parsed = MARCXMLRecord(str(marcxml))

    # distributor = ""  # FUTURE
    # mistoDistribuce = ""
    # datumDistribuce = ""

    # # parse information about distributors
    # distributors = parsed.getCorporations("dst")
    # if len(distributors) >= 1:
    #     mistoDistribuce = distributors[0].place
    #     datumDistribuce = distributors[0].date
    #     distributor = distributors[0].name

    # zpracovatel
    zpracovatel = parsed.getDataRecords("040", "a", False)
    zpracovatel = zpracovatel[0] if len(zpracovatel) >= 1 else ""

    # url
    url = parsed.getDataRecords("856", "u", False)
    url = url[0] if len(url) >= 1 else ""

    binding = parsed.getBinding()

    # i know, that this is not PEP8, but you dont want to see it without proper
    # formating (it looks bad, really bad)
    return EPublication(
        ISBN                = parsed.getISBNs(),
        nazev               = parsed.getName(),
        podnazev            = parsed.getSubname(),
        vazba               = binding[0] if len(binding) > 0 else "",
        cena                = parsed.getPrice(),
        castDil             = parsed.getPart(),
        nazevCasti          = parsed.getPartName(),
        nakladatelVydavatel = parsed.getPublisher(),
        datumVydani         = parsed.getPubDate(),
        poradiVydani        = parsed.getPubOrder(),
        zpracovatelZaznamu  = zpracovatel,
        # mistoDistribuce     = mistoDistribuce,  # FUTURE
        # distributor         = distributor,
        # datumDistribuce     = datumDistribuce,
        # datumProCopyright   = "",
        format              = parsed.getFormat(),
        url                 = url,
        mistoVydani         = parsed.getPubPlace(),
        ISBNSouboruPublikaci= [],
        autori              = map(  # convert Persons to amqp's Authors
            lambda a: Author(
                (a.name + " " + a.second_name).strip(),
                a.surname,
                a.title
            ),
            parsed.getAuthors()
        ),
        originaly           = parsed.getOriginals(),
        internal_url        = ""  # TODO
    )


def _serializeNT(data):
    """
    Serialize namedtuples (and other basic python types) to dictionary with
    some special properties.

    Args:
        data (namedtuple/other python types): Data which will be serialized to
             dict.

    Data can be later automatically de-serialized by calling _deserializeNT().
    """
    if isinstance(data, list):
        return map(lambda x: _serializeNT(x), data)

    elif isinstance(data, tuple) and hasattr(data, "_fields"):  # is namedtuple
        serialized = _serializeNT(dict(data._asdict()))
        serialized["__nt_name"] = data.__class__.__name__

        return serialized

    elif isinstance(data, tuple):
        return tuple(map(lambda x: _serializeNT(x), data))

    elif isinstance(data, dict):
        return dict(
            map(
                lambda key: [key, _serializeNT(data[key])],
                data.keys()
            )
        )

    return data


def toJSON(structure):
    """
    Convert structure to json.

    This is necessary, because standard JSON module can't serialize
    namedtuples.

    Args:
        structure (namedtuple/basic python types): data which will be
                  serialized to JSON.

    Returns:
        str: with serialized data.
    """
    return json.dumps(_serializeNT(structure))


def _deserializeNT(data):
    """
    Deserialize special kinds of dicts from _serializeNT().
    """
    if isinstance(data, list):
        return map(lambda x: _deserializeNT(x), data)

    elif isinstance(data, tuple):
        return tuple(map(lambda x: _deserializeNT(x), data))

    elif isinstance(data, dict) and "__nt_name" in data:  # is namedtuple
        class_name = data["__nt_name"]
        del data["__nt_name"]

        return globals()[class_name](
            **dict(zip(data.keys(), _deserializeNT(data.values())))
        )

    elif isinstance(data, dict):
        return dict(
            map(
                lambda key: [key, _deserializeNT(data[key])],
                data.keys()
            )
        )

    elif isinstance(data, unicode):
        return data.encode("utf-8")

    return data


def fromJSON(json_data):
    """
    Convert JSON string back to python structures.

    This is necessary, because standard JSON module can't serialize
    namedtuples.

    Args:
        json_data (str): JSON string.

    Returns:
        python data/nameduple: with deserialized data.
    """
    return _deserializeNT(json.loads(json_data))
