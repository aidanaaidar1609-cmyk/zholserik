"""Расчёт цены и срока по таблице перевозчиков (без ИИ)."""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data"


def load(name):
    """Читает JSON-файл из папки data."""
    with open(DATA / name, encoding="utf-8") as f:
        return json.load(f)


def estimate(cargo_type, weight_kg):
    """Возвращает первую строку таблицы, где тип груза совпадает и вес не больше max_kg."""
    rows = [r for r in load("prices.json") if r["cargo_type"] == cargo_type]
    rows.sort(key=lambda r: r["max_kg"])  # от маленького веса к большому
    for row in rows:
        if weight_kg <= row["max_kg"]:
            return row
    return None  # для такого веса данных пока нет


def documents(cargo_type):
    """Список документов для типа груза (если типа нет — берём «другое»)."""
    docs = load("documents.json")
    return docs.get(cargo_type, docs.get("другое", []))
