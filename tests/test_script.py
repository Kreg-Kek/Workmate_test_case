import csv
import subprocess
import sys
from pathlib import Path

import pytest

from script import read_files, build_report, write_csv

def create_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def test_read_files_aggregates_and_parses_numbers(tmp_path):
    f = tmp_path / "a.csv"
    create_csv(f, ["student", "coffee spent"], [
        ["Анна Соколова", "1.50"],
        ["Илья Муромец", "2"],
        ["Анна Соколова", "2.5"],
        ["Илья Муромец", "3,25"],  
        ["", "1.0"],     
        ["Иван Иваныч", ""], 
    ])
    data = read_files([str(f)])
    assert set(data.keys()) == {"Анна Соколова", "Илья Муромец"}
    assert pytest.approx(sorted(data["Анна Соколова"])) == [1.5, 2.5]
    assert pytest.approx(sorted(data["Илья Муромец"])) == [2.0, 3.25]

def test_build_report_median_and_sorting():
    data = {
        "Анна Соколова": [1.0, 3.0, 5.0],   
        "Илья Муромец": [10.0],              
        "Иван Иваныч": [2.0, 4.0],      
    }
    rows = build_report(data)
    assert rows[0][0] == "Илья Муромец" and rows[0][1] == 10.0
    medians = {name: med for name, med in rows}
    assert medians["Анна Соколова"] == 3.0 and medians["Иван Иваныч"] == 3.0

def test_write_csv_and_contents(tmp_path):
    rows = [("Илья Муромец", 10.0), ("Анна Соколова", 3.0)]
    outname = tmp_path / "median-report"
    out_file = write_csv(rows, str(outname))
    expected_path = str(outname) + ".csv"
    assert out_file == expected_path
    with open(expected_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["student", "median_coffee_spent"]
        lines = list(reader)
        assert lines == [["Илья Муромец", "10.00"], ["Анна Соколова", "3.00"]]

def test_cli_end_to_end(tmp_path, monkeypatch):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    create_csv(a, ["student", "coffee spent"], [["X", "1"], ["Y", "2"]])
    create_csv(b, ["student", "coffee spent"], [["X", "3"], ["Y", "4"]])
    report_base = tmp_path / "out-report"
    proc = subprocess.run([sys.executable, "-m", "script", "--files", str(a), str(b), "--report", str(report_base)],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    out_csv = str(report_base) + ".csv"
    assert Path(out_csv).exists()
    with open(out_csv, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    data = {r[0]: r[1] for r in rows[1:]}
    assert data["X"] == "2.00"
    assert data["Y"] == "3.00"
