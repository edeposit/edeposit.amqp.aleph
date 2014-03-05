#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
## TODO:
#    - Add setters
#
#= Imports ====================================================================
"""
Module for parsing and high-level processing of MARC XML records.

About format and how the class work; Standard MARC record is made from
three parts:

    leader -- binary something, you can probably ignore it
    controlfileds -- marc fields < 10
    datafields -- important information you actually want

Basic MARC XML scheme uses this structure:

----
<record xmlns=definition..>
    <leader>optional_binary_something</leader>
    <controlfield tag="001">data</controlfield>
    ...
    <controlfield tag="010">data</controlfield>
    <datafield tag="011" ind1=" " ind2=" ">
        <subfield code="scode">data</subfield>
        <subfield code="a">data</subfield>
        <subfield code="a">another data, but same code!</subfield>
        ...
        <subfield code"scode+">another data</subfield>
    </datafield>
    ...
    <datafield tag="999" ind1=" " ind2=" ">
    ...
    </datafield>
</record>
---

<leader> is optional and it is parsed into MARCXMLRecord.leader as string.

<controlfield>s are optional and parsed as dictionary into
MARCXMLRecord.controlfields, and dictionary for data from example would
look like this:

---
MARCXMLRecord.controlfields = {
    "001": "data",
    ...
    "010": "data"
}
---

<datafield>s are non-optional and are parsed into MARCXMLRecord.datafields,
which is little bit more complicated dictionary. Complicated is mainly
because tag parameter is not unique, so there can be more <datafield>s with
same tag!

scode is always one character (ASCII lowercase), or number.

---
MARCXMLRecord.datafields = {
    "011": [{
        "ind1": " ",
        "ind2": " ",
        "scode": ["data"],
        "scode+": ["another data"]
    }],

    # real example
    "928": [{
        "ind1": "1",
        "ind2": " ",
        "a": ["Portál"]
    }],

    "910": [
        {
            "ind1": "1",
            "ind2": " ",
            "a": ["ABA001"]
        },
        {
            "ind1": "2",
            "ind2": " ",
            "a": ["BOA001"],
            "b": ["2-1235.975"]
        },
        {
            "ind1": "3",
            "ind2": " ",
            "a": ["OLA001"],
            "b": ["1-218.844"]
        }
    ]
}
---

As you can see in 910 record example, sometimes there are multiple records
in a list!

NOTICE, THAT RECORDS ARE STORED IN ARRAY, NO MATTER IF IT IS JUST ONE
RECORD, OR MULTIPLE RECORDS. SAME APPLY TO SUBFIELDS.

Example above corresponds with this piece of code from real world:

---
<datafield tag="910" ind1="1" ind2=" ">
<subfield code="a">ABA001</subfield>
</datafield>
<datafield tag="910" ind1="2" ind2=" ">
<subfield code="a">BOA001</subfield>
<subfield code="b">2-1235.975</subfield>
</datafield>
<datafield tag="910" ind1="3" ind2=" ">
<subfield code="a">OLA001</subfield>
<subfield code="b">1-218.844</subfield>
</datafield>
---

- OAI ----------------------------------------------------------------------
To prevent things to be too much simple, there is also another type of MARC
XML document - OAI format.

OAI documents are little bit different, but almost same in structure.

leader is optional and is stored in MARCXMLRecord.controlfields["LDR"], but
also in MARCXMLRecord.leader for backward compatibility.

<controlfield> is renamed to <fixfield> and its "tag" parameter to "label".

<datafield> tag is not named datafield, but <varfield>, "tag" parameter is
"id" and ind1/ind2 are named i1/i2, but works the same way.

<subfield>s parameter "code" is renamed to "label".

Real world example:

---
<oai_marc>
<fixfield id="LDR">-----nam-a22------aa4500</fixfield>
<fixfield id="FMT">BK</fixfield>
<fixfield id="001">cpk19990652691</fixfield>
<fixfield id="003">CZ-PrNK</fixfield>
<fixfield id="005">20130513104801.0</fixfield>
<fixfield id="007">tu</fixfield>
<fixfield id="008">990330m19981999xr-af--d------000-1-cze--</fixfield>
<varfield id="015" i1=" " i2=" ">
<subfield label="a">cnb000652691</subfield>
</varfield>
<varfield id="020" i1=" " i2=" ">
<subfield label="a">80-7174-091-8 (sv. 1 : váz.) :</subfield>
<subfield label="c">Kč 182,00</subfield>
</varfield>
...
</oai_marc>
---

- Full documentation -------------------------------------------------------
Description of simplified MARCXML schema can be found at
http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd

Full description of MARCXML with definition of each element can be found at
http://www.loc.gov/standards/marcxml/mrcbxmlfile.dtd (19492 lines of code)

Description of MARC OAI can be found at
http://www.openarchives.org/OAI/oai_marc.xsd

"""
from string import Template
from collections import namedtuple


