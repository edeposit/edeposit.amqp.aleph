# -*- coding: utf-8 -*-

#
# library for Robot Framework to inspect python modules
# 

import imp
import edeposit.amqp.aleph as aleph

import inspect
import shutil
import variables
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
        def blank_fn(result, uuid):
            return aleph.deserialize(result)

        return aleph.reactToAMQPMessage(
            aleph.serialize(request),
            blank_fn,
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

    def test_Marc_XML_deserialization(self):
        xml = ""
        with open(EXAMPLE_PATH) as f:
            xml = f.read()

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

    def test_JSON_convertor(self):
        data = ""
        with open(EXAMPLE_PATH) as f:
            data = f.read()

        epub = aleph.convertors.toEPublication(data)
        epub2 = aleph.convertors.fromJSON(aleph.convertors.toJSON(epub))

        assert(epub == epub2)
