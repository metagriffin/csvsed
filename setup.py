#!/usr/bin/env python
#------------------------------------------------------------------------------
# file: $Id: setup.py 346 2012-08-12 17:22:39Z griffin $
# desc: the csvsed installation file
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2009/08/04
# copy: (C) CopyLoose 2010 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import sys, os, re
from setuptools import setup, find_packages

if sys.hexversion < 0x02070000:
  raise RuntimeError('This package requires python 2.7 or better')

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

#------------------------------------------------------------------------------
# ugh. why couldn't github just have supported rst??? ignats.
#------------------------------------------------------------------------------
mdheader = re.compile('^(#+) (.*)$', flags=re.MULTILINE)
mdlevels = '=-~+"\''
def hdrepl(match):
  lvl = len(match.group(1)) - 1
  if lvl < 0:
    lvl = 0
  if lvl >= len(mdlevels):
    lvl = len(mdlevels) - 1
  ret = match.group(2).strip()
  return ret + '\n' + ( mdlevels[lvl] * len(ret) ) + '\n'
#------------------------------------------------------------------------------
mdquote = re.compile('^```(?: ?(\w+))?\n(.*?)\n```\n', flags=re.MULTILINE|re.DOTALL)
def qtrepl(match):
  if match.group(1) == 'python':
    ret = '.. code-block:: python\n'
  else:
    ret = '::\n'
  for line in match.group(2).split('\n'):
    if len(line.strip()) <= 0:
      ret += '\n'
    else:
      ret += '\n  ' + line
  return ret + '\n'
#------------------------------------------------------------------------------
mdimg = re.compile(r'!\[([^\]]*)\]\((.*?) "([^"]*)"\)')
imgrepl = '.. image:: \\2\n   :alt: \\1\n'
#------------------------------------------------------------------------------
def md2rst(text):
  text = mdquote.sub(qtrepl, text)
  text = mdheader.sub(hdrepl, text)
  text = mdimg.sub(imgrepl, text)
  return text
#------------------------------------------------------------------------------
README = md2rst(README)

test_packages = [
  'nose                 >= 1.3.0',
  'coverage             >= 3.6',
  ]

install_packages = [
  'csvkit               >= 0.5.0',
  ]

entry_points = {
  'console_scripts': [
    'csvsed             = csvsed.cli:main',
    ],
  }

setup(

  # generic info
  name                  = 'csvsed',
  version               = '0.2.1',

  # build instructions
  packages              = find_packages(),
  zip_safe              = True,
  include_package_data  = True,

  # dependencies
  install_requires      = install_packages,
  tests_require         = test_packages,

  # environment
  test_suite            = 'test',
  entry_points          = entry_points,

  # metadata for upload to PyPI
  url                   = 'http://github.com/metagriffin/csvsed',
  author                = 'metagriffin',
  author_email          = 'metagriffin@uberdev.org',
  description           = 'A stream-oriented CSV modification tool',
  license               = 'MIT (http://opensource.org/licenses/MIT)',
  keywords              = 'CSV comma separated values modification substitution translation transliteration command-line library',
  platforms             = ['any'],
  classifiers           = [
    'Development Status :: 4 - Beta',
    # 'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: Public Domain',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
  ],

  long_description      = README,

)

#------------------------------------------------------------------------------
# end of $Id: setup.py 346 2012-08-12 17:22:39Z griffin $
#------------------------------------------------------------------------------