import dhtmlparser
from dhtmlparser import HTMLElement


#= Functions & objects ========================================================
def _undefinedPattern(value, fn, undefined):
    """
    If fn(value) == True, return `undefined`, else `value`.
    """
    if fn(value):
        return undefined

    return value


def resorted(values):
    """
    Sort values, but put numbers after alphabetically sorted words.

    This function is here for outputs, to be diff-compatible with aleph.
    """
    values = sorted(values)
    words = filter(lambda x: not x.isdigit(), values)
    numbers = filter(lambda x: x.isdigit(), values)

    return words + numbers


class Person(namedtuple("Person", ["name",
                                   "second_name",
                                   "surname",
                                   "title"])):
    """
    This class represents informations about persons as they are defined in
    MARC standards.

    Properties:
        .name
        .second_name
        .surname
        .title
    """
    pass


class Corporation(namedtuple("Corporation", ["name", "place", "date"])):
    """
    Some informations about corporations (fields 110, 610, 710, 810).

    Properties:
        .name
        .place
        .date
    """


class MarcSubrecord(str):
    """
    This class is used to stored data returned from .getDataRecords() method
    from MARCXMLRecord.

    It looks kinda like overshot, but when you are parsing the MARC XML,
    values from subrecords, you need to know the context in which the subrecord
    is put.

    Specifically the i1/i2 values, but sometimes is usefull to have acces even
    to the other subfields from this subrecord.

    This class provides this acces thru .getI1()/.getI2() and
    .getOtherSubfiedls() getters. As a bonus, it is also fully convertable to
    string, in which case only the value of subrecord is preserved.
    """
    def __new__(self, arg, ind1, ind2, other_subfields):
        return str.__new__(self, arg)

    def __init__(self, arg, ind1, ind2, other_subfields):
        self.arg = arg
        self.ind1 = ind1
        self.ind2 = ind2
        self.other_subfields = other_subfields

    def getI1(self):
        return self.ind1

    def getI2(self):
        return self.ind2

    def getOtherSubfiedls(self):
        return self.other_subfields

    def __str__(self):
        return self.arg


