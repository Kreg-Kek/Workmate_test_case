import csv
import subprocess
import sys
from pathlib import Path

from script import read_files, build_report, write_csv

def create_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def test_read_files_file_not_found(tmp_path, capsys):
    data = read_files([str(tmp_path / "no_such.csv")])
    captured = capsys.readouterr()
    assert "Файл не найден" in captured.err
    assert data == {}

def test_read_files_invalid_headers_skipped(tmp_path, capsys):
    f = tmp_path / "bad.csv"
    create_csv(f, ["wrong", "cols"], [["a", "1"]])
    data = read_files([str(f)])
    captured = capsys.readouterr()
    assert "скипаем" in captured.err or "Кривая" in captured.err
    assert data == {}

def test_read_files_alternate_headers_and_bad_numbers(tmp_path):
    f = tmp_path / "alt.csv"
    create_csv(f, ["Name", "coffee_spent"], [
        ["Alice", "1,5"],
        ["Bob", "bad"],
        ["Alice", "2.5"],
        ["", "3"],
    ])
    data = read_files([str(f)])
    assert set(data.keys()) == {"Alice"}
    assert sorted(data["Alice"]) == [1.5, 2.5]

def test_build_report_ignores_empty_lists():
    data = {"A": [], "B": [1.0]}
    rows = build_report(data)
    assert rows == [("B", 1.0)]

def test_write_csv_returns_path_and_format(tmp_path):
    rows = [("A", 2), ("B", 3.456)]
    outbase = tmp_path / "r"
    path = write_csv(rows, str(outbase))
    assert path == str(outbase) + ".csv"
    with open(path, encoding="utf-8") as f:
        reader = list(csv.reader(f))
    assert reader[0] == ["student", "median_coffee_spent"]
    assert reader[1][1] == "2.00"
    assert reader[2][1] == "3.46"

def test_main_exits_with_nonzero_on_empty_report(tmp_path):
    f = tmp_path / "only_header.csv"
    create_csv(f, ["student", "coffee spent"], [])
    report_base = tmp_path / "out"
    proc = subprocess.run([sys.executable, "-m", "script", "--files", str(f), "--report", str(report_base)],
                          capture_output=True, text=True)
    assert proc.returncode == 1
    assert "Пусто" in proc.stderr
