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


BASE_PATH = os.path.basename(__file__)


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



    # def isbn_is_valid(self, isbn_request):
    #     retualep.reactToAMQPMessage(isbn_request)

    # def testedlibrary_send_to_aleph(self, epublication):
    #     return edeposit.amqp.aleph.send_to_aleph(epublication)

    # def testedlibrary_handle_aleph_response(self, epublication):
    #     return edeposit.amqp.aleph.handle_aleph_response(epublication)

    # def testedLibrary_id_conforms_naming_way(self, epublicationDirectory):
    #     """ id je ve tvaru: 2014-01-01-agafdsX. A je to zaroven adresar. """
    #     if not re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}-.+", epublicationDirectory):
    #         AssertionError("epublication directory doesnot conform naming way")

    # def aleph_AcceptedEPublication(self, directory):
    #     """ created responses the same way as Aleph creates it """
    #     pass

    # def aleph_RejectedEPublication(self, directory):
    #     """ created responses the same way as Aleph creates it """
    #     pass

    # def call(self, module_name, method_name, *args):
    #     """calls method from module with *args"""
    #     pass

    # def aleph_success_results(self, export_id):
    #     """ this test function saves into export directory files:
    #     - aleph-record.xml
    #     - aleph-success
    #     """
    #     directory = os.path.join(variables.PATH_OF_EXPORT_DIRECTORY, export_id)
    #     shutil.copyfile(os.path.join(BASE_PATH, "aleph-record.xml"),
    #                     os.path.join(directory, "aleph-record.xml"))
    #     shutil.copyfile(os.path.join(BASE_PATH, "aleph-success"),
    #                     os.path.join(directory, "aleph-success"))
