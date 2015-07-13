import os

from bv_debugpy.debug import debugpy, reload_configuration, reset_to_default
from testutils import *

FILE1 = "/tmp/output_test.out"
FILE2 = "/tmp/output_test2.out"

@debugpy(outputfile=FILE1)
def simple_function():
    return "simple_result"

@debugpy()
def simple_function_no_param():
    return "simple_result"

@debugpy(outputfile=FILE1)
def fibbonaci(number):
    return 1 if number == 0 or number == 1 else (fibbonaci(number-1) + fibbonaci(number-2))

class TestParameters(object):

    @classmethod
    def setup_class(cls):
        reset_environment()

    def setup_method(self, method):
        with open(FILE1, 'w'):
            pass
        with open(FILE2, 'w'):
            pass

    def test_output_to_file(self, capsys):
        os.environ['DEBUGBEE_OUTPUT_FILE'] = FILE2
        reload_configuration()
        simple_function()
        self.assertOutput(FILE1, capsys, "simple_function\n")

    def test_appending_data_to_file(self, capsys):
        simple_function()
        fibbonaci(3)
        self.assertOutput(FILE1, capsys, """simple_function
fibbonaci:number=3
    fibbonaci:number=2
        fibbonaci:number=1
        fibbonaci:number=0
    fibbonaci:number=1
""")

    def test_output_to_file_env_set(self, capsys):
        os.environ['DEBUGBEE_OUTPUT_FILE'] = FILE2
        reload_configuration()
        simple_function_no_param()
        self.assertOutput(FILE2, capsys, "simple_function_no_param\n")

    def assertOutput(self, filename, capsys, expected):
        with open(filename, 'r') as out:
            assert out.read() == expected
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""
