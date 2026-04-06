import csv
import subprocess
import sys
from pathlib import Path
import builtins

from script import parse_args, read_files, write_csv

def test_parse_args_with_required(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["script", "--files", "a.csv", "b.csv", "--report", "out"])
    args = parse_args()
    assert args.files == ["a.csv", "b.csv"]
    assert args.report == "out"

def test_read_files_handles_generic_exception(tmp_path, monkeypatch, capsys):
    target = str(tmp_path / "bad.csv")
    orig_open = builtins.open

    def fake_open(path, *a, **k):
        if path == target:
            raise RuntimeError("boom")
        return orig_open(path, *a, **k)

    monkeypatch.setattr("builtins.open", fake_open)

    good = tmp_path / "good.csv"
    good.parent.mkdir(parents=True, exist_ok=True)
    with orig_open(good, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student", "coffee spent"])
        writer.writerow(["A", "1"])

    data = read_files([str(good), target])
    captured = capsys.readouterr()
    assert "Ошибка" in captured.err
    assert "A" in data

def test_main_prints_table_and_report(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.parent.mkdir(parents=True, exist_ok=True)
    with open(a, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student", "coffee spent"])
        writer.writerow(["X", "1"])
    with open(b, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student", "coffee spent"])
        writer.writerow(["X", "3"])
    report_base = tmp_path / "out-report"
    proc = subprocess.run([sys.executable, "-m", "script", "--files", str(a), str(b), "--report", str(report_base)],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Отчёт записан в" in proc.stdout
    assert "median_coffee_spent" in proc.stdout