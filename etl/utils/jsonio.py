from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')


def parse_date_iso(date_s: str | None) -> datetime | None:
    if not date_s:
        return None
    return datetime.fromisoformat(date_s)
