#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
## Todo
#   - makeSureThatFieldsExist()
#   - script, co si z DTD/xsd vytahne popisky do slovniku/whatever
#= Imports ====================================================================
from string import Template


import dhtmlparser
from dhtmlparser import HTMLElement


#= Functions & objects ========================================================
class Person():
    """
    This class represents informations about persons as they are defined in
    MARC standards.

    Properties:
        .name
        .second_name
        .surname
        .title
    """
    def __init__(self, name, second_name, surname, title):
        self.name = name
        self.second_name = second_name
        self.surname = surname
        self.title = title


class Corporation():
    """
    Some informations about corporations (fields 110, 610, 710, 810).

    Properties:
        .name
        .place
        .date
    """
    def __init__(self, name, place, date):
        super(Corporation, self).__init__()
        self.name = name
        self.place = place
        self.date = date


class MarcSubrecord(str):
    """
    TODO
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
    Class for serialization/deserialization of MARCXML and MARC OAI documents.

    Standard MARC record is made from three parts:
        leader -- binary something, you can probably ignore it
        controlfileds -- marc fields < 10
        datafields -- important information you actually want

    Basic scheme looks like this:

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

    <leader> is optional and it is parsed into MARCXMLRecord.leader as string.

    <controlfield>s are optional and parsed as dictionary into
    MARCXMLRecord.controlfields, and dictionary for data from example would
    look like this:

    MARCXMLRecord.controlfields = {
        "001": "data",
        ...
        "010": "data"
    }

    <datafield>s are non-optional and are parsed into MARCXMLRecord.datafields,
    which is little bit more complicated dictionary. Complicated is mainly
    because tag parameter is not unique, so there can be more <datafield>s with
    same tag!

    scode is always one character (ascii lowercase), or number.

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

    As you can see in 910 record example, sometimes there are multiple records
    in list!

    NOTICE, THAT RECORDS ARE STORED IN ARRAY, NO MATTER IF IT IS JUST ONE
    RECORD, OR MULTIPLE RECORDS. SAME APPLY TO SUBFIELDS.

    Example above corresponds with this piece of code from real world:

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


    - OAI ---------------------------------------------------------------------
    OAI documents are little bit different, but almost same in structure.

    leader is optional and is stored in MARCXMLRecord.controlfields["LDR"], but
    also in MARCXMLRecord.leader for backward compatibility.

    <controlfield> is renamed to <fixfield> and its "tag" parameter to "label".

    <datafield> tag is not named datafield, but <varfield>, "tag" parameter is
    "id" and ind1/ind2 are named i1/i2, but works the same way.

    <subfield>s parameter "code" is renamed to "label".


    - Full documentation ------------------------------------------------------
    Description of simplified MARCXML schema can be found at
    http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd

    Full description of MARCXML with definition of each element can be found at
    http://www.loc.gov/standards/marcxml/mrcbxmlfile.dtd (19492 lines of code)

    Description of MARC OAI can be found at
    http://www.openarchives.org/OAI/oai_marc.xsd
    """
    def __init__(self, xml=None):
        self.leader = None
        self.oai_marc = False
        self.controlfields = {}
        self.datafields = {}
        self.valid_i_chars = list(" 0123456789")

        if xml is not None:
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
            "z": "X0456b"
        }

        Function takes care of OAI MARC.
        """
        if i1 not in self.valid_i_chars:
            raise ValueError("Invalid i1parameter '" + i1 + "'!")
        if i2 not in self.valid_i_chars:
            raise ValueError("Invalid i2parameter '" + i2 + "'!")
        if len(name) != 3:
            raise ValueError("name parameter have to be exactly 3 chars long!")

        subfields_dict[self.getI(1)] = i1
        subfields_dict[self.getI(2)] = i2

        # append dict, or add new dict into self.datafields
        if name in self.datafields:
            self.datafields.append(subfields_dict)
        else:
            self.datafields[name] = [subfields_dict]

    def getDataRecords(self, datafield, subfield, throw_exceptions=True):
        """
        Return content of given subfield in datafield.

        datafield -- String with section name (for example "001", "100", "700")
        subfield -- String with subfield name (for example "a", "1", etc..)
        throw_exceptions -- If True, KeyError is raised if method couldnt found
                            given datafield/subfield. If false, blank array []
                            is returned.

        Returns list of MarcSubrecords. MarcSubrecord is practically same thing
        as string, but has defined .getI1() and .getI2() properties.

        Believe me, you will need this, because MARC XML depends on them from
        time to time (name of authors for example).
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

        roles -- specify which types of corporations you need. Set to ["any"]
                 for any role, ["dst"] for distributors, etc.. See
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

    def getI(self, num):
        """Get current name of i1/ind1 parameter based on self.oai_marc."""
        if num != 1 and num != 2:
            raise ValueError("num parameter have to be 1 or 2!")

        i_name = "ind" if not self.oai_marc else "i"

        return i_name + str(num)

    def _parseCorporations(self, datafield, subfield, roles=["any"]):
        """
        Parse informations about corporations from given field identified by
        datafield parmeter.

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
        role -- see http://www.loc.gov/marc/relators/relaterm.html for details
                set to ["any"] for any role, ["aut"] for authors, etc..

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
                surname, name = person.rsplit(" ")

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
        tag_id -- parameter name, which holds the information, about field name
                  this is normally "tag", but in case of oai_marc "id".

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
        tag_id -- parameter name, which holds the information, about field name
                  this is normally "tag", but in case of oai_marc "id"
        sub_id -- id of parameter, which holds informations about subfield name
                  this is normally "code" but in case of oai_marc "label"

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
        for field_id in sorted(self.controlfields.keys()):
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
        for field_id in sorted(subfields.keys()):
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
        for field_id in sorted(self.datafields.keys()):
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
        leader = ""
        if not self.oai_marc:
            leader = "<leader>" + self.leader + "</leader>"

        return Template(marcxml_template).substitute(
            LEADER=leader.strip(),
            CONTROL_FIELDS=self.__serializeControlFields().strip(),
            DATA_FIELDS=self.__serializeDataFields().strip()
        )

    def __str__(self):
        return self.toXML()

    def __repr__(self):
        return str(self.__dict__)


#= Main program ===============================================================
if __name__ == '__main__':
    r = MARCXMLRecord(open("multi_example.xml").read())

    print repr(r)

    # print r.datafields["910"]
    # print r.leader
    # print r.toXML()

    # print r.getDataRecords("020", "a")
