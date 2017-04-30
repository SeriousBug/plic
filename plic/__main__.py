#!/usr/bin/env python3
"""Program entry point"""

import argparse
import sys
from os.path import basename
import logging
import pickle
import zlib

from scipy import misc
from plic import __metadata__ as metadata, colorspace, compression


def _make_parser(prog_name):
    author_strings = ['Author: {0} <{1}>'.format(name, email) for name, email in zip(metadata.authors, metadata.emails)]
    epilog = '''
{project} {version}

{authors}
'''.format(project=metadata.project,
           version=metadata.version,
           authors='\n'.join(author_strings))

    parser = argparse.ArgumentParser(
        prog=prog_name,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=epilog
    )
    parser.add_argument(
        '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version),
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        "-o", "--output",
        type=argparse.FileType('wb'),
        help="The name of the output file.",
    )
    parser.add_argument(
        "-t", "--interpratio",
        type=int,
        default=3,
        help="Interpolation ratio.",
    )
    operation_mode = parser.add_mutually_exclusive_group(required=False)
    operation_mode.add_argument(
        "-c", "--compress", action='store_true',
        help="The input file should be decompressed.,"
    )
    operation_mode.add_argument(
        "-d", "--decompress", action='store_true',
        help="The input file should be compressed.",
    )
    parser.add_argument(
        "input",
        help="The input file to be processed. If both compress and decompress "
        "options are omitted, the operation will be automatically decided based"
        "on the extension of input file.",
        type=argparse.FileType('rb')
    )
    return parser


def _setup_logger(level):
    """Sets up the root logger.

    DEBUG and INFO level messages will be logged to stdout. WARNING,
    ERROR and CRITICAL level messages will be logged to stderr.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    form = logging.Formatter("%(asctime)s %(levelname)s %(name)s.%(funcName)s:%(lineno)s - %(message)s")
    msg_handler = logging.StreamHandler(stream=sys.stdout)
    msg_handler.setLevel(logging.DEBUG)
    msg_handler.setFormatter(form)
    msg_handler.addFilter(lambda r: r.levelno < logging.WARNING)
    err_handler = logging.StreamHandler(stream=sys.stderr)
    err_handler.setLevel(logging.WARNING)
    err_handler.setFormatter(form)
    logger.addHandler(msg_handler)
    logger.addHandler(err_handler)


def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`

    :raises SystemExit: Raised to exit the program if there were no errors.
    """
    parser = _make_parser(prog_name=basename(argv[0]))
    args = parser.parse_args(argv[1:])
    _setup_logger(logging.INFO if args.verbose else logging.WARNING)
    if args.compress:
        image = misc.imread(args.input)
        transformed = colorspace.rgb2rdgdb(image)
        compressed = compression.compress(transformed, t=args.interpratio)
        encoded = zlib.compress(pickle.dumps(compressed))
        args.output.write(encoded)
    elif args.decompress:
        decoded = pickle.loads(zlib.decompress(args.input.read()))
        decompressed = compression.decompress(decoded)
        detransformed = colorspace.rdgdb2rgb(decompressed)
        misc.imsave(args.output, detransformed)
    raise SystemExit(0)


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    main(sys.argv)


if __name__ == '__main__':
    entry_point()
