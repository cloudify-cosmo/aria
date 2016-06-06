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

from ..exceptions import DSLParsingLogicException
from ..framework import functions
from .. import utils
from ..constants import LOCAL_AGENT


def operation_mapping(
        implementation,
        inputs,
        executor=None,
        max_retries=None,
        retry_interval=None,
        **kwargs):
    return {
        'implementation': implementation,
        'inputs': inputs,
        'executor': executor or LOCAL_AGENT,
        'max_retries': max_retries,
        'retry_interval': retry_interval,
    }


def merge_schema_and_instance_inputs(schema_inputs, instance_inputs):
    flattened_schema_inputs = utils.flatten_schema(schema_inputs)
    merged_inputs = dict(
        flattened_schema_inputs.items() + instance_inputs.items())

    _validate_missing_inputs(merged_inputs, schema_inputs)
    _validate_inputs_types(merged_inputs, schema_inputs)
    return merged_inputs


def _validate_missing_inputs(inputs, schema_inputs):
    """Check that all inputs defined in schema_inputs exist in inputs"""

    missing_inputs = set(schema_inputs) - set(inputs)
    if missing_inputs:
        if len(missing_inputs) == 1:
            message = "Input '{0}' is missing a value".format(
                missing_inputs.pop())
        else:
            formatted_inputs = ', '.join("'{0}'".format(input_name)
                                         for input_name in missing_inputs)
            message = "Inputs {0} are missing a value".format(formatted_inputs)

        raise DSLParsingLogicException(107, message)


def _validate_inputs_types(inputs, schema_inputs):
    for input_key, _input in schema_inputs.iteritems():
        input_type = _input.get('type')
        if input_type is None:
            # no type defined - no validation
            continue
        input_val = inputs[input_key]

        if functions.parse(input_val) != input_val:
            # intrinsic function - not validated at the moment
            continue

        if input_type == 'integer':
            if isinstance(input_val, (int, long)) and not \
                    isinstance(input_val, bool):
                continue
        elif input_type == 'float':
            if isinstance(input_val, (int, float, long)) and not \
                    isinstance(input_val, bool):
                continue
        elif input_type == 'boolean':
            if isinstance(input_val, bool):
                continue
        elif input_type == 'string':
            continue
        else:
            raise DSLParsingLogicException(
                80, "Unexpected type defined in inputs schema "
                    "for input '{0}' - unknown type is {1}"
                    .format(input_key, input_type))

        raise DSLParsingLogicException(
            50, "Input type validation failed: Input '{0}' type "
                "is '{1}', yet it was assigned with the value '{2}'"
                .format(input_key, input_type, input_val))
