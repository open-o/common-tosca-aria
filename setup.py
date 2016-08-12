
from setuptools import setup

install_requires = [
    'ruamel.yaml==0.11.11',
    'clint==0.5.1',

    # These are only required for tests
    'PyYAML==3.10'
]

try:
    from collections import OrderedDict  # NOQA
except ImportError, e:
    install_requires.append('ordereddict==1.1')

try:
    import importlib  # NOQA
except ImportError:
    install_requires.append('importlib')

setup(
    name='aria',
    version='0.1',
    author='GigaSpaces',
    author_email='cosmo-admin@gigaspaces.com',
    package_dir={'': 'src/aria'},
    packages=['aria',
              'aria.consumer',
              'aria.loader',
              'aria.parser',
              'aria.presenter',
              'aria.reader',
              'aria.tools',
              'tosca',
              'tosca.artifacts',
              'tosca.capabilities',
              #'tosca.capabilities.network',
              #'tosca.capabilities.nfv',
              'tosca.datatypes',
              #'tosca.datatypes.compute',
              #'tosca.datatypes.network',
              'tosca.groups',
              #'tosca.groups.nfv',
              'tosca.interfaces',
              'tosca.interfaces.node',
              #'tosca.interfaces.node.lifecycle',
              'tosca.nodes',
              #'tosca.nodes.network',
              #'tosca.nodes.nfv',
              'tosca.policies',
              'tosca.relationships',
              #'tosca.relationships.network',
              #'tosca.relationships.nfv',
              'dsl_parser'],
    license='LICENSE',
    description='ARIA',
    zip_safe=False,
    install_requires=install_requires
)
