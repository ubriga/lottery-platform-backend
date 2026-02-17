from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_ndjson(path: Path, items: Iterable[dict]) -> int:
    ensure_dir(path.parent)
    n = 0
    with path.open('a', encoding='utf-8') as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            n += 1
    return n


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
