"""
Class logging testing.
"""
# pylint: disable=missing-docstring, invalid-name, no-self-use, unused-argument

from debugbee.debug import debugbee_class, debugbee


@debugbee_class()
class SimpleClass(object):
    def __init__(self):
        print "normal init"

    def get_something(self):
        return 3

    def get_more(self):
        return self.get_something()

    def get_even_more(self):
        return self.get_more()


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


@debugbee()
def debugged_method(simpleObj):
    return simpleObj.get_something()

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

    def test_class_depth_call(self, capsys):
        obj = SimpleClass()
        out, err = capsys.readouterr()
        assert out == "init of <class 'debugbee.tests.test_classes.SimpleClass'>\nnormal init\n"
        assert err == ""
        obj.get_even_more()
        out, err = capsys.readouterr()
        assert out == """SimpleClass.get_even_more
    SimpleClass.get_more
        SimpleClass.get_something\n"""
        assert err == ""

    def test_class_and_function(self, capsys):
        obj = SimpleClass()
        obj.get_something()
        debugged_method(obj)
        out, err = capsys.readouterr()
        assert out == """init of <class 'debugbee.tests.test_classes.SimpleClass'>
normal init
SimpleClass.get_something
debugged_method:simpleObj=SimpleClass
    SimpleClass.get_something\n"""
        assert err == ""
