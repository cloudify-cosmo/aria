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

from tosca_parser.import_resolver import AbstractImportResolver

from .suite import ParserTestCase

BLUEPRINT_1 = """
node_types:
    resolver_type_1:
        properties:
            key:
                default: 'default'
node_templates:
    resolver_1:
        type: resolver_type_1
        properties:
            key: value_1
"""
BLUEPRINT_2 = """
node_types:
    resolver_type_2:
        properties:
            key:
                default: 'default'
"""


class TestParseWithResolver(ParserTestCase):
    def test_parse_using_resolver(self):
        self.template.version_section('1.0')
        self.template += """
imports:
    -   http://url1
    -   http://url2"""

        urls = []

        class CustomResolver(AbstractImportResolver):
            def resolve(self, url):
                urls.append(url)
                if len(urls) == 2:
                    return BLUEPRINT_2
                return BLUEPRINT_1
        self.parse(import_resolver=CustomResolver())

        self.assertEqual(len(urls), 2)
        self.assertIn('http://url1', urls)
        self.assertIn('http://url2', urls)
