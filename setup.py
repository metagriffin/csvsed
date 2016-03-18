#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2009/08/04
# copy: (C) Copyright 2016-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import sys, os, re, setuptools
from setuptools import setup, find_packages

# require python 2.7+
if sys.hexversion < 0x02070000:
  raise RuntimeError('This package requires python 2.7 or better')

heredir = os.path.abspath(os.path.dirname(__file__))
def read(*parts):
  try:    return open(os.path.join(heredir, *parts)).read()
  except: return ''

test_dependencies = [
  'nose                 >= 1.3.0',
  'coverage             >= 3.6',
]

dependencies = [
  'distribute           >= 0.6.24',
  'argparse             >= 1.2.1',
  'csvkit               >= 0.5.0',
  'SQLAlchemy           >= 0.6.6',
  'dbf                  >= 0.94.003',
  'openpyxl             >= 1.5.7',
  'python-dateutil      >= 1.5',
  'xlrd                 >= 0.7.1',
]

entrypoints = {
  'console_scripts': [
    'csvsed             = csvsed.cli:main',
  ],
}

classifiers = [
  'Development Status :: 4 - Beta',
  # 'Development Status :: 5 - Production/Stable',
  'Environment :: Console',
  'Intended Audience :: Developers',
  'Intended Audience :: System Administrators',
  'Natural Language :: English',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Topic :: Software Development',
  'Topic :: Software Development :: Libraries :: Python Modules',
  'Topic :: Utilities',
  'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
]

setup(
  name                  = 'csvsed',
  version               = '0.2.2',
  description           = 'A stream-oriented CSV modification tool',
  long_description      = read('README.rst'),
  classifiers           = classifiers,
  author                = 'metagriffin',
  author_email          = 'metagriffin@uberdev.org',
  url                   = 'http://github.com/metagriffin/csvsed',
  keywords              = 'CSV comma separated values modification substitution translation transliteration command-line library',
  packages              = find_packages(),
  platforms             = ['any'],
  include_package_data  = True,
  zip_safe              = True,
  install_requires      = dependencies,
  tests_require         = test_dependencies,
  test_suite            = 'csvsed',
  entry_points          = entrypoints,
  license               = 'GPLv3+',
)

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
