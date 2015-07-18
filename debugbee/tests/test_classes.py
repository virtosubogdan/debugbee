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

@debugbee_class()
class PrettyClass(object):
    def __init__(self):
        print "Pretty Init"

    def get_something(self):
        return 3

    def __str__(self):
        return "Pretty Object"

    def __unicode__(self):
        return u"Pretty Object in unicode"

    def _private(self):
        return "this is private!"

class TestFunctionDebug(object):

    def test_simple_class(self, capsys):
        obj = SimpleClass()
        out, err = capsys.readouterr()
        assert out == "init of <class 'debugbee.tests.test_classes.SimpleClass'>\nnormal init\n"
        assert err == ""
        obj.get_something()
        out, err = capsys.readouterr()
        assert out == "SimpleClass.get_something\n"
        assert err == ""

    def test_ignore_representations(self, capsys):
        obj = PrettyClass()
        out, err = capsys.readouterr()
        assert out == "init of <class 'debugbee.tests.test_classes.PrettyClass'>\nPretty Init\n"
        assert err == ""
        obj._private()
        assert str(obj) != unicode(obj)
        out, err = capsys.readouterr()
        assert out == "PrettyClass._private\n"
        assert err == ""
