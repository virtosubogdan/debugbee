"""
Class logging testing.
"""
# pylint: disable=missing-docstring, invalid-name, no-self-use, unused-argument

import os

from debugbee.debug import debugbee_class, reload_configuration, reset_to_default
import debugbee.parameter_names as pn

@debugbee_class()
class SimpleClass(object):
    def __init__(self):
        print "normal init"

    def get_something(self):
        return 3

class TestFunctionDebug(object):

    def test_simple_class(self, capsys):
        obj = SimpleClass()
        out, err = capsys.readouterr()
        assert out == "init of <class 'debugbee.tests.test_classes.SimpleClass'>\nnormal init\n"
        assert err == ""
        obj.get_something()
        out, err = capsys.readouterr()
        assert out == "get_something\n"
        assert err == ""
