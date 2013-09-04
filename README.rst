======
csvmod
======

A stream-oriented CSV modification tool. Like a stripped-down "sed"
command, but for tabular data.


Installation
============

.. code-block:: bash

  $ pip install csvsed


Usage and Examples
==================

Installation of the `csvsed` python package also installs the
``csvsed`` command-line tool. Use ``csvsed --help`` for all command
line options, but here are some examples to get you going. Given the
input file ``sample.csv``:

.. code-block:: text

  Employee ID,Age,Wage,Status
  8783,47,"104,343,873.83","All good, but nowhere to go."
  2003,32,"98,878,784.00",A-OK

Removing thousands-separators from the "Wage" column using the "s"
(substitute) modifier:

.. code-block:: bash

  $ cat sample.csv | csvsed -c Wage s/,//g
  Employee ID,Age,Wage,Status
  8783,47,104343873.83,"All good, but nowhere to go."
  2003,32,98878784.00,A-OK

Convert/extract some text using the "s" (substitute) and "y"
(transliterate) modifiers:

.. code-block:: bash

  $ cat sample.csv | csvsed -c Status 's/^All (.*),.*/\1/' \
    | csvsed -c Status 's/^A-(.*)/\1/' \
    | csvsed -c Status 'y/a-z/A-Z/'
  Employee ID,Age,Wage,Status
  8783,47,"104,343,873.83",GOOD
  2003,32,"98,878,784.00",OK

Square the "Age" column using the "e" (execute) modifier:

.. code-block:: bash

  $ cat sample.csv | csvsed -c Age 'e/xargs -I {} echo "{}^2" | bc/'
  Employee ID,Age,Wage,Status
  8783,2209,"104,343,873.83","All good, but nowhere to go."
  2003,1024,"98,878,784.00",A-OK

That, however, called the external program for each column (quite
inefficient with large data sets)... so let's do that more
efficiently, with a "continuous" mode program. Given the following
``id2name.py`` program which takes a CSV on STDIN with a single column
(an employee ID) and writes a CSV to STDOUT with the IDs converted to
names:

.. code-block:: python

  #!/usr/bin/env python
  import sys, csvkit
  table = {'8783': 'ElfenKyng', '2003': 'Stradivarius'}
  # NOTE: *not* using csvkit's reader because it reads-ahead
  # causing problems since this must be stream-oriented...
  writer = csvkit.CSVKitWriter(sys.stdout)
  while True:
    item = sys.stdin.readline()
    if not item: break
    item = item.strip()
    writer.writerow([table[item] if item in table else item])
    sys.stdout.flush()

Then the following will efficiently convert the 'Employee ID' column
to names:

.. code-block:: bash

  $ cat sample.csv | csvsed -c 'Employee ID' 'e/id2name.py/c'
  Employee ID,Age,Wage,Status
  ElfenKyng,47,"104,343,873.83","All good, but nowhere to go."
  Stradivarius,32,"98,878,784.00",A-OK
