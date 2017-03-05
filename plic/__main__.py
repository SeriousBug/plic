#!/usr/bin/env python3
"""Program entry point"""

from __future__ import print_function

import argparse
import sys
from os.path import basename
import pickle
import zlib

from scipy import misc
from plic import __metadata__ as metadata, colorspace, compression


def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    author_strings = []
    for name, email in zip(metadata.authors, metadata.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    epilog = '''
{project} {version}

{authors}
'''.format(project=metadata.project,
           version=metadata.version,
           authors='\n'.join(author_strings),
           url=metadata.url)

    parser = argparse.ArgumentParser(prog=basename(argv[0]),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=metadata.description,
                                     epilog=epilog)
    parser.add_argument('--version',
                        action='version',
                        version='{0} {1}'.format(metadata.project, metadata.version))

    parser.add_argument("-o", "--output",
                        type=str,
                        help="The name of the output file.")
    operation_mode = parser.add_mutually_exclusive_group(required=False)
    operation_mode.add_argument("-c", "--compress", action='store_true',
                                help="The input file should be decompressed.")
    operation_mode.add_argument("-d", "--decompress", action='store_true',
                                help="The input file should be compressed.")
    parser.add_argument("input",
                        help="The input file to be processed. If both compress and decompress options "
                        "are omitted, the operation will be automatically decided based on the extension of "
                        "input file.")
    args = parser.parse_args(argv[1:])
    if args.compress:
        image = misc.imread(args.input)
        transformed = colorspace.rgb2rdgdb(image)
        compressed = compression.compress(transformed)
        encoded = zlib.compress(pickle.dumps(compressed))
        with open(args.output, 'wb') as f:
            f.write(encoded)
    elif args.decompress:
        with open(args.input, 'rb') as f:
            decoded = pickle.loads(zlib.decompress(f.read()))
        decompressed = compression.decompress(decoded)
        detransformed = colorspace.rdgdb2rgb(decompressed)
        misc.imsave(args.output, detransformed)
    raise SystemExit(0)


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    main(sys.argv)


if __name__ == '__main__':
    entry_point()
