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


def write_report(report, path=None):
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if path is None:
        print(text)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + "\n")