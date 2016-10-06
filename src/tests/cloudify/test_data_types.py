from .suite import (get_node_by_name,
                    ParserTestCase,
                    TempDirectoryTestCase,
                    CloudifyParserError
                    )

from dsl_parser.exceptions import (
    DSLParsingLogicException,
    DSLParsingException,
    ERROR_UNKNOWN_TYPE,
    ERROR_CODE_CYCLE,
    ERROR_VALUE_DOES_NOT_MATCH_TYPE,
    ERROR_INVALID_TYPE_NAME,
)


class TestDataTypes(ParserTestCase, TempDirectoryTestCase):
    def test_unknown_type(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template.data_types_section(
            properties_first='\n        type: unknown-type')
        self.assert_parser_issue_messages(
            ['"type" refers to an unknown data type in "first": u\'unknown-type\''])

    def test_simple(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template.data_types_section()
        self.parse()

    def test_definitions(self):
        extras = (
            '  pair_of_pairs_type:\n'
            '    properties:\n'
            '      first:\n'
            '        type: pair_type\n'
            '      second:\n'
            '        type: pair_type\n'
        )
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template.data_types_section(extras=extras)
        self.parse()

    def test_infinite_list(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template += (
            '\n'
            'data_types:\n'
            '  list_type:\n'
            '    properties:\n'
            '      head:\n'
            '        type: integer\n'
            '      tail:\n'
            '        type: list_type\n'
            '        default:\n'
            '          head: 1\n'
        )
        self.assert_parser_issue_messages(
            ['type of property "tail" creates a circular value hierarchy: u\'list_type\''])

    def test_definitions_with_default_error(self):
        extras = (
            '  pair_of_pairs_type:\n'
            '    properties:\n'
            '      first:\n'
            '        type: pair_type\n'
            '        default:\n'
            '          first: 1\n'
            '          second: 2\n'
            '          third: 4\n'
            '      second:\n'
            '        type: pair_type\n'
        )
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template.data_types_section(extras=extras)

        # TODO issue #1 in the second section of test_data_types

    def test_unknown_type_in_datatype(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template += """
data_types:
  pair_type:
    properties:
      first:
        type: unknown-type
      second: {}
"""
        self.assert_parser_issue_messages(
            ['"type" refers to an unknown data type in "first": u\'unknown-type\''])

    def test_nested_validation(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
node_templates:
  n_template:
    type: n_type
    properties:
      n_pair:
        second:
          first: 4
          second: invalid_type_value
node_types:
  n_type:
    properties:
      n_pair:
        type: pair_of_pairs_type
data_types:
  pair_type:
    properties:
      first: {}
      second:
        type: integer
  pair_of_pairs_type:
    properties:
      first:
        type: pair_type
        default:
          first: 1
          second: 2
      second:
        type: pair_type
"""
        self.assert_parser_issue_messages(
            ['field "n_pair" is not a valid "int": \'invalid_type_value\'',
             'required property "second" in type "pair_type" is not assigned a value in "n_pair"'
             ])

    def test_nested_defaults(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
node_types:
  vm_type:
    properties:
      agent:
        type: agent
node_templates:
  vm:
    type: vm_type
    properties:
      agent: {}
data_types:
  agent_connection:
    properties:
      username:
        type: string
        default: ubuntu
      key:
        type: string
        default: ~/.ssh/id_rsa

  agent:
    properties:
      connection:
        type: agent_connection
        default: {}
      basedir:
        type: string
        default: /home/
"""
        parsed = self.parse()
        vm = get_node_by_name(parsed, 'vm')
        self.assertEqual(
            'ubuntu',
            vm['properties']['agent']['connection']['username'])

    def test_derives(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
node_types:
  vm_type:
    properties:
      agent:
        type: agent
node_templates:
  vm:
    type: vm_type
    properties:
      agent:
        connection:
          key: /home/ubuntu/id_rsa
data_types:
  agent_connection:
    properties:
      username:
        type: string
        default: ubuntu
      key:
        type: string
        default: ~/.ssh/id_rsa
  agent:
    derived_from: agent_installer
    properties:
      basedir:
        type: string
        default: /home/
  agent_installer:
    properties:
      connection:
        type: agent_connection
        default: {}
"""
        parsed = self.parse()
        vm = get_node_by_name(parsed, 'vm')
        self.assertEqual(
            'ubuntu',
            vm['properties']['agent']['connection']['username'])
        self.assertEqual(
            '/home/ubuntu/id_rsa',
            vm['properties']['agent']['connection']['key'])

    def test_nested_type_error(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
node_templates:
  node:
    type: node_type
    properties:
      a:
        b:
          c:
            d: should_be_int
node_types:
  node_type:
    properties:
      a:
        type: a
data_types:
  a:
    properties:
      b:
        type: b
  b:
    properties:
      c:
        type: c
  c:
    properties:
      d:
        type: integer

"""
        self.assert_parser_issue_messages(
            ['field "a" is not a valid "int": \'should_be_int\'',
             'required property "d" in type "c" is not assigned a value in "a"'
             ])

    def test_unknown_parent(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template += """
data_types:
  a:
    derived_from: b
    properties:
      p:
        type: integer
"""
        ex = self.assertRaises(CloudifyParserError, self.parse)
        self.assertIn('unknown parent type "b" in "a"',
                      ex.message)

    def test_redefine_primitive(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template += """
data_types:
  integer:
    properties:
      p:
        type: string
"""

    def test_subtype_override_field_type(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
node_templates:
  node:
    type: node_type
    properties:
      b:
        i: 'redefined from int'
        s: 'to make sure that b really derives from a'
node_types:
  node_type:
    properties:
      b:
        type: b
data_types:
  a:
    properties:
      i:
        type: integer
      s:
        type: string
  b:
    derived_from: a
    properties:
      i:
        type: string
"""
        self.parse()

    def test_nested_type_error_in_default(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template += """
data_types:
  a:
    properties:
      b:
        type: b
        default:
          c:
            d:
              e: 'should be int'
  b:
    properties:
      c:
        type: c
  c:
    properties:
      d:
        type: d
  d:
    properties:
      e:
        type: integer
"""
        self.assert_parser_issue_messages([
            'field "b" is not a valid "int": \'should be int\'',
        ])

    def test_nested_merging(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
node_templates:
  node:
    type: node_type
    properties:
      b: {}
node_types:
  node_type:
    properties:
      b:
        type: b
        default:
          i: 'it will be used too'
      bb:
        type: b
        default:
          i: 'it will be used'
data_types:
  a:
    properties:
      i:
        type: integer
      s:
        type: string
        default: 's string'
  b:
    derived_from: a
    properties:
      i:
        type: string
        default: 'i string'
"""
        parsed = self.parse()
        node = get_node_by_name(parsed, 'node')
        expected = {
            'b': {
                'i': 'it will be used too',
                's': 's string'
            },
            'bb': {
                'i': 'it will be used',
                's': 's string'
            }
        }
        self.assertEqual(expected, node['properties'])

    def test_complex_nested_merging(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
data_types:
  data1:
    properties:
      inner:
        type: data1_inner
        default:
          inner3: inner3_override
          inner6:
            inner2_3: inner2_3_override
  data12:
    derived_from: data1
    properties:
      inner:
        type: data1_inner
        default:
          inner4: inner4_override
          inner6:
            inner2_4: inner2_4_override
  data1_inner:
    properties:
      inner1:
        default: inner1_default
      inner2:
        default: inner2_default
      inner3:
        default: inner3_default
      inner4:
        default: inner4_default
      inner5:
        default: inner5_default
      inner6:
        type: data2_inner
        default:
          inner2_2: inner2_2_override
      inner7: {}
  data2_inner:
    properties:
      inner2_1:
        default: inner2_1_default
      inner2_2:
        default: inner2_2_default
      inner2_3:
        default: inner2_3_default
      inner2_4:
        default: inner2_4_default
      inner2_5:
        default: inner2_5_default
      inner2_6:
        default: inner2_6_default
node_types:
  type1:
    properties:
      prop1:
        type: data1
        default:
          inner:
            inner4: inner4_override
            inner6:
              inner2_4: inner2_4_override
  type2:
    derived_from: type1
    properties:
      prop1:
        type: data1
        default:
          inner:
            inner5: inner5_override
            inner6:
              inner2_5: inner2_5_override
            inner7: inner7_override
  type3:
    derived_from: type1
    properties:
      prop1:
        type: data12
        default:
          inner:
            inner5: inner5_override
            inner6:
              inner2_5: inner2_5_override
            inner7: inner7_override

node_templates:
  node1:
    type: type1
    properties:
      prop1:
        inner:
          inner2: inner2_override
          inner6:
            inner2_6: inner2_6_override
          inner7: inner7_override
  node2:
    type: type2
    properties:
      prop1:
        inner:
          inner2: inner2_override
          inner6:
            inner2_6: inner2_6_override
  node3:
    type: type3
    properties:
      prop1:
        inner:
          inner2: inner2_override
          inner6:
            inner2_6: inner2_6_override
"""
        parsed = self.parse()

        def prop1(node_name):
            return get_node_by_name(parsed, node_name)['properties']['prop1']
        node1_prop = prop1('node1')
        node2_prop = prop1('node2')
        node3_prop = prop1('node3')
        self.assertEqual(
            {'inner': {'inner1': 'inner1_default',
                       'inner2': 'inner2_override',
                       'inner3': 'inner3_override',
                       'inner4': 'inner4_override',
                       'inner5': 'inner5_default',
                       'inner7': 'inner7_override',
                       'inner6': {'inner2_1': 'inner2_1_default',
                                  'inner2_2': 'inner2_2_override',
                                  'inner2_3': 'inner2_3_override',
                                  'inner2_4': 'inner2_4_override',
                                  'inner2_5': 'inner2_5_default',
                                  'inner2_6': 'inner2_6_override'}}}, node1_prop)
        self.assertEqual(
            {'inner': {'inner1': 'inner1_default',
                       'inner2': 'inner2_override',
                       'inner3': 'inner3_override',
                       'inner4': 'inner4_override',
                       'inner5': 'inner5_override',
                       'inner7': 'inner7_override',
                       'inner6': {'inner2_1': 'inner2_1_default',
                                  'inner2_2': 'inner2_2_override',
                                  'inner2_3': 'inner2_3_override',
                                  'inner2_4': 'inner2_4_override',
                                  'inner2_5': 'inner2_5_override',
                                  'inner2_6': 'inner2_6_override'}}}, node2_prop)
        self.assertEqual(
            {'inner': {'inner1': 'inner1_default',
                       'inner2': 'inner2_override',
                       'inner3': 'inner3_override',
                       'inner4': 'inner4_override',
                       'inner5': 'inner5_override',
                       'inner7': 'inner7_override',
                       'inner6': {'inner2_1': 'inner2_1_default',
                                  'inner2_2': 'inner2_2_override',
                                  'inner2_3': 'inner2_3_override',
                                  'inner2_4': 'inner2_4_override',
                                  'inner2_5': 'inner2_5_override',
                                  'inner2_6': 'inner2_6_override'}}}, node3_prop)

    def test_partial_default_validation_in_node_template(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
data_types:
  datatype:
    properties:
      prop1: {}
      prop2: {}
node_types:
  type:
    properties:
      prop:
        type: datatype
        default:
          prop1: value
node_templates:
  node:
    type: type
"""
        ex = self.assertRaises(CloudifyParserError, self.parse)
        self.assertIn('required property "prop2" in type "datatype" '
                      'is not assigned a value in "node"',
                      ex.message)

    def test_additional_fields_validation(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
data_types:
  datatype:
    properties:
      prop1:
        required: false
node_types:
  type:
    properties:
      prop:
        type: datatype
        default:
          prop2: value
node_templates:
  node:
    type: type
"""
        self.assert_parser_issue_messages(
            ['assignment to undefined property "prop2" in type "datatype" in "node"'])

    def test_nested_required_false(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
data_types:
  a:
    properties:
      b: {}

node_types:
  type:
    properties:
      a:
        type: a
        required: false
node_templates:
  node1:
    type: type
"""
        self.parse()

    def test_nested_merge_with_inheritance(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
data_types:
  a:
    properties:
      b:
        default: b_default
node_types:
  type:
    properties:
      a:
        type: a
        default:
          b: b_override
  type2:
    derived_from: type
    properties:
      a:
        type: a
node_templates:
  node:
    type: type2
"""
        parsed = self.parse()
        node = get_node_by_name(parsed, 'node')
        self.assertEqual(node['properties']['a']['b'], 'b_override')

    def test_version_check(self):
        self.template.version_section('cloudify_dsl', '1.1')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template += """
data_types:
  a:
    properties:
      i:
        type: integer
"""
        ex = self.assertRaises(CloudifyParserError, self.parse)
        self.assertIn('field "data_types" is not supported in '
                      '"aria_extension_cloudify.v1_1.templates.ServiceTemplate"',
                      ex.message)

    def test_implicit_default_value(self):
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
data_types:
  data1:
    properties:
      inner:
        default: inner_default

node_types:
  type1:
    properties:
      prop1:
        type: data1

node_templates:
  node1:
    type: type1
"""
        parsed = self.parse()
        node1 = parsed['nodes'][0]
        self.assertEqual(node1['properties']['prop1']['inner'],
                         'inner_default')

    def test_imports_merging(self):
        import_path = self.make_yaml_file(
            content="""
data_types:
  data1:
    properties:
      prop1:
        default: value1
""")
        self.template.version_section('cloudify_dsl', '1.2')
        self.template += """
imports:
  - {0}
data_types:
  data2:
    properties:
      prop2:
        default: value2
node_types:
  type:
    properties:
      prop1:
        type: data1
      prop2:
        type: data2
node_templates:
  node:
    type: type
""".format(import_path)
        properties = self.parse()['nodes'][0]['properties']
        self.assertEqual(properties['prop1']['prop1'], 'value1')
        self.assertEqual(properties['prop2']['prop2'], 'value2')