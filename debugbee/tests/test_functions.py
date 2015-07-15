"""
All purpose testing.
"""
# pylint: disable=missing-docstring

import os

from debugbee.debug import debugbee, reload_configuration, reset_to_default
import debugbee.parameter_names as pn


@debugbee()
def simple_function():
    return "simple_result"


@debugbee()
def fibbonaci(number):
    return 1 if number == 0 or number == 1 else (fibbonaci(number-1) + fibbonaci(number-2))


@debugbee()
def max(a, b, c, *args, **kwargs):
    maximum = a if a > b else b
    maximum = maximum if maximum > c else c
    return maximum

@debugbee()
def identity(argument, *args, **kwargs):
    return argument


class TestFunctionDebug(object):

    def test_simple_function(self, capsys):
        simple_function()
        out, err = capsys.readouterr()
        assert out == "simple_function\n"
        assert err == ""


    def test_recursion(self, capsys):
        fibbonaci(3)
        out, err = capsys.readouterr()
        assert out == """\
fibbonaci:number=3
    fibbonaci:number=2
        fibbonaci:number=1
        fibbonaci:number=0
    fibbonaci:number=1
"""
        assert err == ""


    def test_identation_change(self, capsys):
        os.environ[pn.ENV_IDENTATION] = '5'
        reload_configuration()
        fibbonaci(3)
        out, err = capsys.readouterr()
        assert out == """\
fibbonaci:number=3
     fibbonaci:number=2
          fibbonaci:number=1
          fibbonaci:number=0
     fibbonaci:number=1
"""
        assert err == ""


    def test_depth_limiting(self, capsys):
        reset_to_default()
        fibbonaci(4)
        out, err = capsys.readouterr()
        assert out == """\
fibbonaci:number=4
    fibbonaci:number=3
        fibbonaci:number=2
        fibbonaci:number=1
    fibbonaci:number=2
        fibbonaci:number=1
        fibbonaci:number=0
"""
        assert err == ""

    def test_argument_printing(self, capsys):
        reset_to_default()
        max(1, 2, 3)
        out, err = capsys.readouterr()
        expected_out = """max:a=1,b=2,c=3\n"""
        assert out == expected_out
        assert err == ""
        max(1, b=2, c=3)
        out, err = capsys.readouterr()
        assert out == expected_out
        assert err == ""
        max(b=2, c=3, a=1)
        out, err = capsys.readouterr()
        assert out == expected_out
        assert err == ""
        max(1, **{'b':2, 'c':3})
        out, err = capsys.readouterr()
        assert out == expected_out
        assert err == ""
        max(1, b=2, c=3, d=10, e=12)
        out, err = capsys.readouterr()
        assert out == """max:a=1,b=2,c=3,d=10,e=12\n"""
        assert err == ""
        max(1, 2, 3, 10, 12)
        out, err = capsys.readouterr()
        assert out == """max:a=1,b=2,c=3,=10,=12\n"""
        assert err == ""

class TestLongOutput(object):

    def test_long_argument_data(self, capsys):
        long_string = '-' * 1000
        identity(long_string)
        expect_sys(capsys, out='identity:argument=--------..\n')


    def test_long_argument_name(self, capsys):
        long_string = '-' * 10
        identity(long_string, long_argument_name='-' * 200)
        expect_sys(capsys, out='identity:argument=----------,long.arg..name=--------..\n')


def expect_sys(capsys, out="", err=""):
    actual_out, actual_err = capsys.readouterr()
    assert actual_out == out
    assert actual_err == err
