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

import datetime
import difflib
import logging
import sys, os

from . import __version__

class TTY:
    """TTY escape codes."""
    clear = "\033[0m"
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    magenta = "\033[35m"

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

    report_attributes = (
        'index',
        'name',
        'expression',
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
        self.skip = [] # list of attributes to skip
        self.sort = 'index' # sort key for algorithms

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
        # Collect list of algorithms and cuts
        self.algorithms = []
        cuts = {}
        for row in menu.algorithms:
            self.algorithms.append(Algorithm(**row))
            if row['name'] in menu.cuts.keys():
                for cut in menu.cuts[row['name']]:
                    cuts[cut['name']] = Cut(**cut)
        self.cuts = cuts.values()

    def sorted_algorithms(self):
        """Returns sorted list of algorithms."""
        def sort_key(algorithm):
            if self.sort == 'index':
                return int(algorithm.index)
            return getattr(algorithm, self.sort)
        return sorted(self.algorithms, key=sort_key)

    def sorted_cuts(self):
        """Returns sorted list of cuts."""
        return sorted(self.cuts, key=lambda cut: cut.name)

    def to_diff(self):
        """Returns list of attributes to be read by unified_diff."""
        items = []
        # Metadata
        items.extend(self.meta.to_diff(skip=self.skip))
        # Algorithms
        for algorithm in self.sorted_algorithms():
            items.append("") # separate by an empty line
            items.extend(algorithm.to_diff(skip=self.skip))
        # Cuts
        for cut in self.sorted_cuts():
            items.append("") # separate by an empty line
            items.extend(cut.to_diff(skip=self.skip))
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

def report_diff(fromfile, tofile, verbose=False, ostream=sys.stdout):
    """Perform simple diff on two menus in TWiki format for reports.
    >>> report_diff(fromfile, tofile)
    """
    fromlist = fromfile.to_diff()
    tolist = tofile.to_diff()

    from_algorithms = {}
    to_algorithms = {}

    for algorithm in fromfile.algorithms:
        from_algorithms[algorithm.name] = algorithm
    for algorithm in tofile.algorithms:
        to_algorithms[algorithm.name] = algorithm

    def added_algorithms(a, b):
        algorithms = []
        names = [algorithm.name for algorithm in b.algorithms]
        for algorithm in a.algorithms:
            if algorithm.name not in names:
                algorithms.append(algorithm)
        return algorithms

    added = added_algorithms(tofile, fromfile)
    removed = added_algorithms(fromfile, tofile)
    updated = []

    for name, fromalgorithm in from_algorithms.iteritems():
        if name in to_algorithms:
            toalgorithm = to_algorithms[name]
            differences = []
            for attr in toalgorithm.report_attributes:
                if getattr(fromalgorithm, attr) != getattr(toalgorithm, attr):
                    differences.append([attr, getattr(fromalgorithm, attr), getattr(toalgorithm, attr)])
            if differences:
                updated.append([toalgorithm, differences])

    if added or removed or updated:
        ostream.write("---++ Changes with respect to !{0}".format(fromfile.meta.name))
        ostream.write(os.linesep)

    if added:
        ostream.write("   * Added the following algorithms")
        ostream.write(os.linesep)
        for algorithm in added:
            ostream.write("      * {0}".format(algorithm.name))
            ostream.write(os.linesep)

    if updated:
        ostream.write("   * Changed the following algorithms")
        ostream.write(os.linesep)
        for algorithm, differnces in updated:
            ostream.write("      * {0}".format(algorithm.name))
            ostream.write(os.linesep)
            # Verbose changes
            if verbose:
                for attr, left, right in differnces:
                    ostream.write("          * {0}: {1} --> {2}".format(attr, left, right))
                    ostream.write(os.linesep)

    if removed:
        ostream.write("   * Removed the following algorithms")
        ostream.write(os.linesep)
        for algorithm in removed:
            ostream.write("      * {0}".format(algorithm.name))
            ostream.write(os.linesep)

def unified_diff(fromfile, tofile, verbose=False, ostream=sys.stdout):
    """Perform unified diff on two menus.
    >>> unified_diff(fromfile, tofile)
    """
    fromlines = fromfile.to_diff()
    tolines = tofile.to_diff()

    for line in difflib.unified_diff(fromlines, tolines, fromfile=fromfile.filename, tofile=tofile.filename, lineterm=""):
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
        # Print diff markers
        elif line.startswith('@@'):
            if ostream.isatty():
                ostream.write(TTY.yellow)
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

def context_diff(fromfile, tofile, verbose=False, ostream=sys.stdout):
    """Perform context diff on two menus.
    >>> context_diff(fromfile, tofile)
    """
    fromlines = fromfile.to_diff()
    tolines = tofile.to_diff()

    for line in difflib.context_diff(fromlines, tolines, fromfile=fromfile.filename, tofile=tofile.filename, lineterm=""):
        # Print added lines
        if line.startswith('+ '):
            if ostream.isatty():
                ostream.write(TTY.green)
            ostream.write(os.linesep)
            ostream.write(line)
            if ostream.isatty():
                ostream.write(TTY.clear)
        # Print removed lines
        elif line.startswith('- '):
            if ostream.isatty():
                ostream.write(TTY.red)
            ostream.write(os.linesep)
            ostream.write(line)
            if ostream.isatty():
                ostream.write(TTY.clear)
        # Print changed lines
        elif line.startswith('! '):
            if ostream.isatty():
                ostream.write(TTY.magenta)
            ostream.write(os.linesep)
            ostream.write(line)
            if ostream.isatty():
                ostream.write(TTY.clear)
        # Print diff markers
        elif line.startswith('---') or line.startswith('***'):
            if ostream.isatty():
                ostream.write(TTY.yellow)
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

def html_diff(fromfile, tofile, verbose=False, ostream=sys.stdout):
    """Perform diff on two menus and writes results to HTML table.
    >>> with open("sample.html", "w") as f:
    ...     html_diff(fromfile, tofile, f)
    """
    fromlines = fromfile.to_diff()
    tolines = tofile.to_diff()

    diff = difflib.HtmlDiff()
    html = diff.make_file(
        fromlines, tolines,
        os.path.basename(fromfile.filename),
        os.path.basename(tofile.filename),
    )

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # patching CSS style and adding a footer
    patches = [
        [
            """</style>""",
            """
            /* additional styles added by tm-diff */
            table:first-of-type {
              width: 100% !important;
            }
            td[nowrap] {
              max-width: 600px !important;
              word-wrap: normal !important;
              white-space: pre-wrap !important;
              word-break: break-all !important;
              padding-left: 1px;
            }
            .pull-left {
              float: left;
            }
            .pull-right {
              float: right;
            }
            .footer p {
              font-family: 'sans serif';
              float: right;
              font-size: .9em;
              color: darkgray;
            }
            </style>
            """
        ],
        [
            """</body>""",
            """
              <div class="footer">
               <p>Generated by tm-diff v{0} on {1}.</p>
              </div>
            </body>
            """.format(__version__, timestamp)
        ],
    ]

    for needle, patch in patches:
        html = html.replace(needle, patch, 1) # patch only first occurence

    ostream.write(html)
