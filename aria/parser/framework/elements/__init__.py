# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

from ... import exceptions
from ... import holder

PRIMITIVE_TYPES = (list, bool, int, float, long, basestring, dict)


UNPARSED = type('Unparsed', (object,), {})()


class ElementType(object):  # pylint: disable=too-few-public-methods
    def __init__(self, obj_type):
        if isinstance(obj_type, list):
            obj_type = tuple(obj_type)
        self.type = obj_type


class Leaf(ElementType):  # pylint: disable=too-few-public-methods
    pass


class Dict(ElementType):  # pylint: disable=too-few-public-methods
    pass


class List(ElementType):  # pylint: disable=too-few-public-methods
    pass


class Element(object):  # pylint: disable=too-many-instance-attributes
    schema = None
    required = False
    requires = {}
    provides = []
    extend = None
    supported_version = None

    def __new__(cls, *args, **kwargs):
        if callable(cls.extend):
            cls.extend.extend = None
            return cls.extend(*args, **kwargs)  # pylint: disable=not-callable
        return super(Element, cls).__new__(cls, *args, **kwargs)

    def __init__(self, context, initial_value, name=None):
        self.context = context
        initial_value = holder.Holder.from_object(initial_value)
        self.initial_value_holder = initial_value
        self._initial_value = initial_value.restore()
        self.start_line = initial_value.start_line
        self.start_column = initial_value.start_column
        self.end_line = initial_value.end_line
        self.end_column = initial_value.end_column
        self.filename = initial_value.filename
        name = holder.Holder.from_object(name)
        self.name = name.restore()
        self.name_start_line = name.start_line
        self.name_start_column = name.start_column
        self.name_end_line = name.end_line
        self.name_end_column = name.end_column
        self._parsed_value = UNPARSED
        self._provided = None

    def __str__(self):
        message = ''
        if self.filename:
            message += '\n  in: {0}'.format(self.filename)
        if self.name_start_line >= 0:
            message += (
                '\n  in line: {0}, column: {1}'.format(
                    self.name_start_line + 1,
                    self.name_start_column))
        elif self.start_line >= 0:
            message += '\n  in line {0}, column {1}'.format(
                self.start_line + 1, self.start_column)
        message += '\n  path: {0}'.format(self.path)
        message += '\n  value: {0}'.format(self._initial_value)

        return message

    def __repr__(self):
        return '{cls.__name__}({self.path})'.format(
            cls=self.__class__, self=self)

    def validate(self, **kwargs):
        pass

    def validate_version(self, version):
        if self.initial_value is None or self.supported_version is None:
            return
        if version.number < self.supported_version.number:
            raise exceptions.DSLParsingLogicException(
                exceptions.ERROR_CODE_DSL_DEFINITIONS_VERSION_MISMATCH,
                '{0} not supported in version {1}, it was added in {2}'.format(
                    self.name,
                    version,
                    self.supported_version.name))

    def parse(self, **_):
        return self.initial_value

    @property
    def index(self):
        """Alias name for list based elements"""
        return self.name

    @property
    def initial_value(self):
        return copy.deepcopy(self._initial_value)

    @property
    def value(self):
        if self._parsed_value == UNPARSED:
            raise exceptions.DSLParsingSchemaAPIException(
                exceptions.ERROR_CODE_ILLEGAL_VALUE_ACCESS,
                'Cannot access element value before parsing')
        return copy.deepcopy(self._parsed_value)

    @value.setter
    def value(self, val):
        self._parsed_value = val

    def calculate_provided(self, **_):
        return {}

    @property
    def provided(self):
        return copy.deepcopy(self._provided)

    @provided.setter
    def provided(self, value):
        self._provided = value

    @property
    def path(self):
        elements = [str(e.name) for e in self.context.ancestors_iter(self)]
        if elements:
            elements.pop()
        elements.reverse()
        elements.append(str(self.name))
        return '.'.join(elements)

    @property
    def defined(self):
        return self.value is not None or self.start_line is not None

    def parent(self):
        return next(self.context.ancestors_iter(self))

    def ancestor(self, element_type):
        matches = [e for e in self.context.ancestors_iter(self)
                   if isinstance(e, element_type)]
        if not matches:
            raise exceptions.DSLParsingElementMatchException(
                "No matches found for '{0}'".format(element_type))
        if len(matches) > 1:
            raise exceptions.DSLParsingElementMatchException(
                "Multiple matches found for '{0}'".format(element_type))
        return matches[0]

    def descendants(self, element_type):
        return [e for e in self.context.descendants(self)
                if isinstance(e, element_type)]

    def child(self, element_type):
        matches = [e for e in self.context.child_elements_iter(self)
                   if isinstance(e, element_type)]
        if not matches:
            raise exceptions.DSLParsingElementMatchException(
                "No matches found for '{0}'".format(element_type))
        if len(matches) > 1:
            raise exceptions.DSLParsingElementMatchException(
                "Multiple matches found for '{0}'".format(element_type))
        return matches[0]

    def build_dict_result(self):
        return dict((child.name, child.value)
                    for child in self.context.child_elements_iter(self))

    def children(self):
        return list(self.context.child_elements_iter(self))

    def sibling(self, element_type):
        return self.parent().child(element_type)


class DictElement(Element):
    def parse(self, **_):
        return self.build_dict_result()


class UnknownSchema(object):  # pylint: disable=too-few-public-methods
    pass


class UnknownElement(Element):
    schema = UnknownSchema()
