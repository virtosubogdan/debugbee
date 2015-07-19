#pylint: disable=maybe-no-member, global-statement, invalid-name, star-args
"""
Module for configuration and primary debug decorator.
"""
from __future__ import print_function
from collections import namedtuple
import functools
import inspect
from itertools import izip_longest
import os

import debugbee.parameter_names as pn

State = namedtuple('State', ['depth'])
state = State(depth=0)


def debugbee(**parameters):
    def _decorator(func):
        @functools.wraps(func)
        def _function(*args, **kwargs):
            return _debugbee_log(func, args, kwargs, parameters)
        return _function
    return _decorator


def debugbee_class(**parameters):
    def _decorator(cls):
        class DecoratedClass(cls):
            def __init__(self):
                computed_parameters = compute_parameters(parameters)
                write_message("init of {}".format(str(cls)), computed_parameters)
                cls.__init__(self)
                # TODO: don't get why this can't be used
                # super(DecoratedClass, self).__init__()

            def __getattribute__(self, name):
                attr = object.__getattribute__(self, name)
                if hasattr(attr, '__call__'):
                    def newfunc(*args, **kwargs):
                        return _debugbee_log(attr, args, kwargs, parameters, cls=cls, obj=self)
                    return newfunc
                else:
                    return attr
        return DecoratedClass
    return _decorator

def _debugbee_log(func, args, kwargs, parameters, cls=None, obj=None):
    global state
    parameters = compute_parameters(parameters)
    if state.depth < CALLER_DEPTH:
        log(func, args=args, kwargs=kwargs, parameters=parameters, cls=cls)
    state = state._replace(depth=state.depth + 1) # pylint: disable=protected-access
    returned_value = func(*args, **kwargs)
    state = state._replace(depth=state.depth - 1) # pylint: disable=protected-access
    return returned_value


def log(function, args, kwargs, parameters, cls):
    arguments = compute_arguments(function, args, kwargs, cls is not None)
    log_message = make_log_message(function.func_name, arguments, cls)

    overflow_charactes = len(log_message) - parameters[pn.MESSAGE_MAX_WIDTH]
    if overflow_charactes > 0:
        arguments, overflow_charactes = trim_arguments(arguments, overflow_charactes)
        log_message = make_log_message(function.func_name, arguments)
    write_message(log_message, parameters)


def write_message(log_message, parameters):
    if parameters[pn.OUT_FILE]:
        with open(parameters[pn.OUT_FILE], 'a') as outputfile:
            outputfile.write(log_message + '\n')
    else:
        print(log_message)

def make_log_message(function_name, arguments, cls=None):
    arguments_str = ''
    for name, value in arguments:
        if arguments_str:
            arguments_str += ','
        value_cls = type(value)
        if value_cls.__str__ == object.__str__:
            if value_cls.__module__ == 'debugbee.debug':
                value_cls = value_cls.__bases__[0]
            value = value_cls.__name__
        arguments_str += str(name) + '=' + str(value)
    full_value = function_name + ':' + arguments_str if arguments_str else function_name
    full_value = str(cls.__name__) + '.' + full_value if cls else full_value
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


def squash_arg_name(argument_name, max_part_len=4):
    new_name = '.'.join(part if len(part) <= max_part_len else part[:max_part_len-1] + '.'
                        for part in argument_name.split('_'))
    return len(argument_name) - len(new_name), new_name


def compute_arguments(function, args, kwargs, is_object):
    copied_kwargs = False
    cmp_arguments = []
    f_args, _, _, f_defaults = inspect.getargspec(function)
    extra_args = []
    for name, value in izip_longest(f_args, args):
        if is_object and name == 'self':
            continue
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
    CALLER_DEPTH = int(os.environ.get(pn.ENV_CALLER_DEPTH, '3'))
    LIST_ARGUMENTS = bool(os.environ.get(pn.ENV_LIST_ARGUMENTS, 'True'))
    IDENTATION = int(os.environ.get(pn.ENV_IDENTATION, '4'))
    OUTPUT_FILE = os.environ.get(pn.ENV_OUTPUT_FILE, None)
    OUT_WIDTH = os.environ.get(pn.ENV_OUT_WIDTH, 120)


def reset_to_default():
    """ Resets all configuration parameters to defaults. """
    global CALLER_DEPTH, LIST_ARGUMENTS, IDENTATION, OUTPUT_FILE, OUT_WIDTH
    CALLER_DEPTH = 3
    LIST_ARGUMENTS = True
    IDENTATION = 4
    OUTPUT_FILE = None
    OUT_WIDTH = 120


reload_configuration()


def compute_parameters(parameters=None):
    if not parameters:
        parameters = {}
    if pn.OUT_FILE not in parameters:
        parameters[pn.OUT_FILE] = OUTPUT_FILE
    if pn.MESSAGE_MAX_WIDTH not in parameters:
        parameters[pn.MESSAGE_MAX_WIDTH] = OUT_WIDTH
    return parameters
