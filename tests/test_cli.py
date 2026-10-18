import json

import pytest

from streamstats.__main__ import main

LINE = '{"timestamp": "2024-05-01T12:00:00Z", "level": "ERROR", "source": "бд", "message": "🔥"}\n'


def test_cli_ok(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text(LINE * 2, encoding="utf-8")
    out = tmp_path / "r.json"
    assert main(["analyze", str(p), "--output", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_events"] == 2
    assert data["top_error_sources"][0] == {"source": "бд", "count": 2}


def test_cli_multiple_files(tmp_path):
    csv_file = tmp_path / "a.csv"
    csv_file.write_text(
        "timestamp,level,source,message\n2024-05-01T12:00:00Z,ERROR,бд,x\n",
        encoding="utf-8",
    )
    jsonl_file = tmp_path / "b.jsonl"
    jsonl_file.write_text(LINE, encoding="utf-8")
    out = tmp_path / "r.json"

    assert main(["analyze", str(csv_file), str(jsonl_file), "--output", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_events"] == 2
    assert data["by_source"]["бд"] == 2
    assert data["top_error_sources"][0] == {"source": "бд", "count": 2}


def test_cli_invalid_strict(tmp_path, capsys):
    p = tmp_path / "a.jsonl"
    p.write_text(LINE + "мусор\n", encoding="utf-8")
    with pytest.raises(SystemExit) as info:
        main(["analyze", str(p)])
    assert info.value.code == 2
    assert "a.jsonl:2" in capsys.readouterr().err


def test_cli_invalid_skip(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text(LINE + "мусор\n", encoding="utf-8")
    out = tmp_path / "r.json"
    assert main(["analyze", str(p), "--skip-invalid", "--output", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["skipped_lines"] == 1


def test_cli_missing_file(tmp_path):
    with pytest.raises(SystemExit) as info:
        main(["analyze", str(tmp_path / "нет.csv")])
    assert info.value.code == 2


def test_cli_csv_report(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text(LINE * 2, encoding="utf-8")
    out = tmp_path / "r.csv"
    assert main(["analyze", str(p), "--output", str(out)]) == 0
    text = out.read_text(encoding="utf-8-sig")
    assert "summary,total_events,2" in text
    assert "top_error_sources,бд,2" in text
