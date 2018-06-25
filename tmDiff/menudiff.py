#!/usr/bin/env python
#
# Diff for XML menus
#
# The algorithm specific content is extracted into a simple text representation
# and a unified diff is applied to make differences visible.
#
# Diff format, blocks are separated by empty lines:
#
# ----
# index: <index>
# module_id: <module_id>
# module_index: <module_index>
# name: <name>
# expression: <expression>
# comment: <comment>
# ----
#
# The printed line information refers to the extracted content (can be dumped
# with flag -d
#


import tmTable

import difflib
import logging
import sys, os

class TTY:
    """TTY escape codes."""
    clear = "\033[0m"
    red = "\033[31m"
    green = "\033[32m"

class Diffable(object):
    """Implements a diffabel object. To be inherited by classes defining class
    attribute `sorted_attribuites`.
    """

    sorted_attributes = tuple()

    default_value = ''

    def __init__(self, **kwargs):
        for attr in self.sorted_attributes:
            setattr(self, attr, kwargs[attr] if attr in kwargs else self.default_value)

    def fmt_attr(self, attr):
        """Format attribute used for unified diff.
        >>> o.fmt_attr('foobar')
        'foobar: 42'
        """
        return "{0}: {1}".format(attr, getattr(self, attr))

    def to_diff(self, skip=[]):
        """Returns diff-able list of attributes for unified diff.
        >>> o.to_diff()
        ['foo: 42', 'bar: baz']
        >>> o.to_diff(skip=['bar']) # skip attributes
        ['foo: 42']
        """
        return [self.fmt_attr(attr) for attr in self.sorted_attributes if attr not in skip]

class Meta(Diffable):
    """Simple menu metadata container.
    >>> meta = Meta(**row)
    """

    sorted_attributes = (
        'name',
        'uuid_menu',
        'uuid_firmware',
        'n_modules',
        'grammar_version',
        'is_valid',
        'is_obsolete',
        'comment',
    )

class Algorithm(Diffable):
    """Simple algorithm container.
    >>> algorithm = Algorithm(**row)
    """

    sorted_attributes = (
        'index',
        'module_id',
        'module_index',
        'name',
        'expression',
        'comment',
    )

    impl_attributes = (
        'module_id',
        'module_index',
    )

class Cut(Diffable):

    sorted_attributes = (
        'name',
        'type',
        'object',
        'minimum',
        'maximum',
        'data',
        'comment',
    )

class Menu(object):
    """Simple menu container."""

    def __init__(self, filename, skipimpl=False):
        self.skipimpl = skipimpl
        self.load(filename)

    def load(self, filename):
        """Load menu from XML file."""
        self.filename = filename
        menu = tmTable.Menu()
        scale = tmTable.Scale()
        ext_signal = tmTable.ExtSignal()
        message = tmTable.xml2menu(filename, menu, scale, ext_signal)
        if message:
            raise RuntimeError(message)
        # Collect list of metadata
        self.meta = Meta(**menu.menu)
        # Collect list of algorithms
        self.algorithms = []
        cuts = {}
        for row in menu.algorithms:
            self.algorithms.append(Algorithm(**row))
            if row['name'] in menu.cuts.keys():
                for cut in menu.cuts[row['name']]:
                    cuts[cut['name']] = Cut(**cut)
        self.cuts = cuts.values()

    def to_diff(self):
        """Returns list of attributes to be read by unified_diff."""
        items = []
        # Metadata
        items.extend(self.meta.to_diff())
        # Algorithms
        for algorithm in sorted(self.algorithms, key=lambda algorithm: algorithm.name):
            items.append("") # separate by an empty line
            # Skip implemetation attributes on demand.
            skip = Algorithm.impl_attributes if self.skipimpl else []
            items.extend(algorithm.to_diff(skip=skip))
        # Cuts
        for cut in sorted(self.cuts, key=lambda cut: cut.name):
            items.append("") # separate by an empty line
            items.extend(cut.to_diff())
        return items

    def dump_intermediate(self, outdir=None):
        """Dumps intermediate text file used to perform the unified diff."""
        if not outdir:
            outdir = os.getcwd()
        filename = "{0}.txt".format(os.path.basename(self.filename))
        with open(os.path.join(outdir, filename), 'wb') as fp:
            for line in self.to_diff():
                fp.write(line)
                fp.write(os.linesep)

def unified_diff(fromfile, tofile, dump=False, skipimpl=False, ostream=sys.stdout):
    """Perform unified diff onn two XML menus.
    >>> unified_diff("foo.xml", "bar.xml")
    """

    frommenu = Menu(fromfile, skipimpl)
    tomenu = Menu(tofile, skipimpl)

    fromlist = frommenu.to_diff()
    tolist = tomenu.to_diff()

    if dump:
        frommenu.dump_intermediate()
        tomenu.dump_intermediate()

    for line in difflib.unified_diff(fromlist, tolist, fromfile=fromfile, tofile=tofile, lineterm=""):
        # Print added lines
        if line.startswith('+'):
            if ostream.isatty():
                ostream.write(TTY.green)
            ostream.write(os.linesep)
            ostream.write(line)
            if ostream.isatty():
                ostream.write(TTY.clear)
        # Print removed lines
        elif line.startswith('-'):
            if ostream.isatty():
                ostream.write(TTY.red)
            ostream.write(os.linesep)
            ostream.write(line)
            if ostream.isatty():
                ostream.write(TTY.clear)
        # Print matching lines
        else:
            ostream.write(os.linesep)
            if ostream.isatty():
                ostream.write(TTY.clear)
            ostream.write(line)
    ostream.write(os.linesep)
