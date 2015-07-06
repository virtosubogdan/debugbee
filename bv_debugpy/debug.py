""" Module for configuration and primary debug decorator. """
from __future__ import print_function
from collections import namedtuple
import functools
import inspect
from itertools import izip_longest
import os

CALLER_DEPTH = int(os.environ.get('DEBUGBY_CALLER_DEPTH', '3'))
LIST_ARGUMENTS = bool(os.environ.get('DEBUGBY_LIST_ARGUMENTS', 'True'))
IDENTATION = int(os.environ.get('DEBUGBY_IDENTATION', '4'))

State = namedtuple('State', ['depth'])
state = State(depth=0)


def debugpy(list_arguments=LIST_ARGUMENTS):
    def _decorator(func):
        @functools.wraps(func)
        def _function(*args, **kwargs):
            global state
            if state.depth < CALLER_DEPTH:
                log(func, args=args, kwargs=kwargs, parameters=compute_log_parameters())
            state = state._replace(depth=state.depth + 1)
            returned_value = func(*args, **kwargs)
            state = state._replace(depth=state.depth - 1)
            return returned_value
        return _function
    return _decorator


def log(function, args, kwargs, parameters):
    arguments = compute_arguments(function, args, kwargs)
    arguments_str = ','.join(str(k) + '=' + str(v) for k,v in arguments)
    full_value = function.func_name + ':' + arguments_str if arguments_str else function.func_name
    print(' ' * IDENTATION * state.depth + full_value)


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
    global CALLER_DEPTH, LIST_ARGUMENTS, IDENTATION
    CALLER_DEPTH = int(os.environ.get('DEBUGBY_CALLER_DEPTH', '3'))
    LIST_ARGUMENTS = bool(os.environ.get('DEBUGBY_LIST_ARGUMENTS', 'True'))
    IDENTATION = int(os.environ.get('DEBUGBY_IDENTATION', '4'))


def reset_to_default():
    """ Resets all configuration parameters to defaults. """
    global CALLER_DEPTH, LIST_ARGUMENTS, IDENTATION
    CALLER_DEPTH = 3
    LIST_ARGUMENTS = True
    IDENTATION = 4


def compute_log_parameters():
    return {}
