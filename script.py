import argparse
import csv
import sys
from collections import defaultdict
from statistics import median
from tabulate import tabulate

def parse_args():
    p = argparse.ArgumentParser(description="медианная сумма трат на кофе по каждому студенту")
    p.add_argument("--files", nargs="+", required=True, help="Имена .csv файлов")
    p.add_argument("--report", required=True, help="median-coffee по ТЗ")
    return p.parse_args()

def read_files(file_paths, student_col="student", coffee_col="coffee spent"):
    data = defaultdict(list)
    for path in file_paths:
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = {h.lower(): h for h in reader.fieldnames or []}
                if student_col not in headers or coffee_col not in headers:
                    lc = {h.lower(): h for h in (reader.fieldnames or [])}
                    s_key = lc.get(student_col)
                    c_key = lc.get(coffee_col)
                else:
                    s_key = headers[student_col]
                    c_key = headers[coffee_col]

                if not s_key or not c_key:
                    alt_student = lc.get("name") or lc.get("student_name") or lc.get("student")
                    alt_coffee = lc.get("coffee_spent") or lc.get("coffee") or lc.get("coffee spent")
                    s_key = s_key or alt_student
                    c_key = c_key or alt_coffee

                if not s_key or not c_key:
                    print(f"Кривая строка в файле {path} скипаем.", file=sys.stderr)
                    continue

                for row in reader:
                    student = (row.get(s_key) or "").strip()
                    raw = (row.get(c_key) or "").strip()
                    if not student or raw == "":
                        continue
                    try:
                        value = float(raw)
                    except ValueError:
                        try:
                            value = float(raw.replace(",", "."))
                        except ValueError:
                            continue
                    data[student].append(value)
        except FileNotFoundError:
            print(f"Файл не найден: {path}", file=sys.stderr)
        except Exception as e:
            print(f"Ошибка: {path}: {e}", file=sys.stderr)
    return data

def build_report(data):
    rows = []
    for student, spends in data.items():
        if not spends:
            continue
        med = median(spends)
        rows.append((student, med))
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows

def write_csv(report_rows, outname):
    out_file = f"{outname}.csv"
    with open(out_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["student", "median_coffee_spent"])
        for student, med in report_rows:
            writer.writerow([student, f"{med:.2f}"])
    return out_file

def main():
    args = parse_args()
    data = read_files(args.files)
    report_rows = build_report(data)
    if not report_rows:
        print("Пусто", file=sys.stderr)
        sys.exit(1)
    out_file = write_csv(report_rows, args.report)
    table = [[i+1, s, f"{m:.2f}"] for i, (s, m) in enumerate(report_rows)]
    print(tabulate(table, headers=["#", "student", "median_coffee_spent"], tablefmt="github"))
    print(f"\nОтчёт записан в {out_file}")

if __name__ == "__main__":
    main()
