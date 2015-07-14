""" Module for configuration and primary debug decorator. """
from __future__ import print_function
from collections import namedtuple
import functools
import inspect
from itertools import izip_longest
import os

from .parameter_names import *

State = namedtuple('State', ['depth'])
state = State(depth=0)


def debugbee(**parameters):
    def _decorator(func):
        @functools.wraps(func)
        def _function(*args, **kwargs):
            global state
            if state.depth < CALLER_DEPTH:
                log(func, args=args, kwargs=kwargs, parameters=compute_parameters(parameters))
            state = state._replace(depth=state.depth + 1)
            returned_value = func(*args, **kwargs)
            state = state._replace(depth=state.depth - 1)
            return returned_value
        return _function
    return _decorator


def log(function, args, kwargs, parameters):
    arguments = compute_arguments(function, args, kwargs)
    log_message = make_log_message(function.func_name, arguments)

    overflow_charactes = len(log_message) - parameters[MESSAGE_MAX_WIDTH]
    if overflow_charactes > 0:
        arguments, overflow_charactes = trim_arguments(arguments, overflow_charactes)
        log_message = make_log_message(function.func_name, arguments)

    if parameters[OUT_FILE]:
        with open(parameters[OUT_FILE], 'a') as outputfile:
            outputfile.write(log_message + '\n')
    else:
        print(log_message)

def make_log_message(function_name, arguments):
    arguments_str = ','.join(str(k) + '=' + str(v) for k, v in arguments)
    full_value = function_name + ':' + arguments_str if arguments_str else function_name
    return ' ' * IDENTATION * state.depth + full_value


def trim_arguments(arguments, expected_gain):
    for index, argument_data in enumerate(arguments):
        arg_name, arg_value = argument_data
        if len(arg_name) > 10:
            gain, arg_name = squash_arg_name(arg_name)
            arguments[index] = (arg_name, arg_value)
            expected_gain -= gain
        if expected_gain <= 0:
            return arguments, 0
        str_val = str(arg_value)
        if len(str_val) > 10:
            expected_gain -= len(str_val) - 10
            arguments[index] = (arg_name, str_val[:8] + '..')
        if expected_gain <= 0:
            return arguments, 0
        str_val = str(arg_value)
    return arguments, expected_gain


def squash_arg_name(argument_name):
    return 0, argument_name


def compute_arguments(function, args, kwargs):
    copied_kwargs = False
    cmp_arguments = []
    f_args, _, _, f_defaults = inspect.getargspec(function)
    extra_args = []
    for name, value in izip_longest(f_args, args):
        if name is None:
            extra_args.append(('', value))
        elif value is None:
            if name in kwargs:
                if not copied_kwargs:
                    kwargs = dict(kwargs)
                    copied_kwargs = True
                real_value = kwargs[name]
                del kwargs[name]
            else:
                real_value = f_defaults[name]
            cmp_arguments.append((name, real_value))
        else:
            cmp_arguments.append((name, value))
    for karg_name in sorted(kwargs.keys()):
        cmp_arguments.append((karg_name, kwargs[karg_name]))
    return cmp_arguments + extra_args


def reload_configuration():
    """ Reloads the configuration parameters from the available sources. """
    global CALLER_DEPTH, LIST_ARGUMENTS, IDENTATION, OUTPUT_FILE, OUT_WIDTH
    CALLER_DEPTH = int(os.environ.get(ENV_CALLER_DEPTH, '3'))
    LIST_ARGUMENTS = bool(os.environ.get(ENV_LIST_ARGUMENTS, 'True'))
    IDENTATION = int(os.environ.get(ENV_IDENTATION, '4'))
    OUTPUT_FILE = os.environ.get(ENV_OUTPUT_FILE, None)
    OUT_WIDTH = os.environ.get(ENV_OUT_WIDTH, 120)


def reset_to_default():
    """ Resets all configuration parameters to defaults. """
    global CALLER_DEPTH, LIST_ARGUMENTS, IDENTATION, OUTPUT_FILE, OUT_WIDTH
    CALLER_DEPTH = 3
    LIST_ARGUMENTS = True
    IDENTATION = 4
    OUTPUT_FILE = None
    OUT_WIDTH = 120


reload_configuration()


def compute_parameters(parameters={}):
    if OUT_FILE not in parameters:
        parameters[OUT_FILE] = OUTPUT_FILE
    if MESSAGE_MAX_WIDTH not in parameters:
        parameters[MESSAGE_MAX_WIDTH] = OUT_WIDTH
    return parameters
