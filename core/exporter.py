import json
import csv
from pathlib import Path


def export_json(data, path="output.json"):
    Path(path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def export_txt(text, path="output.txt"):
    Path(path).write_text(text, encoding="utf-8")


def export_markdown(title, content, path="output.md"):
    md = f"# {title}\n\n{content}"
    Path(path).write_text(md, encoding="utf-8")


def export_tables_csv(tables, base="tables"):
    for i, table in enumerate(tables, start=1):
        path = f"{base}_{i}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if table.get("headers"):
                writer.writerow(table["headers"])
            writer.writerows(table["rows"])
