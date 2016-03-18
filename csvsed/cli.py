# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2009/08/04
# copy: (C) Copyright 2009-EOT metagriffin -- see LICENSE.txt
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

'''
Command-line interface to `csvsed.sed`.
'''

import re, sys

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, CSVFileType, parse_column_identifiers
from csvsed import sed

#------------------------------------------------------------------------------
class CsvSed(CSVKitUtility):

  description = 'A stream-oriented CSV modification tool. Like a ' \
      ' stripped-down "sed" command, but for tabular data.'
  override_flags = 'f'

  #----------------------------------------------------------------------------
  def add_arguments(self):
    self.argparser.add_argument(
      '-c', '--columns',
      dest='columns',
      help='A comma separated list of column indices or names to be modified.')
    # todo: support in-place file modification
    # todo: make sure that it supports backup spec, eg '-i.orig'
    # self.argparser.add_argument(
    #   '-i', '--in-place',
    #   dest='inplace',
    #   help='Modify a file in-place (with a value, specifies that the original'
    #   ' should be renamed first, e.g. "-i.orig")')
    self.argparser.add_argument(
      'expr', metavar='EXPR',
      help='The "sed" expression to evaluate: currently supports substitution'
      ' (s/REGEX/EXPR/FLAGS) and transliteration (y/SRC/DEST/FLAGS).')
    self.argparser.add_argument(
      'file', metavar='FILE',
      nargs='?', type=CSVFileType(), default=sys.stdin,
      help='The CSV file to operate on. If omitted or "-", will read from STDIN.')

  #----------------------------------------------------------------------------
  def main(self):
    reader = CSVKitReader(self.args.file, **self.reader_kwargs)
    cnames = reader.next()
    cids   = parse_column_identifiers(self.args.columns, cnames, self.args.zero_based)
    mods   = {idx: self.args.expr for idx in cids}
    output = CSVKitWriter(self.output_file, **self.writer_kwargs)
    reader = sed.CsvFilter(reader, mods, header=False)
    output.writerow(cnames)
    for row in reader:
      output.writerow(row)

#------------------------------------------------------------------------------
def main():
  utility = CsvSed()
  return utility.main()

if __name__ == '__main__':
  sys.exit(main())

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
