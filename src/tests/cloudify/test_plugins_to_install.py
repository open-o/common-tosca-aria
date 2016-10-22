#
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

from dsl_parser.constants import DEPLOYMENT_PLUGINS_TO_INSTALL

from .suite import (ParserTestCase,
                    op_struct,
                    get_node_by_name)


class NodePluginsToInstallTest(ParserTestCase):
    def test_no_duplicate_node_plugins_to_install_field_from_relationship(self):  # NOQA
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
  test_node1:
    type: cloudify.nodes.Compute
    interfaces:
      test_interface:
        start:
          implementation: test_plugin.start
          inputs: {}
    relationships:
      - type: cloudify.relationships.my_relationship
        target: test_node2
  test_node2:
    type: cloudify.nodes.Compute

node_types:
  cloudify.nodes.Compute: {}

plugins:
  test_plugin:
    executor: host_agent
    source: dummy

relationships:
  cloudify.relationships.my_relationship:
    source_interfaces:
      cloudify.interfaces.relationship_lifecycle:
        postconfigure:
          implementation: test_plugin.task.postconfigure
          inputs: {}
"""
        result = self.parse()
        node = get_node_by_name(result, 'test_node1')
        plugin = node['plugins_to_install'][0]
        self.assertEquals('test_plugin', plugin['name'])
        self.assertEquals(1, len(node['plugins_to_install']))

    def test_node_plugins_to_install_field_from_relationship(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
  test_node1:
    type: cloudify.nodes.Compute
    relationships:
      - type: cloudify.relationships.my_relationship
        target: test_node2
  test_node2:
    type: cloudify.nodes.Compute

node_types:
  cloudify.nodes.Compute: {}

plugins:
  test_plugin:
    executor: host_agent
    source: dummy

relationships:
  cloudify.relationships.my_relationship:
    source_interfaces:
      cloudify.interfaces.relationship_lifecycle:
        postconfigure:
          implementation: test_plugin.task.postconfigure
          inputs: {}
"""
        # TODO issue #1 in test_plugins_to_install
        result = self.parse()
        node = get_node_by_name(result, 'test_node1')
        plugin = node['plugins_to_install'][0]
        self.assertEquals('test_plugin', plugin['name'])
        self.assertEquals(1, len(node['plugins_to_install']))

    def test_node_plugins_to_install_field(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
    test_node1:
        type: cloudify.nodes.Compute
node_types:
    cloudify.nodes.Compute:
        interfaces:
            test_interface:
                start:
                    implementation: test_plugin.start
                    inputs: {}
plugins:
    test_plugin:
        executor: host_agent
        source: dummy
"""
        result = self.parse()
        plugin = result['nodes'][0]['plugins_to_install'][0]
        self.assertEquals('test_plugin', plugin['name'])
        self.assertEquals(1, len(result['nodes'][0]['plugins_to_install']))

    def test_node_plugins_to_install_field_plugins_from_contained_nodes(self):
        def get_plugin_to_install_from_node(node, plugin_name):
            for plugin in node['plugins_to_install']:
                if plugin['name'] == plugin_name:
                    return plugin
            return None

        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
   test_node1:
      type: cloudify.nodes.Compute
   test_node2:
      type: test_type
      relationships:
        -  type: cloudify.relationships.contained_in
           target: test_node1
   test_node3:
      type: test_type2
      relationships:
        -  type: cloudify.relationships.contained_in
           target: test_node2
   test_node4:
      type: test_type
      relationships:
        -  type: cloudify.relationships.contained_in
           target: test_node3
node_types:
   cloudify.nodes.Compute: {}
   test_type:
      interfaces:
        test_interface:
           start:
              implementation: test_plugin.start
              inputs: {}
   test_type2:
      interfaces:
        test_interface2:
           install:
              implementation: test_plugin2.install
              inputs: {}
relationships:
   cloudify.relationships.contained_in: {}
plugins:
   test_plugin:
      executor: host_agent
      source: dummy
   test_plugin2:
      executor: host_agent
      source: dummy
"""
        result = self.parse()

        self.assertEquals(4, len(result['nodes']))
        test_node2 = get_node_by_name(result, 'test_node2')
        # TODO issue #2 in test_plugins_to_install
        # ensuring non-host nodes don't have this field
        self.assertTrue('plugins_to_install' not in test_node2)
        test_node1 = get_node_by_name(result, 'test_node1')
        test_plugin = get_plugin_to_install_from_node(test_node1, 'test_plugin')
        test_plugin2 = get_plugin_to_install_from_node(test_node1, 'test_plugin2')
        self.assertEquals('test_plugin', test_plugin['name'])
        self.assertEquals('test_plugin2', test_plugin2['name'])
        self.assertEquals(2, len(test_node1['plugins_to_install']))

    def test_instance_relationships_target_node_plugins(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template.node_type_section()
        self.template.node_template_section()
        self.template += """
  test_node2:
    type: test_type
    relationships:
      - type: test_relationship
        target: test_node
        source_interfaces:
          test_interface1:
            install: test_plugin1.install
      - type: test_relationship
        target: test_node
        target_interfaces:
          test_interface1:
            install: test_plugin2.install
relationships:
  test_relationship: {}
plugins:
  test_plugin1:
    executor: central_deployment_agent
    source: dummy
  test_plugin2:
    executor: central_deployment_agent
    source: dummy
"""
        result = self.parse()
        self.assertEquals(2, len(result['nodes']))

        test_node2 = get_node_by_name(result, 'test_node2')
        self.assertEquals('test_node2', test_node2['id'])
        self.assertEquals(2, len(test_node2['relationships']))

        relationship1 = test_node2['relationships'][0]
        self.assertEquals('test_relationship', relationship1['type'])
        self.assertEquals('test_node', relationship1['target_id'])
        rel1_source_ops = relationship1['source_operations']
        self.assertEqual(
            op_struct('test_plugin1', 'install',
                      executor='central_deployment_agent'),
            rel1_source_ops['install'])
        self.assertEqual(
            op_struct('test_plugin1', 'install',
                      executor='central_deployment_agent'),
            rel1_source_ops['test_interface1.install'])
        self.assertEquals(2, len(rel1_source_ops))
        self.assertEquals(8, len(relationship1))

        plugin1_def = test_node2['plugins'][1]
        self.assertEquals('test_plugin1', plugin1_def['name'])

        relationship2 = test_node2['relationships'][1]
        self.assertEquals('test_relationship', relationship2['type'])
        self.assertEquals('test_node', relationship2['target_id'])

        rel2_source_ops = relationship2['target_operations']
        self.assertEqual(
            op_struct('test_plugin2', 'install',
                      executor='central_deployment_agent'),
            rel2_source_ops['install'])
        self.assertEqual(
            op_struct('test_plugin2', 'install',
                      executor='central_deployment_agent'),
            rel2_source_ops['test_interface1.install'])
        self.assertEquals(2, len(rel2_source_ops))
        self.assertEquals(8, len(relationship2))

        # expecting the other plugin to be under test_node rather than
        # test_node2:
        test_node1 = get_node_by_name(result, 'test_node')
        plugin2_def = test_node1['plugins'][0]
        self.assertEquals('test_plugin2', plugin2_def['name'])


class DeploymentPluginsToInstallTest(ParserTestCase):
    def test_one_central_one_host_plugin_on_same_node(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
  test_node1:
    type: cloudify.nodes.Compute
node_types:
  cloudify.nodes.Compute:
    interfaces:
      test_interface:
        start:
          implementation: test_plugin.start
          inputs: {}
        create:
          implementation: test_management_plugin.create
          inputs: {}
plugins:
  test_plugin:
    executor: host_agent
    source: dummy
  test_management_plugin:
    executor: central_deployment_agent
    source: dummy
"""
        result = self.parse()
        deployment_plugins = result['nodes'][0][DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(1, len(deployment_plugins))
        plugin = deployment_plugins[0]
        self.assertEquals('test_management_plugin', plugin['name'])

        # check the property on the plan is correct
        deployment_plugins = result[DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(1, len(deployment_plugins))

    def test_one_central_overrides_host_plugin(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_types:
  test_type: {}
node_templates:
  test_node1:
    type: test_type
    interfaces:
      test_interface:
        start:
          implementation: test_plugin.start
          executor: central_deployment_agent
plugins:
  test_plugin:
    executor: host_agent
    source: dummy
"""
        result = self.parse()
        node = get_node_by_name(result, 'test_node1')
        deployment_plugins = node[DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(1, len(deployment_plugins))
        plugin = deployment_plugins[0]
        self.assertEquals('test_plugin', plugin['name'])
        # TODO issue #3 in test_plugins_to_install
        self.assertIsNone(node.get('plugins_to_install'))
        # check the property on the plan is correct
        deployment_plugins = result[DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(1, len(deployment_plugins))
        plugin = deployment_plugins[0]
        self.assertEquals('test_plugin', plugin['name'])

    def test_node_plugins_to_install_no_host(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
  test_node1:
    type: cloudify.nodes.Root
node_types:
  cloudify.nodes.Root:
    interfaces:
      test_interface:
        start:
          implementation: cloud.server.start
          inputs: {}
plugins:
  cloud:
    executor: central_deployment_agent
    source: dummy
"""
        result = self.parse()
        self.assertEquals(1, len(result[DEPLOYMENT_PLUGINS_TO_INSTALL]))

    def test_same_plugin_one_two_nodes(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
  test_node1:
    type: cloudify.nodes.Compute
  test_node2:
    type: cloudify.nodes.Compute

node_types:
  cloudify.nodes.Compute:
    interfaces:
      test_interface:
        start:
          implementation: test_management_plugin.start
          inputs: {}

plugins:
  test_management_plugin:
    executor: central_deployment_agent
    source: dummy
"""
        result = self.parse()
        for node in result['nodes']:
            deployment_plugins = node[DEPLOYMENT_PLUGINS_TO_INSTALL]
            self.assertEquals(1, len(deployment_plugins))
            plugin = deployment_plugins[0]
            self.assertEquals('test_management_plugin', plugin['name'])

        deployment_plugins = result[DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(1, len(deployment_plugins))

    def test_two_plugins_on_one_node(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
  test_node1:
    type: cloudify.nodes.Compute

node_types:
  cloudify.nodes.Compute:
    interfaces:
      test_interface:
        start:
          implementation: test_management_plugin1.start
          inputs: {}
        create:
          implementation: test_management_plugin2.create
          inputs: {}

plugins:
  test_management_plugin1:
    executor: central_deployment_agent
    source: dummy
  test_management_plugin2:
    executor: central_deployment_agent
    source: dummy
"""
        result = self.parse()
        deployment_plugins = result['nodes'][0][DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(2, len(deployment_plugins))

        # TODO issue #4 in test_plugins_to_install
        # check the property on the plan is correct
        deployment_plugins = result[DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(2, len(deployment_plugins))

    def test_two_identical_plugins_on_node(self):
        self.template.version_section('cloudify_dsl', '1.0')
        self.template += """
node_templates:
  test_node1:
    type: cloudify.nodes.Compute

node_types:
  cloudify.nodes.Compute:
    interfaces:
      test_interface:
        start:
          implementation: test_management_plugin.start
          inputs: {}
        create:
          implementation: test_management_plugin.create
          inputs: {}

plugins:
  test_management_plugin:
    executor: central_deployment_agent
    source: dummy
"""
        result = self.parse()
        deployment_plugins = result['nodes'][0][DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(1, len(deployment_plugins))

        # check the property on the plan is correct
        deployment_plugins = result[DEPLOYMENT_PLUGINS_TO_INSTALL]
        self.assertEquals(1, len(deployment_plugins))