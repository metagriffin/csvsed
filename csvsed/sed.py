# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  csvsed.sed
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2009/08/04
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
A stream-oriented CSV modification tool. Like a stripped-down "sed"
command, but for tabular data.
'''

import re, string, types, subprocess, csvkit, csv
from csvkit.exceptions import ColumnIdentifierError

#------------------------------------------------------------------------------
class InvalidModifierSpec(Exception): pass

#------------------------------------------------------------------------------
class CsvFilter(object):
  def __init__(self, reader, modifiers, header=True):
    '''
    On-the-fly modifies CSV records coming from a csvkit reader object.

    :Parameters:

    reader : iter

      The CSV record source - must support the `next()` call, which
      should return a list of values.

    modifiers : { list, dict }

      Specifies a set of modifiers to apply to the `reader`, which can
      be either a sequence or dictionary of a modifiers to apply. If
      it is a sequence, then the modifiers are applied to the
      equivalently positioned cells in the input records. If it is a
      dictionary, the keys can be integers (column position) or
      strings (column name). In all cases, the modifiers can be one of
      the following:

      * function : takes a single string argument and returns a string
      * string : a sed-like modification specification.

      Currently supported modification specifications:

      * Substitution: "s/REGEX/REPL/FLAGS"

        Replaces regular expression `REGEX` with replacement string
        `REPL`, which can use back references. Supports the following
        flags:

        * i: case-insensitive
        * g: global replacement (otherwise only the first is replaced)
        * l: uses locale-dependent character classes
        * m: enables multiline matching for "^" and "$"
        * s: "." also matches the newline character
        * u: enables unicode escape sequences
        * x: `REGEX` uses verbose descriptors & comments

      * Transliteration: "y/SRC/DST/FLAGS"

        (This is a slightly modified version of sed's "y" command.)

        Each character in `SRC` is replaced with the corresponding
        character in `DST`. The dash character ("-") indicates a range
        of characters (e.g. "a-z" for all alphabetic characters).  If
        the dash is needed literally, then it must be the first or
        last character, or escaped with "\". The "\" character escapes
        itself. Only the "i" flag, indicating case-insensitive
        matching of `SRC`, is supported.

      Note that the "/" character can be any character as long as it
      is used consistently and not used within the specification,
      e.g. ``s|a|b|`` is equivalent to ``s/a/b/``.

    header : bool, optional, default: true

      If truthy (the default), then the first row will not be modified.
    '''
    self.reader    = reader
    self.header    = header
    self.cnames    = None if not header else reader.next()
    self.modifiers = standardize_modifiers(self.cnames, modifiers)

  #----------------------------------------------------------------------------
  def __iter__(self):
    return self

  #----------------------------------------------------------------------------
  def next(self):
    if self.header:
      self.header = False
      return self.cnames
    row = self.reader.next()
    for col, mod in self.modifiers.items():
      row[col] = mod(row[col])
    return row

#------------------------------------------------------------------------------
def standardize_modifiers(cnames, modifiers):
  # TODO: csvkit.grep.standardize_patterns could be refactored to support
  #       this process here as well...
  try:
    # Test to see if dictionary of modifiers
    modifiers = {k: v for k, v in modifiers.items() if v}
  except AttributeError:
    # Fallback to sequence of modifiers
    return {i: spec2modifier(v) for i, v in enumerate(modifiers) if v}
  modifiers = {k: spec2modifier(v) for k, v in modifiers.items()}
  if not cnames:
    return modifiers
  p2 = {}
  for k in modifiers:
    if k in cnames:
      idx = cnames.index(k)
      if idx in modifiers:
        raise ColumnIdentifierError(
          'Column %s has index %i which already has a pattern.' % (k,idx))
      p2[idx] = modifiers[k]
    else:
      p2[k] = modifiers[k]
  return p2

#------------------------------------------------------------------------------
def spec2modifier(obj):
  # obj is function
  if hasattr(obj, '__call__'):
    return obj
  # obj is a specification string
  return eval(obj[0].upper() + '_modifier')(obj)

#------------------------------------------------------------------------------
class S_modifier(object):
  'The "substitution" modifier ("s/REGEX/REPL/FLAGS").'
  def __init__(self, spec):
    super(S_modifier, self).__init__()
    if not spec or len(spec) < 4 or spec[0] != 's':
      raise InvalidModifierSpec(spec)
    sspec = spec.split(spec[1])
    if len(sspec) != 4:
      raise InvalidModifierSpec(spec)
    flags = 0
    for flag in sspec[3].upper():
      flags |= getattr(re, flag, 0)
    self.regex = re.compile(sspec[1], flags)
    self.repl  = sspec[2]
    self.count = 0 if 'g' in sspec[3].lower() else 1
  def __call__(self, value):
    return self.regex.sub(self.repl, value, count=self.count)

#------------------------------------------------------------------------------
def cranges(spec):
  # todo: there must be a better way...
  ret = ''
  idx = 0
  while idx < len(spec):
    c = spec[idx]
    idx += 1
    if c == '-' and len(ret) > 0 and len(spec) > idx:
      for i in range(ord(ret[-1]) + 1, ord(spec[idx]) + 1):
        ret += chr(i)
      idx += 1
      continue
    if c == '\\' and len(spec) > idx:
      c = spec[idx]
      idx += 1
    ret += c
  return ret

#------------------------------------------------------------------------------
class Y_modifier(object):
  'The "transliterate" modifier ("y/SOURCE/DESTINATION/FLAGS").'
  # todo: the python2 string.maketrans & string.translate functions
  #       only work on non-unicode input and csvkit produces unicode
  #       values... so the current 'y' modifier does not use them.
  #       *HOWEVER*, python3's version *does* work, so in py3 mode,
  #       use that!
  def __init__(self, spec):
    super(Y_modifier, self).__init__()
    if not spec or len(spec) < 4 or spec[0] != 'y':
      raise InvalidModifierSpec(spec)
    yspec = spec.split(spec[1])
    if len(yspec) != 4:
      raise InvalidModifierSpec(spec)
    yspec[1] = cranges(yspec[1])
    yspec[2] = cranges(yspec[2])
    if 'i' in yspec[3].lower():
      # self.table = string.maketrans(yspec[1].lower() + yspec[1].upper(),
      #                               2 * yspec[2])
      self.src = yspec[1].lower() + yspec[1].upper()
      self.dst = 2 * yspec[2]
    else:
      # self.table = string.maketrans(yspec[1], yspec[2])
      self.src = yspec[1]
      self.dst = yspec[2]
    if len(self.src) != len(self.dst):
      raise InvalidModifierSpec(spec)
  def __call__(self, value):
    # return string.translate(val, self.table)
    # TODO: this could be *much* more efficient...
    ret = ''
    for ch in value:
      idx = self.src.find(ch)
      if idx < 0:
        ret += ch
      else:
        ret += self.dst[idx]
    return ret

#------------------------------------------------------------------------------
class ReadlineIterator(object):
  'An iterator that calls readline() to get its next value.'
  # NOTE: this is a hack to make csv.reader not read-ahead.
  def __init__(self, f): self.f = f
  def __iter__(self): return self
  def next(self):
    line = self.f.readline()
    if not line: raise StopIteration
    return line

#------------------------------------------------------------------------------
class E_modifier(object):
  'The "execute" external program modifier ("e/PROGRAM+OPTIONS/FLAGS").'
  def __init__(self, spec):
    super(E_modifier, self).__init__()
    if not spec or len(spec) < 3 or spec[0] != 'e':
      raise InvalidModifierSpec(spec)
    espec = spec.split(spec[1])
    if len(espec) != 3:
      raise InvalidModifierSpec(spec)
    espec[2] = espec[2].lower()
    self.command = espec[1]
    self.index   = 1 if 'i' in espec[2] else None
    self.csv     = 'c' in espec[2]
    if not self.csv:
      return
    self.proc = subprocess.Popen(
      self.command, shell=True, bufsize=0,
      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    self.writer = csvkit.CSVKitWriter(self.proc.stdin)
    # note: not using csvkit's reader because there is no easy way of
    # making it not read-ahead (which breaks the "continuous" mode).
    # self.reader = csvkit.CSVKitReader(self.proc.stdout)
    # todo: fix csvkit so that it can be used in non-read-ahead mode.
    self.reader = csv.reader(ReadlineIterator(self.proc.stdout))
  def __call__(self, value):
    if not self.csv:
      return self.execOnce(value)
    self.writer.writerow([value])
    return self.reader.next()[0].decode('utf-8')
  def execOnce(self, value):
    p = subprocess.Popen(
      self.command, shell=True,
      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errput = p.communicate(value)
    if p.returncode != 0:
      raise Exception('command "%s" failed: %s' % (self.command, errput))
    if output[-1] == '\n':
      output = output[:-1]
    return output

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