class MARCXMLRecord:
    """
    Class for serialization/deserialization of MARCXML and MARC OAI
    documents.

    This class parses everything between <root> elements. It checks, if
    there is root element, so please, give it full XML.

    Internal format is described in module docstring. You can access
    internal data directly, or using few handy methods on two different
    levels of abstraction:

    - No abstraction at all ------------------------------------------------
    You can choose to access data directly and for this use, there is few
    important properties:

      .leader         (string)
      .oai_marc       (bool)
      .controlfields  (dict)
      .datafields     (dict of arrays of dict of arrays of strings ^-^)

    .controlfields is simple and easy to use dictionary, where keys are
    field identificators (string, 3 chars, all chars digits). Value is
    always string.

    .datafields is little bit complicated and it is dictionary, consisting
    of arrays of dictionaries, which consist from arrays of strings and two
    special parameters.

    It sounds horrible, but it is not that hard to understand:

    ---
    .datafields = {
        "011": ["ind1": " ", "ind2": " "]  # array of 0 or more dicts
        "012": [
            {
                "a": ["a) subsection value"],
                "b": ["b) subsection value"],
                "ind1": " ",
                "ind2": " "
            },
            {
                "a": [
                    "multiple values in a) subsections are possible!",
                    "another value in a) subsection"
                ],
                "c": [
                    "subsection identificator is always one character long"
                ],
                "ind1": " ",
                "ind2": " "
            }
        ]
    }
    ---

    Notice ind1/ind2 keywords, which are reserved indicators and used in few
    cases thru MARC standard.

    Dict structure is not that hard to understand, but kinda long to access,
    so there is also little bit more high-level abstraction access methods.

    - Lowlevel abstraction -------------------------------------------------
    To access data little bit easier, there are defined two methods to
    access and two methods to add data to internal dictionaries:

      .addControlField(name, value)
      .addDataField(name, i1, i2, subfields_dict)

    Names imho selfdescribing. subfields_dict is expected en enforced to be
    dictionary with one character long keys and list of strings as values.

    Getters are also simple to use:

      .getControlRecord(controlfield)
      .getDataRecords(datafield, subfield, throw_exceptions)

    .getControlRecord() is basically just wrapper over .controlfields and
    works same way as accessing .controlfields[controlfield]

    .getDataRecords(datafield, subfield, throw_exceptions) return list of
    MarcSubrecord* objects with informations from section `datafield`
    subsection `subfield`.

    If throw_exceptions parameter is set to False, method returns empty list
    instead of throwing KeyError.

    *As I said, function returns list of MarcSubrecord objects. They are
    almost same thing as normal strings (they are actually subclassed
    strings), but defines few important methods, which can make your life
    little bit easier:

      .getI1()
      .getI2()
      .getOtherSubfiedls()

    .getOtherSubfiedls() returns dictionary with other subsections, as
    subfield requested by calling .getDataRecords().

    - Highlevel abstractions -----------------------------------------------
    There is also lot of highlevel getters:

      .getName()
      .getSubname()
      .getPrice()
      .getPart()
      .getPartName()
      .getPublisher()
      .getPubDate()
      .getPubOrder()
      .getFormat()
      .getPubPlace()
      .getAuthors()
      .getCorporations()
      .getDistributors()
      .getISBNs()
      .getBinding()
      .getOriginals()
    """
    def __init__(self, xml=None):
        self.leader = None
        self.oai_marc = False
        self.controlfields = {}
        self.datafields = {}
        self.valid_i_chars = list(" 0123456789")

        # it is always possible to create blank object and add values into it
        # piece by piece thru .addControlField()/.addDataField() methods.
        if xml is not None:
            self._original_xml = xml
            self.__parseString(xml)

    def addControlField(self, name, value):
        if len(name) != 3:
            raise ValueError("name parameter have to be exactly 3 chars long!")

        self.controlfields[name] = value

    def addDataField(self, name, i1, i2, subfields_dict):
        """
        Add new datafield into self.datafields.

        name -- name of datafield
        i1 -- value of i1/ind1 parameter
        i2 -- value of i2/ind2 parameter
        subfields_dict -- dictionary containing subfields in this format:

        {
            "field_id": ["subfield data",],
            ...
            "z": ["X0456b"]
        }

        field_id can be only one characted long!

        Function takes care of OAI MARC.
        """
        if i1 not in self.valid_i_chars:
            raise ValueError("Invalid i1parameter '" + i1 + "'!")
        if i2 not in self.valid_i_chars:
            raise ValueError("Invalid i2parameter '" + i2 + "'!")
        if len(name) != 3:
            raise ValueError("name parameter have to be exactly 3 chars long!")
        if not isinstance(subfields_dict, dict):
            raise ValueError(
                "subfields_dict parameter has to be dict instance!"
            )
        for key in subfields_dict.keys():
            if len(key) > 1:
                raise KeyError(
                    "subfields_dict can be only one character long!"
                )
            if not isinstance(subfields_dict[key], list):
                raise ValueError(
                    "Values at under '" + key + "' have to be list!"
                )

        subfields_dict[self.getI(1)] = i1
        subfields_dict[self.getI(2)] = i2

        # append dict, or add new dict into self.datafields
        if name in self.datafields:
            self.datafields.append(subfields_dict)
        else:
            self.datafields[name] = [subfields_dict]

    def getControlRecord(self, controlfield):
        """
        Return record from given `controlfield`. Returned type: str.
        """
        return self.controlfields[controlfield]

    def getDataRecords(self, datafield, subfield, throw_exceptions=True):
        """
        Return content of given subfield in datafield.

        datafield -- String with section name (for example "001", "100",
                     "700")
        subfield -- String with subfield name (for example "a", "1", etc..)
        throw_exceptions -- If True, KeyError is raised if method couldnt
                            found given datafield/subfield. If false, blank
                            array [] is returned.

        Returns list of MarcSubrecords. MarcSubrecord is practically same
        thing as string, but has defined .getI1() and .getI2() properties.

        Believe me, you will need this, because MARC XML depends on them
        from time to time (name of authors for example).
        """
        if len(datafield) != 3:
            raise ValueError(
                "datafield parameter have to be exactly 3 chars long!"
            )
        if len(subfield) != 1:
            raise ValueError(
                "Bad subfield specification - subield have to be 3 chars long!"
            )

        if datafield not in self.datafields:
            if throw_exceptions:
                raise KeyError(datafield + " is not in datafields!")
            else:
                return []

        output = []
        for df in self.datafields[datafield]:
            if subfield not in df:
                if throw_exceptions:
                    raise KeyError(subfield + " is not in subfields!")
                else:
                    return []

            # records are not returned just like plain string, but like
            # MarcSubrecord, because you will need ind1/ind2 values
            for i in df[subfield]:
                output.append(
                    MarcSubrecord(
                        i,
                        df[self.getI(1)],
                        df[self.getI(2)],
                        df
                    )
                )

        return output

    def getName(self):
        return "".join(self.getDataRecords("245", "a", True))

    def getSubname(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("245", "b", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getPrice(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("020", "c", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getPart(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("245", "p", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getPartName(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("245", "n", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getPublisher(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("260", "b", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getPubDate(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("260", "c", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getPubOrder(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("901", "f", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getFormat(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("300", "c", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getPubPlace(self, undefined=""):
        return _undefinedPattern(
            "".join(self.getDataRecords("260", "a", False)),
            lambda x: x.strip() == "",
            undefined
        )

    def getAuthors(self):
        """Return list of authors represented as Person objects."""
        authors = self._parsePersons("100", "a")
        authors += self._parsePersons("600", "a")
        authors += self._parsePersons("700", "a")
        authors += self._parsePersons("800", "a")

        return authors

    def getCorporations(self, roles=["dst"]):
        """
        Return list of Corporation objects specified by roles parameter.

        roles -- specify which types of corporations you need. Set to
                 ["any"] for any role, ["dst"] for distributors, etc.. See
                 http://www.loc.gov/marc/relators/relaterm.html for details.
        """
        corporations = self._parseCorporations("110", "a", roles)
        corporations += self._parseCorporations("610", "a", roles)
        corporations += self._parseCorporations("710", "a", roles)
        corporations += self._parseCorporations("810", "a", roles)

        return corporations

    def getDistributors(self):
        """
        Return list of distributors. Each distributor is represented as
        Corporation object.
        """
        return self.getCorporations(roles=["dst"])

    def getISBNs(self):
        """Return list of ISBN strings."""

        if len(self.getDataRecords("020", "a", False)) != 0:
            return map(
                lambda ISBN: ISBN.strip().split(" ", 1)[0],
                self.getDataRecords("020", "a", True)
            )

        if len(self.getDataRecords("901", "i", False)) != 0:
            return map(
                lambda ISBN: ISBN.strip().split(" ", 1)[0],
                self.getDataRecords("901", "i", True)
            )

        return []

    def getBinding(self):
        if len(self.getDataRecords("020", "a", False)) != 0:
            return map(
                lambda x: x.strip().split(" ", 1)[1],
                filter(
                    lambda x: "-" in x and " " in x,
                    self.getDataRecords("020", "a", True)
                )
            )

        return []

    def getOriginals(self):
        """Return list of original names."""
        return self.getDataRecords("765", "t", False)

    def getI(self, num):
        """
        Get current name of i1/ind1 parameter based on self.oai_marc.

        This method is used mainly internally, but it can be handy if you
        work with with raw MARC XML object and not using getters.
        """
        if num != 1 and num != 2:
            raise ValueError("num parameter have to be 1 or 2!")

        i_name = "ind" if not self.oai_marc else "i"

        return i_name + str(num)

    def _parseCorporations(self, datafield, subfield, roles=["any"]):
        """
        Parse informations about corporations from given field identified
        by datafield parmeter.

        datafield -- String identifying MARC field ("110", "610", etc..)
        subfield -- String identifying MARC subfield with name, which is
                     typically stored in "a" subfield.
        roles -- specify which roles you need. Set to ["any"] for any role,
                 ["dst"] for distributors, etc.. See
                 http://www.loc.gov/marc/relators/relaterm.html for details.

        Returns list of Corporation objects.
        """
        if len(datafield) != 3:
            raise ValueError(
                "datafield parameter have to be exactly 3 chars long!"
            )
        if len(subfield) != 1:
            raise ValueError(
                "Bad subfield specification - subield have to be 3 chars long!"
            )
        parsed_corporations = []
        for corporation in self.getDataRecords(datafield, subfield, False):
            other_subfields = corporation.getOtherSubfiedls()

            # check if corporation have at least one of the roles specified in
            # 'roles' parameter of function
            if "4" in other_subfields and roles != ["any"]:
                corp_roles = other_subfields["4"]  # list of role parameters

                relevant = any(map(lambda role: role in roles, corp_roles))

                # skip non-relevant corporations
                if not relevant:
                    continue

            name = ""
            place = ""
            date = ""

            name = corporation

            if "c" in other_subfields:
                place = ",".join(other_subfields["c"])
            if "d" in other_subfields:
                date = ",".join(other_subfields["d"])

            parsed_corporations.append(Corporation(name, place, date))

        return parsed_corporations

    def _parsePersons(self, datafield, subfield, roles=["aut"]):
        """
        Parse persons from given datafield.

        datafield -- string code of datafield ("010", "730", etc..)
        subfield -- string code of subfield ("a", "z", "4", etc..)
        role -- set to ["any"] for any role, ["aut"] for authors, etc..
                (see http://www.loc.gov/marc/relators/relaterm.html for
                details)

        Main records for persons are: "100", "600" and "700", subrecords "c".

        Returns list of Person objects.
        """
        # parse authors
        parsed_persons = []
        raw_persons = self.getDataRecords(datafield, subfield, False)
        for person in raw_persons:
            ind1 = person.getI1()
            ind2 = person.getI2()
            other_subfields = person.getOtherSubfiedls()

            # check if person have at least one of the roles specified in
            # 'roles' parameter of function
            if "4" in other_subfields and roles != ["any"]:
                person_roles = other_subfields["4"]  # list of role parameters

                relevant = any(map(lambda role: role in roles, person_roles))

                # skip non-relevant persons
                if not relevant:
                    continue

            # result is string, so ind1/2 in MarcSubrecord are lost
            person = person.strip()

            name = ""
            second_name = ""
            surname = ""
            title = ""

            # here it gets nasty - there is lot of options in ind1/ind2
            # parameters
            if ind1 == "1" and ind2 == " ":
                if "," in person:
                    surname, name = person.split(",", 1)
                else:
                    surname, name = person.split(" ", 1)

                if "c" in other_subfields:
                    title = ",".join(other_subfields["c"])
            elif ind1 == "0" and ind2 == " ":
                name = person.strip()

                if "b" in other_subfields:
                    second_name = ",".join(other_subfields["b"])

                if "c" in other_subfields:
                    surname = ",".join(other_subfields["c"])
            elif ind1 == "1" and ind2 == "0" or ind1 == 0 and ind2 == 0:
                name = person.strip()
                title = ",".join(other_subfields["c"])

            parsed_persons.append(
                Person(
                    name.strip(),
                    second_name.strip(),
                    surname.strip(),
                    title.strip()
                )
            )

        return parsed_persons

    def __parseString(self, xml):
        """
        Parse MARC XML document to dicts, which are contained in
        self.controlfields and self.datafields.

        Also detect if this is oai marc format or not (see elf.oai_marc).
        """
        if not isinstance(xml, HTMLElement):
            xml = dhtmlparser.parseString(str(xml))

        # check if there are any records
        record = xml.find("record")
        if len(record) <= 0:
            raise ValueError("There is no <record> in your MARCXML document!")
        record = record[0]

        self.oai_marc = len(record.find("oai_marc")) > 0

        # leader is separate only in marc21
        if not self.oai_marc:
            leader = record.find("leader")
            if len(leader) >= 1:
                self.leader = leader[0].getContent()

        # parse body in respect of OAI MARC format possibility
        if self.oai_marc:
            self.__parseControlFields(record.find("fixfield"))
            self.__parseDataFields(record.find("varfield"), "id", "label")
        else:
            self.__parseControlFields(record.find("controlfield"), "tag")
            self.__parseDataFields(record.find("datafield"), "tag", "code")

        # for backward compatibility of marcxml with oai
        if self.oai_marc and "LDR" in self.controlfields:
            self.leader = self.controlfields["LDR"]

    def __parseControlFields(self, fields, tag_id="tag"):
        """
        Parse control fields.

        fields -- list of HTMLElements
        tag_id -- parameter name, which holds the information, about field
                  name this is normally "tag", but in case of oai_marc
                  "id".

        Returns None.
        """
        for field in fields:
            params = field.params
            if tag_id not in params:  # skip tags with blank parameters
                continue

            self.controlfields[params[tag_id]] = field.getContent().strip()

    def __parseDataFields(self, fields, tag_id="tag", sub_id="code"):
        """
        Parse data fields.

        fields -- list of HTMLElements
        tag_id -- parameter name, which holds the information, about field
                  name this is normally "tag", but in case of oai_marc "id"
        sub_id -- id of parameter, which holds informations about subfield
                  name this is normally "code" but in case of oai_marc
                  "label"

        """
        for field in fields:
            field_repr = {}
            params = field.params

            if tag_id not in params:
                continue

            tag = params[tag_id]

            # take care of iX/indX parameter - I have no idea what is this, but
            # they look important (=they are everywhere)
            i1_name = self.getI(1)
            i2_name = self.getI(2)
            field_repr = {
                i1_name: " " if i1_name not in params else params[i1_name],
                i2_name: " " if i2_name not in params else params[i2_name],
            }

            # process all subfields
            for subfield in field.find("subfield"):
                if sub_id not in subfield.params:
                    continue
                code = subfield.params[sub_id]

                if code in field_repr:
                    field_repr[code].append(subfield.getContent().strip())
                else:
                    field_repr[code] = [subfield.getContent().strip()]

            if tag in self.datafields:
                self.datafields[tag].append(field_repr)
            else:
                self.datafields[tag] = [field_repr]

    def __serializeControlFields(self):
        template = '<$TAGNAME $FIELD_NAME="$FIELD_ID">$CONTENT</$TAGNAME>\n'
        tagname = "controlfield" if not self.oai_marc else "fixfield"
        field_name = "tag" if not self.oai_marc else "id"

        output = ""
        for field_id in resorted(self.controlfields.keys()):
            output += Template(template).substitute(
                TAGNAME=tagname,
                FIELD_NAME=field_name,
                FIELD_ID=field_id,
                CONTENT=self.controlfields[field_id]
            )

        return output

    def __serializeDataSubfields(self, subfields):
        template = '\n<$TAGNAME $FIELD_NAME="$FIELD_ID">$CONTENT</$TAGNAME>'

        tagname = "subfield"
        field_name = "code" if not self.oai_marc else "label"

        output = ""
        for field_id in resorted(subfields.keys()):
            for subfield in subfields[field_id]:
                output += Template(template).substitute(
                    TAGNAME=tagname,
                    FIELD_NAME=field_name,
                    FIELD_ID=field_id,
                    CONTENT=subfield
                )

        return output

    def __serializeDataFields(self):
        template = '<$TAGNAME $FIELD_NAME="$FIELD_ID" $I1_NAME="$I1_VAL" '
        template += '$I2_NAME="$I2_VAL">'
        template += '$CONTENT\n'
        template += '</$TAGNAME>\n'

        tagname = "datafield" if not self.oai_marc else "varfield"
        field_name = "tag" if not self.oai_marc else "id"

        i1_name = self.getI(1)
        i2_name = self.getI(2)

        output = ""
        for field_id in resorted(self.datafields.keys()):
            # unpac dicts from array
            for dict_field in self.datafields[field_id]:
                i1_val = dict_field[i1_name]
                i2_val = dict_field[i2_name]

                # temporarily remove i1/i2 from dict
                del dict_field[i1_name]
                del dict_field[i2_name]

                output += Template(template).substitute(
                    TAGNAME=tagname,
                    FIELD_NAME=field_name,
                    FIELD_ID=field_id,
                    I1_NAME=i1_name,
                    I2_NAME=i2_name,
                    I1_VAL=i1_val,
                    I2_VAL=i2_val,
                    CONTENT=self.__serializeDataSubfields(dict_field)
                )

                # put back temporarily removed i1/i2
                dict_field[i1_name] = i1_val
                dict_field[i2_name] = i2_val

        return output

    def toXML(self):
        """
        Convert object back to XML string.

        Returned string should be same as parsed, if everything works as
        expected.
        """
        marcxml_template = """<record xmlns="http://www.loc.gov/MARC21/slim/"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.loc.gov/MARC21/slim
http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
$LEADER
$CONTROL_FIELDS
$DATA_FIELDS
</record>
"""

        # serialize leader, if it is present
        leader = self.leader if self.leader is not None else ""
        if not self.oai_marc and leader != "":  # print only visible leaders
            leader = "<leader>" + leader + "</leader>"

        return Template(marcxml_template).substitute(
            LEADER=leader.strip(),
            CONTROL_FIELDS=self.__serializeControlFields().strip(),
            DATA_FIELDS=self.__serializeDataFields().strip()
        )

    def __str__(self):
        return self.toXML()

    def __repr__(self):
        return str(self.__dict__)
