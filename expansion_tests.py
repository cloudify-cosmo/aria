"""
  Aria.parser Extension Demo
"""
from __future__ import print_function

import sys
import pprint
from functools import wraps, partial

from tosca_parser.framework.elements.blueprint import Blueprint
from tosca_parser.framework.functions import template_functions

from tosca_parser.extension_tools import (  # from tosca_parser.extension_tools the user can get:
    Element,                                # base-element class to create custom Element
    ElementExtension,                       # Element Extension object
    Function,                               # base-function class to create custom Function
    IntrinsicFunctionExtension,             # Function Extension object
)
from tosca_parser import parse, extend


def main_demo():
    print('create a new Debug Blueprint Element,')
    print('This is a Blueprint Element with a debug print on every func call')
    TestBlueprint = print_class_methods_args(
        Blueprint, prefix='Aria.parser Expansion Demo:\n')
    print('TestBlueprint: {0!r}'.format(TestBlueprint))

    print('creating a ElementExpansion object')
    print('In this ElementExpansion:')
    print('    action: replace element')
    print('    target_element: element to action on')
    print('    new_element: element to action with')
    element_expantion = ElementExtension(
        action=ElementExtension.REPLACE_ELEMENT_ACTION,
        target_element=Blueprint,
        new_element=TestBlueprint)
    print('element_expantion: {0!r}'.format(element_expantion))

    print('creating a PropertyFunctionExpansion object')
    print('In this PropertyFunctionExpansion:')
    print('    action: add function')
    print('    name: function name')
    print('    function: Function class to action with')
    function_expantion = IntrinsicFunctionExtension(
        action=IntrinsicFunctionExtension.ADD_FUNCTION_ACTION,
        name='test_function',
        function=type('TestFunction', (Function,), {}))
    print('function_expantion: {0!r}'.format(function_expantion))

    print('Expanding the aria.parser "Language"')
    extend(element_extentions=[element_expantion],
           function_expansions=[function_expantion])

    print('Check function expanded, result:'.format(
        bool(template_functions.get('test_function'))))

    tosca_template = (
        '/home/liorm/work/workspace/bootstrap/cloudify-manager-blueprints/'
        'openstack-manager-blueprint.yaml')
    print('Check element replacement expanding:')
    print("    for this test we'll run the parser")
    print('tosca-template: {0}'.format(tosca_template))
    plane = parse(tosca_template)

    print('results:')
    print('- plane keys: {0}'.format(plane.keys()))
    print('- plane version: {0}'.format(plane.version))
    print('- plane outputs: {0}'.format(plane.outputs.keys()))
    # print('- plane node_template:')
    # pprint.pprint(plane.node_templates)
    # print('- plane inputs:')
    # pprint.pprint(plane.inputs)
    print('Success!...')


def clean_main_demo():
    TestBlueprint = print_class_methods_args(
        Blueprint, prefix='Aria.parser Expansion Demo:\n')
    element_extension = ElementExtension(
        action=ElementExtension.REPLACE_ELEMENT_ACTION,
        target_element=Blueprint,
        new_element=TestBlueprint)

    function_expantion = IntrinsicFunctionExtension(
        action=IntrinsicFunctionExtension.ADD_FUNCTION_ACTION,
        name='test_function',
        function=type('TestFunction', (Function,), {}))

    extend(element_extentions=[element_extension],
           function_expansions=[function_expantion])

    tosca_template = (
        '/home/liorm/work/workspace/bootstrap/cloudify-manager-blueprints/'
        'openstack-manager-blueprint.yaml')
    parse(tosca_template)


def print_func_args(func=None, prefix='DEBUG:', class_name=None):
    """
    Decorator to print function call details - parameters names and effective values
    !!!Do not use on production ONLY for debug!!!
    :param func: decorated function to analyze
    :param prefix: prifix for the debug prints
    :param class_name: add class name to func' path
    :return: print_func_args wrapper
    """
    if func is None:
        return partial(print_func_args, prefix=prefix, class_name=class_name)

    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        arg_names = func.func_code.co_varnames[:func.func_code.co_argcount]
        args = func_args[:len(arg_names)]
        defaults = func.func_defaults or ()
        start = len(defaults) - (func.func_code.co_argcount - len(args))
        args += defaults[start:]
        params = zip(arg_names, args)
        args = func_args[len(arg_names):]
        if args:
            params.append(('args', args))
        if func_kwargs:
            params.append(('kwargs', func_kwargs))
        if class_name:
            func_path = func.__module__ + ':' + class_name + '.' + func.__name__
        else:
            func_path = func.__module__ + '.' + func.__name__
        print('%s %s(%s)' % (prefix, func_path, ', '.join('%s = %r' % p for p in params)))
        return func(*func_args, **func_kwargs)
    return wrapper


def print_class_methods_args(cls=None, prefix='DEBUG:'):
    """
    Decorate every class method with print_func_args decorator
    (won't work with classmethods and staticmethods)
    !!!Do not use on production ONLY for debug!!!
    :param cls: class to decorate
    :param prefix: prifix for the debug prints
    :return: Decorated class
    """
    if cls is None:
        return partial(print_class_methods_args, prefix=prefix)

    for name, method in vars(cls).iteritems():
        if callable(method):
            setattr(cls, name, print_func_args(
                method, prefix, class_name=cls.__name__))
    cls.__init__ = print_func_args(
        cls.__init__, prefix, class_name=cls.__name__)
    return cls

if __name__ == '__main__':
    sys.exit(main_demo())
