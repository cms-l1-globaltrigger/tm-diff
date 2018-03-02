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

import argparse
import difflib
import logging
import sys, os

Newline = "\n"
ColorRed = "\033[31m"
ColorGreen = "\033[32m"
ColorClear = "\033[0m"

class Diffable(object):

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
        return "{}: {}".format(attr, getattr(self, attr))

    def to_diff(self):
        """Returns diff-able list of attributes for unified diff.
        >>> o.to_diff()
        ['foo: 42', 'bar: baz']
        """
        return [self.fmt_attr(attr) for attr in self.sorted_attributes]

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

    def __init__(self, filename):
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
            items.extend(algorithm.to_diff())
        # Cuts
        for cut in sorted(self.cuts, key=lambda cut: cut.name):
            items.append("") # separate by an empty line
            items.extend(cut.to_diff())
        return items

    def dump_intermediate(self, outdir=None):
        """Dumps intermediate text file used to perform the unified diff."""
        if not outdir:
            outdir = os.getcwd()
        filename = "{}.txt".format(os.path.basename(self.filename))
        with open(os.path.join(outdir, filename), 'wb') as fp:
            for line in self.to_diff():
                fp.write(line)
                fp.write(Newline)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs=2, help="XML menu files 'FILE1 FILE2'")
    parser.add_argument('-d', '--dump', action='store_true', help="dump the extracted intermediate menu content")
    return parser.parse_args()

def main():
    args = parse_args()

    # Read input files
    fromfile = Menu(args.file[0])
    tofile = Menu(args.file[1])

    # Prepare input string list
    fromlist = fromfile.to_diff()
    tolist = tofile.to_diff()

    if args.dump:
        fromfile.dump_intermediate()
        tofile.dump_intermediate()

    # Perform an unified diff
    for line in difflib.unified_diff(fromlist, tolist, fromfile=fromfile.filename, tofile=tofile.filename, lineterm=""):
        # Print added lines
        if line.startswith('+'):
            if sys.stdout.isatty():
                sys.stdout.write(ColorGreen)
            sys.stdout.write(Newline)
            sys.stdout.write(line)
            if sys.stdout.isatty():
                sys.stdout.write(ColorClear)
        # Print removed lines
        elif line.startswith('-'):
            if sys.stdout.isatty():
                sys.stdout.write(ColorRed)
            sys.stdout.write(Newline)
            sys.stdout.write(line)
            if sys.stdout.isatty():
                sys.stdout.write(ColorClear)
        # Print matching lines
        else:
            sys.stdout.write(Newline)
            if sys.stdout.isatty():
                sys.stdout.write(ColorClear)
            sys.stdout.write(line)
    sys.stdout.write(Newline)

    sys.exit()

if __name__ == '__main__':
    main()
