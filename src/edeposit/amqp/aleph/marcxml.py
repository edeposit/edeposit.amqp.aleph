#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
# This work is licensed under a Creative Commons 3.0 Unported License
# (http://creativecommons.org/licenses/by/3.0/).
#
## Todo
#   - makeSureThatFieldsExist()
#   - script, co si z DTD/xsd vytahne popisky do slovniku/whatever
#= Imports ====================================================================
from string import Template

from __init__ import Producent, EPublication, OriginalFile, Author

import dhtmlparser
from dhtmlparser import HTMLElement


#= Variables ==================================================================



#= Functions & objects ========================================================
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
            "scode": "data",
            "scode+": "another data"
        }],

        # real example
        "928": [{
            "ind1": "1",
            "ind2": " ",
            "a": "Portál"
        }],

        "910": [
            {
                "ind1": "1",
                "ind2": " ",
                "a": "ABA001"
            },
            {
                "ind1": "2",
                "ind2": " ",
                "a": "BOA001",
                "b": "2-1235.975"
            },
            {
                "ind1": "3",
                "ind2": " ",
                "a": "OLA001",
                "a": "1-218.844"
            }
        ]
    }

    As you can see in 910 record example, sometimes there are multiple records
    in list!

    NOTICE, THAT RECORDS ARE STORED IN ARRAY, NO MATTER IF IT IS JUST ONE
    RECORD, OR MULTIPLE RECORDS.

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

        if xml is not None:
            self.__parseString(xml)

    def addControlField(self, name, value):
        self.controlfields[name] = value

    def addDataField(self, name, i1, i2, subfields_dict):
        """
        Add new datafield into self.datafields.

        Takes care of oai marc.
        """
        subfields_dict[self.getI(1)] = i1
        subfields_dict[self.getI(2)] = i2

        # append dict, or add new dict into self.datafields
        if name in self.datafields:
            self.datafields.append(subfields_dict)
        else:
            self.datafields[name] = [subfields_dict]

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
        record = record[0]  # TODO: možná opravit na postupné rozparsování?

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

    def getI(self, num):
        """Get current name of i1/ind1 paraemter based on self.oai_marc."""
        i_name = "ind" if not self.oai_marc else "i"

        return i_name + str(num)

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

                field_repr[code] = subfield.getContent().strip()

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
            output += Template(template).substitute(
                TAGNAME=tagname,
                FIELD_NAME=field_name,
                FIELD_ID=field_id,
                CONTENT=subfields[field_id]
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


def toEpublication(marcxml):
    pass


def fromEpublication(epublication):
    pass


#= Main program ===============================================================
if __name__ == '__main__':
    r = MARCXMLRecord(open("example.xml").read())

    # print r.datafields["910"]
    print r.leader
    print r.toXML()
