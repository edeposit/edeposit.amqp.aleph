# -*- coding: utf-8 -*-

#
# library for Robot Framework to inspect python modules
# 

import inspect
import imp

class PythonModule(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, modulePath):
        self.modulePath = modulePath

    def get_module_variables(self):
        pass

    def variable_presented(self,name):
        #import sys, pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        module = imp.load_source("module", self.modulePath)
        value = getattr(module,name)
        if not value:
            raise AssertionError("module: %s has no variable '%s'" % (self.modulePath, name))
    
    def is_type_of(self, element, reference):
        if type(element) != reference:
            raise AssertionError("wrong type")

    def isbn_is_valid(self,result):
        if not result.valid:
            raise AssertionError("attribute 'valid' must be True")
        pass

    def isbn_is_not_valid(self,result):
        if result.valid:
            raise AssertionError("attribute 'valid' must be False")

