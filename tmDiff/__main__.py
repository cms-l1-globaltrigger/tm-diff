import argparse
import os
import sys
from typing import Callable, Dict, List

from . import menudiff
from . import __version__

FMT_UNIFIED: str = "unified"
FMT_CONTEXT: str = "context"
FMT_HTML: str = "html"
FMT_REPORT: str = "report"
FMT_DEFAULT: str = FMT_UNIFIED
FMT_CHOICES: List[str] = [FMT_UNIFIED, FMT_CONTEXT, FMT_HTML, FMT_REPORT]

SKIP_MODULE: str = "module"
SKIP_COMMENT: str = "comment"
SKIP_LABELS: str = "labels"
SKIP_CHOICES: List[str] = [SKIP_MODULE, SKIP_COMMENT, SKIP_LABELS]

SORT_INDEX: str = "index"
SORT_NAME: str = "name"
SORT_EXPRESSION: str = "expression"
SORT_DEFAULT: str = SORT_INDEX
SORT_CHOICES: List[str] = [SORT_INDEX, SORT_NAME, SORT_EXPRESSION]

DIFF_FUNCTIONS: Dict[str, Callable] = {
    FMT_UNIFIED: menudiff.unified_diff,
    FMT_CONTEXT: menudiff.context_diff,
    FMT_HTML: menudiff.html_diff,
    FMT_REPORT: menudiff.report_diff,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file",
        nargs=2,
        help="XML menu files 'FILE1 FILE2'"
    )
    parser.add_argument("-f", "--format",
        metavar="<format>",
        choices=FMT_CHOICES,
        default=FMT_DEFAULT,
        help=f"select output format, default is '{FMT_DEFAULT}'"
    )
    parser.add_argument("-s", "--skip",
        metavar="<mode>",
        action="append",
        choices=SKIP_CHOICES,
        default=[],
        help="skip information"
    )
    parser.add_argument("--sort",
        metavar="<key>",
        choices=SORT_CHOICES,
        default=SORT_DEFAULT,
        help=f"select key for algorithm sorting, default is '{SORT_DEFAULT}'"
    )
    parser.add_argument("-d", "--dump",
        action="store_true",
        help="dump the extracted intermediate content"
    )
    parser.add_argument("-o",
        dest="ostream",
        metavar="<file>",
        type=argparse.FileType("wt"),
        default=sys.stdout,
        help="write output to file"
    )
    parser.add_argument("-v", "--verbose",
        action="count",
        help="increase output verbosity"
    )
    parser.add_argument("--version",
        action="version",
        version="%(prog)s {0}".format(__version__)
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    from_file: str = args.file[0]
    to_file: str = args.file[1]

    skip: List[str] = []

    # Skip module specific attributes
    if SKIP_MODULE in args.skip:
        skip.append("uuid_firmware")
        skip.append("n_modules")
        skip.append("module_id")
        skip.append("module_index")

    # Skip comments
    if SKIP_COMMENT in args.skip:
        skip.append("comment")

    # Skip comments
    if SKIP_LABELS in args.skip:
        skip.append("labels")

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


if __name__ == "__main__":
    sys.exit(main())
