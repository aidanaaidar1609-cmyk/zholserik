"""Хранение заявок для перевозчика (в демо — простой JSON-файл)."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

FILE = Path(__file__).parent / "data" / "requests.json"
ALMATY = timezone(timedelta(hours=5))  # время Казахстана (UTC+5)


def load_requests():
    if not FILE.exists():
        return []
    return json.loads(FILE.read_text(encoding="utf-8"))


def save_request(item):
    items = load_requests()
    item["time"] = datetime.now(ALMATY).strftime("%d.%m %H:%M")
    items.append(item)
    FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
