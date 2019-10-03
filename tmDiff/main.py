import argparse
import sys, os

from . import menudiff
from . import __version__

FMT_UNIFIED = 'unified'
FMT_CONTEXT = 'context'
FMT_HTML = 'html'
FMT_REPORT = 'report'
FMT_DEFAULT = FMT_UNIFIED
FMT_CHOICES = [FMT_UNIFIED, FMT_CONTEXT, FMT_HTML, FMT_REPORT]

SKIP_MODULE = 'module'
SKIP_COMMENT = 'comment'
SKIP_CHOICES = [SKIP_MODULE, SKIP_COMMENT]

SORT_INDEX = 'index'
SORT_NAME = 'name'
SORT_EXPRESSION = 'expression'
SORT_DEFAULT = SORT_INDEX
SORT_CHOICES = [SORT_INDEX, SORT_NAME, SORT_EXPRESSION]

DIFF_FUNCTIONS = {
    FMT_UNIFIED: menudiff.unified_diff,
    FMT_CONTEXT: menudiff.context_diff,
    FMT_HTML: menudiff.html_diff,
    FMT_REPORT: menudiff.report_diff,
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
        nargs=2,
        help="XML menu files 'FILE1 FILE2'"
    )
    parser.add_argument('-f', '--format',
        metavar='<format>',
        choices=FMT_CHOICES,
        default=FMT_DEFAULT,
        help="select output format, default is '{0}'".format(FMT_DEFAULT)
    )
    parser.add_argument('-s', '--skip',
        metavar='<mode>',
        action='append',
        choices=SKIP_CHOICES,
        default=[],
        help="skip information"
    )
    parser.add_argument('--sort',
        metavar='<key>',
        choices=SORT_CHOICES,
        default=SORT_DEFAULT,
        help="select key for algorithm sorting, default is '{0}'".format(SORT_DEFAULT)
    )
    parser.add_argument('-d', '--dump',
    action='store_true',
    help="dump the extracted intermediate content"
    )
    parser.add_argument('-o',
        dest='ostream',
        metavar='<file>',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="write output to file"
    )
    parser.add_argument('-v', '--verbose',
        action='count',
        help="increase output verbosity"
    )
    parser.add_argument('--version',
        action='version',
        version="%(prog)s {0}".format(__version__)
    )
    return parser.parse_args()

def main():
    args = parse_args()

    from_file = args.file[0]
    to_file = args.file[1]

    skip = []

    # Skip module specific attributes
    if SKIP_MODULE in args.skip:
        skip.append('uuid_firmware')
        skip.append('n_modules')
        skip.append('module_id')
        skip.append('module_index')

    # Skip comments
    if SKIP_COMMENT in args.skip:
        skip.append('comment')

    # Extract information from XMLs
    from_menu = menudiff.Menu(from_file)
    from_menu.skip = skip
    from_menu.sort = args.sort
    to_menu = menudiff.Menu(to_file)
    to_menu.skip = skip
    to_menu.sort = args.sort

    # Dump extracted information on demand
    if args.dump:
        from_menu.dump_intermediate()
        to_menu.dump_intermediate()

    # Execute diff function
    DIFF_FUNCTIONS[args.format](
        fromfile=from_menu,
        tofile=to_menu,
        verbose=args.verbose,
        ostream=args.ostream
    )

    return 0

if __name__ == '__main__':
    sys.exit(main())
