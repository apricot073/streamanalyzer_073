import csv
import json
import logging

from .errors import InvalidEventError, UnsupportedFormatError
from .models import parse_event

logger = logging.getLogger(__name__)


class SkipCounter:
    """Счётчик пропущенных строк (--skip-invalid)."""

    def __init__(self) -> None:
        self.count = 0

def _read_csv(path):
    """Обработать CSV."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        try:
            header = reader.fieldnames
            if header is None:
                return
            missing = [name for name in ("timestamp", "level", "source", "message") if name not in header]
            if missing:
                raise InvalidEventError(
                    f"в заголовке CSV нет колонок: {', '.join(missing)}",
                    path=str(path),
                    line_no=1,
                )
            for row in reader:
                yield reader.line_num, row
        except csv.Error as exc:
            raise InvalidEventError(
                f"ошибка CSV: {exc}", path=str(path), line_no=reader.line_num
            ) from exc


def _read_jsonl(path):
    """Обработать JSONL."""
    with open(path, encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                yield line_no, line


def _csv_to_dict(row: dict) -> dict:
    """Валидировать CSV."""
    if None in row:
        raise InvalidEventError("в строке больше значений, чем колонок в заголовке")
    return row


def _jsonl_to_dict(line: str) -> dict:
    """Валидировать JSONL."""
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as exc:
        raise InvalidEventError(f"некорректный JSON: {exc.msg}") from exc
    if not isinstance(obj, dict):
        raise InvalidEventError("строка JSONL должна быть JSON-объектом")
    return obj


FORMATS = {
    "csv": (_read_csv, _csv_to_dict),
    "jsonl": (_read_jsonl, _jsonl_to_dict),
}


def iter_events(path: str, fmt: str, skip_invalid: bool = False, skipped: SkipCounter | None = None):
    """Лениво прочитать событие из файла."""
    if fmt not in FORMATS:
        raise UnsupportedFormatError(f"неподдерживаемый формат: {fmt!r}")
    reader, to_mapping = FORMATS[fmt]
    path = str(path)

    for line_no, raw in reader(path):
        try:
            event = parse_event(to_mapping(raw))
        except InvalidEventError as exc:
            exc.path = path
            exc.line_no = line_no
            if skip_invalid:
                logger.warning("пропущена строка: %s", exc)
                if skipped is not None:
                    skipped.count += 1
                continue
            raise
        yield event
