# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2011/04/08
# copy: (C) Copyright 2011-EOT metagriffin -- see LICENSE.txt
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

import unittest, StringIO, csvkit
from . import sed

#------------------------------------------------------------------------------
def run(source, modifiers, header=True):
  src = StringIO.StringIO(source)
  dst = StringIO.StringIO()
  reader = csvkit.CSVKitReader(src)
  reader = sed.CsvFilter(reader, modifiers, header=header)
  writer = csvkit.CSVKitWriter(dst)
  for row in reader:
    writer.writerow(row)
  return dst.getvalue()

#------------------------------------------------------------------------------
class TestSed(unittest.TestCase):

  baseCsv = '''\
header 1,header 2,header 3,header 4,header 5
field 1.1,field 1.2,field 1.3,field 1.4,field 1.5
field 2.1,field 2.2,field 2.3,field 2.4,field 2.5
field 3.1,field 3.2,field 3.3,field 3.4,field 3.5
'''

  #----------------------------------------------------------------------------
  def test_charRanges(self):
    self.assertEqual('abcdef', sed.cranges('a-f'))
    self.assertEqual('a-f', sed.cranges('a\-f'))
    self.assertEqual('abc-', sed.cranges('abc-'))
    self.assertEqual('-abc', sed.cranges('-abc'))
    self.assertEqual('a\]^_z', sed.cranges('a\\\\-_z'))
    self.assertEqual('abcdefg', sed.cranges('a-c-e-g'))

  #----------------------------------------------------------------------------
  def test_modifier_y_directcall(self):
    self.assertEqual(sed.Y_modifier('y/abc/def/')('b,a,c'), 'e,d,f')
    self.assertEqual(sed.Y_modifier('y/abc/def/')('b,A,C'), 'e,A,C')
    self.assertEqual(sed.Y_modifier('y/abc/def/i')('b,A,C'), 'e,d,f')
    self.assertEqual(sed.Y_modifier('y/a-z/A-Z/')('Back-Up'), 'BACK-UP')
    self.assertEqual(sed.Y_modifier('y/a\-z/A~Z/')('Back-Up'), 'BAck~Up')

  #----------------------------------------------------------------------------
  def test_modifier_y_toupper(self):
    chk = '''\
header 1,header 2,header 3,header 4,header 5
field 1.1,field 1.2,FIELD 1.3,field 1.4,field 1.5
field 2.1,field 2.2,FIELD 2.3,field 2.4,field 2.5
field 3.1,field 3.2,FIELD 3.3,field 3.4,field 3.5
'''
    self.assertEqual(run(self.baseCsv, {2: 'y/a-z/A-Z/'}), chk)

  #----------------------------------------------------------------------------
  def test_modifier_s_directcall(self):
    self.assertEqual(sed.S_modifier('s/a/b/')('abcabc'), 'bbcabc')
    self.assertEqual(sed.S_modifier('s/a/b/g')('abcabc'), 'bbcbbc')
    self.assertEqual(sed.S_modifier('s/a/b/g')('abcABC'), 'bbcABC')
    self.assertEqual(sed.S_modifier('s/a/b/gi')('abcABC'), 'bbcbBC')

  #----------------------------------------------------------------------------
  def test_modifier_s_noflags(self):
    chk = '''\
header 1,header 2,header 3,header 4,header 5
xield 1.1,field 1.2,field 1.3,field 1.4,field 1.5
xield 2.1,field 2.2,field 2.3,field 2.4,field 2.5
xield 3.1,field 3.2,field 3.3,field 3.4,field 3.5
'''
    self.assertMultiLineEqual(run(self.baseCsv, {0: 's/./x/'}), chk)

  #----------------------------------------------------------------------------
  def test_modifier_s_gflag(self):
    chk = '''\
header 1,header 2,header 3,header 4,header 5
xxxxxxxxx,field 1.2,field 1.3,field 1.4,field 1.5
xxxxxxxxx,field 2.2,field 2.3,field 2.4,field 2.5
xxxxxxxxx,field 3.2,field 3.3,field 3.4,field 3.5
'''
    self.assertMultiLineEqual(run(self.baseCsv, {0: 's/./x/g'}), chk)

  #----------------------------------------------------------------------------
  def test_modifier_s_multicol(self):
    chk = '''\
header 1,header 2,header 3,header 4,header 5
xxxxxxxxx,field 1.2,yyyyyyyyy,field 1.4,field 1.5
xxxxxxxxx,field 2.2,yyyyyyyyy,field 2.4,field 2.5
xxxxxxxxx,field 3.2,yyyyyyyyy,field 3.4,field 3.5
'''
    self.assertMultiLineEqual(run(self.baseCsv, {0: 's/./x/g', 2: 's/./y/g'}), chk)

  #----------------------------------------------------------------------------
  def test_modifier_s_colbyname(self):
    chk = '''\
header 1,header 2,header 3,header 4,header 5
xxxxxxxxx,field 1.2,yyyyyyyyy,field 1.4,field 1.5
xxxxxxxxx,field 2.2,yyyyyyyyy,field 2.4,field 2.5
xxxxxxxxx,field 3.2,yyyyyyyyy,field 3.4,field 3.5
'''
    self.assertMultiLineEqual(
      run(self.baseCsv, {'header 1': 's/./x/g', 'header 3': 's/./y/g'}), chk)

  #----------------------------------------------------------------------------
  def test_modifier_s_nomatch(self):
    chk = self.baseCsv
    self.assertMultiLineEqual(run(self.baseCsv, {0: 's/[IE]/../'}), chk)

  #----------------------------------------------------------------------------
  def test_modifier_s_iflag(self):
    chk = '''\
header 1,header 2,header 3,header 4,header 5
f..eld 1.1,field 1.2,field 1.3,field 1.4,field 1.5
f..eld 2.1,field 2.2,field 2.3,field 2.4,field 2.5
f..eld 3.1,field 3.2,field 3.3,field 3.4,field 3.5
'''
    self.assertMultiLineEqual(run(self.baseCsv, {0: 's/[IE]/../i'}), chk)

  #----------------------------------------------------------------------------
  def test_modifier_s_multiflag(self):
    chk = '''\
header 1,header 2,header 3,header 4,header 5
f....ld 1.1,field 1.2,field 1.3,field 1.4,field 1.5
f....ld 2.1,field 2.2,field 2.3,field 2.4,field 2.5
f....ld 3.1,field 3.2,field 3.3,field 3.4,field 3.5
'''
    self.assertMultiLineEqual(run(self.baseCsv, {0: 's/[IE]/../ig'}), chk)

  #----------------------------------------------------------------------------
  def test_modifier_s_remove(self):
    src = 'cell 1,"123,456,789.0"\n'
    chk = 'cell 1,123456789.0\n'
    self.assertMultiLineEqual(run(src, {1: 's/,//g'}, header=False), chk)

  #----------------------------------------------------------------------------
  def test_modifier_e_directcall(self):
    self.assertEqual(sed.E_modifier('e/tr ab xy/')('b,a,c'), 'y,x,c')
    self.assertEqual(sed.E_modifier('e/xargs -I {} echo "{}^2" | bc/')('4'), '16')

  #----------------------------------------------------------------------------
  def test_modifier_e_multipipe(self):
    chk = '''\
header 1,header 2,header 3,header 4,header 5
field 1.1,field 1.2,field 1.3,1.96,field 1.5
field 2.1,field 2.2,field 2.3,5.76,field 2.5
field 3.1,field 3.2,field 3.3,11.56,field 3.5
'''
    self.assertMultiLineEqual(
      run(self.baseCsv, {3: 'e/cut -f2 -d" " | xargs -I {} echo "scale=3;{}^2" | bc/'}), chk)

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
