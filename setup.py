#!/usr/bin/env python

#
# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved.
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

from setuptools import setup
import sys

if sys.version_info < (2, 7):
    sys.exit('ARIA requires Python 2.7+')
if sys.version_info >= (3, 0):
    sys.exit('ARIA does not support Python 3')

setup(
    name='aria_openo',
    version='0.1',
    description='ARIA',
    license='Apache License Version 2.0',

    author='GigaSpaces',
    author_email='info@ariatosca.org',
    
    url='http://ariatosca.org/',
    download_url='https://github.com/aria-tosca',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration'],

    packages=[
        'aria_rest',
        'aria_openo'
    ],

    package_dir={
        'aria_rest': 'src/aria_rest',
        'aria_openo': 'src/aria_openo'
    },

    package_data={
        'aria_rest': ['swagger.yaml'],
    },

    entry_points={
        'console_scripts': [
            'aria-rest = aria_rest.__main__:main',
            'aria-openo = aria_openo.__main__:main']
    },
      
    # Please make sure this is in sync with src/aria/requirements.txt
    install_requires=['aria==0.1.0',
                      'connexion==1.1.4',
                      'python_daemon==2.1.2'])
