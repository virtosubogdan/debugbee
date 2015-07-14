import os

from debugbee.parameter_names import *


def reset_environment():
    for variable in ('DEBUGBY_CALLER_DEPTH', 'DEBUGBY_LIST_ARGUMENTS', 'DEBUGBY_LIST_ARGUMENTS',
                     ENV_IDENTATION, ENV_OUTPUT_FILE):
        if variable in os.environ:
            del os.environ[variable]
