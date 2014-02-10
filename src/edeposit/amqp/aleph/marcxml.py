#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
# This work is licensed under a Creative Commons 3.0 Unported License
# (http://creativecommons.org/licenses/by/3.0/).
#
#= Imports ====================================================================
from string import Template

from __init__ import Producent, EPublication, OriginalFile, Author

import dhtmlparser
from dhtmlparser import HTMLElement


#= Variables ==================================================================



#= Functions & objects ========================================================
class MARCXmlRecord:
    def __init__(self, xml=None):
        self.leader = None
        self.controlfields = {}
        self.datafields = {}
        self.oai_marc = False

        if xml is not None:
            self.__parseString(xml)

    def __parseString(self, xml):
        """
        Parse MARC XML document to dicts, which are contained in
        self.controlfields and self.datafields.

        Also detect if this is oai marc format or not (self.oai_marc).
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
            if tag_id not in params:
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
            i_name = "ind" if not self.oai_marc else "i"
            i1_name = i_name + "1"
            i2_name = i_name + "2"
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

            # if there are more fields with same name, convert placeholder to
            # dict
            if tag in self.datafields and \
               isinstance(self.datafields[tag], dict):
                self.datafields[tag] = [self.datafields[tag]]

            if tag in self.datafields:
                self.datafields[tag].append(field_repr)
            else:
                self.datafields[tag] = field_repr

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

        i_name = "ind" if not self.oai_marc else "i"
        i1_name = i_name + "1"
        i2_name = i_name + "2"

        output = ""
        for field_id in sorted(self.datafields.keys()):
            # if field_id points to just dict, make it array (this saves a lot
            # of work with array unpacking in case there is array and not dict)
            if isinstance(self.datafields[field_id], dict):
                self.datafields[field_id] = [self.datafields[field_id]]

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
            LEADER=leader,
            CONTROL_FIELDS=self.__serializeControlFields(),
            DATA_FIELDS=self.__serializeDataFields()
        )


def toEpublication(marcxml):
    pass


def fromEpublication(epublication):
    pass


#= Main program ===============================================================
if __name__ == '__main__':
    r = MARCXmlRecord(open("example.xml").read())

    # print r.datafields["910"]
    print r.leader
    print r.toXML()
