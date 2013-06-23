# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  csvsed.sed
# desc: a stream-oriented CSV modification tool.
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2009/08/04
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import re, string, types
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

        Each character in `SRC` is replaced with the corresponding
        character in `DST`. Only the "i" flag is supported.

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
  def __call__(self, val):
    return self.regex.sub(self.repl, val, count=self.count)

#------------------------------------------------------------------------------
class Y_modifier(object):
  'The "transliterate" modifier ("y/SOURCE/DESTINATION/FLAGS").'
  def __init__(self, spec):
    super(Y_modifier, self).__init__()
    if not spec or len(spec) < 4 or spec[0] != 'y':
      raise InvalidModifierSpec(spec)
    tspec = spec.split(spec[1])
    if len(tspec) != 4:
      raise InvalidModifierSpec(spec)
    if 'i' in tspec[3].lower():
      self.table = string.maketrans(tspec[1].lower() + tspec[1].upper(),
                                    2 * tspec[2])
    else:
      self.table = string.maketrans(tspec[1], tspec[2])
  def __call__(self, val):
    return string.translate(val, self.table)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
