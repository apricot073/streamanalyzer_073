import csv
import json

from .models import Level


def build_report(stats, files):
    return {
        "files": list(files),
        "total_events": stats.total,
        "by_level": {level.value: stats.by_level[level] for level in Level},
        "by_source": dict(stats.by_source),
        "top_error_sources": [
            {"source": source, "count": count}
            for source, count in stats.top_error_sources(5)
        ],
        "first_timestamp": stats.first_ts.isoformat() if stats.first_ts else None,
        "last_timestamp": stats.last_ts.isoformat() if stats.last_ts else None,
        "skipped_lines": stats.skipped,
    }


def write_csv_report(report, path):
    """Записать тот же словарь отчёта в CSV: section,key,value."""
    rows = [("section", "key", "value")]
    rows.append(("summary", "total_events", report["total_events"]))
    rows.append(("summary", "first_timestamp", report["first_timestamp"]))
    rows.append(("summary", "last_timestamp", report["last_timestamp"]))
    rows.append(("summary", "skipped_lines", report["skipped_lines"]))
    for level, count in report["by_level"].items():
        rows.append(("by_level", level, count))
    for source, count in report["by_source"].items():
        rows.append(("by_source", source, count))
    for item in report["top_error_sources"]:
        rows.append(("top_error_sources", item["source"], item["count"]))
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(rows)


def write_report(report, path=None):
    if path is not None and str(path).lower().endswith(".csv"):
        write_csv_report(report, path)
        return
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if path is None:
        print(text)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
