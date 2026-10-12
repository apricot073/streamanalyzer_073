from __future__ import annotations

import argparse
import sys

from streamstats.errors import StreamStatsError

def build_parser():
    parser = argparse.ArgumentParser(
        prog="streamstats",
        description="Console utility: stream analyzer",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="TBA",
        description="TBA",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    analyze_parser.add_argument(
        "INPUT",
        help='TBA',
    )

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert a value between units",
        description="Groups: length (mm, cm, m, km), mass (g, kg), temperature (c, f, k).",
    )
    convert_parser.add_argument(
        "--format",
        dest="format",
        required=True,
        help="TBA",
    )
    convert_parser.add_argument(
        "--output",
        dest="outfile",
        required=True,
        help="TBA",
    )

    return parser


def main(argv: list[str]):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            pass
    except StreamStatsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
