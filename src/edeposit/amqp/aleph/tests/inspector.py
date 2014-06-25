#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# library for Robot Framework to inspect python modules
#

import os
import sys

sys.path.insert(0, os.path.abspath('src/edeposit/amqp'))

import imp
import aleph
import aleph.export as export
import aleph.datastructures.convertor as convertor

import os.path


BASE_PATH = os.path.dirname(__file__)
EXAMPLE_PATH = BASE_PATH + "/"
EXAMPLE_PATH += "resources/aleph_data_examples/xml_outputs/example4.xml"


class Inspector(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def variable_presented(self, modulePath, name):
        module = imp.load_source("module", modulePath)
        value = getattr(module, name)
        if not value:
            raise AssertionError(
                "Module: %s has no variable '%s'!" % (self.modulePath, name)
            )

    def is_type_of(self, element, reference):
        if type(element) != reference:
            raise AssertionError(
                "type(%s) != %s" % (str(type(element)), str(reference))
            )

    def call(self, fn, *args, **kwargs):
        return fn(*args, **kwargs)

    def aleph_request(self, request):
        return aleph.reactToAMQPMessage(
            request,
            "0"
        )

    def greater_or_equal_than(self, lvalue, rvalue):
        if int(lvalue) < int(rvalue):
            raise AssertionError(str(lvalue) + " is not >= " + str(rvalue))

    def length(self, val):
        return len(val)

    def value_partialy_in_any_epub(self, value, field_ident_fn, epub):
        if type(epub) != list:
            epub = [epub]

        fields = map(lambda e: field_ident_fn(e), epub)
        if len(fields) > 0 and type(fields[0]) == list:
            fields = sum(fields, [])

        if not any(map(lambda x: value in x, fields)):
            raise AssertionError(
                "Epublications doesn't have your value '%s'!" % (value)
            )

    def author_partialy_in_any_epub(self, author, epub):
        ident = lambda epub: map(
            lambda a: a.lastName.decode("utf-8"),
            epub.epublication.autori
        )

        return self.value_partialy_in_any_epub(author, ident, epub)

    def read_file(self, fn):
        with open(fn) as f:
            return f.read().decode("utf-8").encode("utf-8")

    def test_Marc_XML_deserialization(self):
        xml = self.read_file(EXAMPLE_PATH)

        m = aleph.marcxml.MARCXMLRecord(xml)

        # test getters
        assert m.getAuthors()[0].name == "Eric S."
        assert m.getAuthors()[0].surname == "Raymond"
        assert m.getISBNs()[0] == "80-251-0225-4"
        assert "brož." in m.getBinding()[0]
        assert len(m.getCorporations()) == 0
        assert len(m.getDistributors()) == 0
        assert m.getFormat() == "23 cm"
        assert m.getName() == "Umění programování v UNIXu /"
        assert m.getSubname() == ""
        assert m.getPrice() == "Kč 590,00"
        assert m.getPart() == ""
        assert m.getPartName() == ""
        assert m.getPart() == ""
        assert m.getPublisher() == "Computer Press,"
        assert m.getPubDate() == "2004"
        assert m.getPubOrder() == "1. vyd."
        assert m.getOriginals()[0] == "Art of UNIX programming"

        # test m.__str__() equality with original XML
        assert set(xml.splitlines()) == set(str(m).splitlines())

    def test_epublication_convertor(self):
        epub = aleph.convertor.toEPublication(self.read_file(EXAMPLE_PATH))

        assert epub.autori[0].lastName == "Raymond", "Bad author name."
        assert epub.ISBN[0] == "80-251-0225-4", "Bad ISBN."
        assert "brož." in epub.vazba, "Bad binding."
        assert epub.format == "23 cm", "Bad size."
        assert epub.nazev == "Umění programování v UNIXu /", "Bad name."
        assert epub.podnazev == "", "Bad subname"
        assert epub.cena == "Kč 590,00", "Bad price."
        assert epub.nazevCasti == "", "Bad part name."
        assert epub.castDil == "", "Bad part order."
        assert epub.nakladatelVydavatel == "Computer Press,", "Bad publisher."
        assert epub.datumVydani == "2004", "Bad pub date."
        assert epub.poradiVydani == "1. vyd.", "Bad pub order."
        assert epub.originaly[0] == "Art of UNIX programming", "Bad original name."
        assert epub.internal_url == "", "Bad internal URL."

    def convert_epublication_to_post_request(self):
        xml = self.read_file(EXAMPLE_PATH)
        xml = aleph.marcxml.MARCXMLRecord(xml)

        epub = convertor.toEPublication(xml)
        epub = epub._replace(
            autori=[epub.autori[0].firstName + " " + epub.autori[0].lastName],
            url="Someurl"
        )
        post = export.PostData(epub)

        assert(epub.nazev == post._POST["P07012001_a"])

        return post

    def try_to_send_bad_data(self):
        post_dict = self.convert_epublication_to_post_request().get_POST_data()
        post_dict["P1601ISB__a"] = "edeposit_test"
        post_dict["P0501010__a"] = "edeposit_test"

        data = export._sendPostDict(post_dict).decode("utf-8")

        assert(u"P07012001_a='Umění programování v UNIXu /'" in data)
        assert(u"P0504010__d='Kč 590,00'" in data)

        return data
