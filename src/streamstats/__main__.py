import argparse
import logging
import sys
from pathlib import Path

from .analysis import Stats, filter_level, filter_source, filter_time
from .errors import CLIConfigError, InvalidEventError, InvalidTimestampError, StreamStatsError
from .models import Level, parse_timestamp
from .parsers import SkipCounter, iter_events
from .report import build_report, write_report

EXTENSIONS = {".csv": "csv", ".jsonl": "jsonl"}

def build_parser():
    parser = argparse.ArgumentParser(
        prog="streamstats",
        description="Потоковый анализатор файлов событий",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="построить статистический отчёт",
    )
    analyze_parser.add_argument(
        "inputs",
        nargs="+",
        metavar="INPUT",
        help='входные файлы',
    )
    analyze_parser.add_argument(
        "--format",
        choices=["csv", "jsonl"],
        help="формат входных файлов (определяется по расширению)",
    )
    analyze_parser.add_argument(
        "--output",
        dest="outfile",
        metavar="REPORT.json",
        help="куда записать отчёт (по умолчанию stdout)",
    )
    analyze_parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="пропускать некорректные строки вместо остановки",
    )
    analyze_parser.add_argument(
        "--level", action="append", type=str.upper,
        choices=[level.value for level in Level],
        help="учитывать только события этого уровня (можно несколько раз)",
    )
    analyze_parser.add_argument(
        "--source", action="append",
        help="учитывать только события этого источника (можно несколько раз)",
    )
    analyze_parser.add_argument("--since", help="не раньше этой метки (ISO 8601)")
    analyze_parser.add_argument("--until", help="не позже этой метки (ISO 8601)")

    return parser


def parse_time_arg(value, option):
    if value is None:
        return None
    try:
        return parse_timestamp(value)
    except InvalidTimestampError as e:
        raise CLIConfigError(f"{option}: {e}") from e


def detect_format(path, explicit):
    if explicit is not None:
        return explicit
    fmt = EXTENSIONS.get(Path(path).suffix.lower())
    if fmt is None:
        raise CLIConfigError(
            f"{path}: не удалось определить формат по расширению, укажите --format"
        )
    return fmt


def run_analyze(args):
    since = parse_time_arg(args.since, "--since")
    until = parse_time_arg(args.until, "--until")
    total = Stats()
    for path in args.inputs:
        fmt = detect_format(path, args.format)
        skipped = SkipCounter()
        try:
            events = iter_events(path, fmt, args.skip_invalid, skipped)
            if args.level:
                events = filter_level(events, set(args.level))
            if args.source:
                events = filter_source(events, set(args.source))
            if since is not None or until is not None:
                events = filter_time(events, since, until)
            for event in events:
                total.add(event)
        except UnicodeDecodeError as exc:
            raise InvalidEventError(f"{path}: файл не в кодировке UTF-8 ({exc.reason})") from exc
        total.skipped += skipped.count

    write_report(build_report(total, args.inputs), args.outfile)


def main(argv: list[str]):
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    try:
        run_analyze(args)
    except StreamStatsError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"Ошибка файла: {e}", file=sys.stderr)
        sys.exit(2)
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
