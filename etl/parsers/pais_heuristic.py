from __future__ import annotations

import re
from dataclasses import asdict
from datetime import datetime
from typing import Iterable, List, Optional

from bs4 import BeautifulSoup

from etl.connectors.base_connector import DrawResult

DATE_RE = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})")


def _extract_ints(text: str) -> List[int]:
    return [int(x) for x in re.findall(r"\d+", text)]


def parse_pais_archive_html(
    html: str,
    *,
    game_id: str,
    source_url: str,
    numbers_count: int,
    bonus_count: int,
    min_num: int,
    max_num: int,
) -> List[DrawResult]:
    """Heuristic parser for Pais archive pages.

    It searches all table rows, looks for a DD/MM/YYYY date, and then extracts numbers
    in the allowed range. This is resilient to minor HTML changes.
    """

    soup = BeautifulSoup(html, 'html.parser')
    draws: List[DrawResult] = []

    for tr in soup.find_all('tr'):
        row_text = " ".join(tr.stripped_strings)
        m = DATE_RE.search(row_text)
        if not m:
            continue

        date_text = m.group(1)
        try:
            draw_date = datetime.strptime(date_text, '%d/%m/%Y')
        except ValueError:
            continue

        # Remove date portion before extracting ints, so day/month/year don't pollute.
        text_wo_date = row_text.replace(date_text, " ")
        ints = _extract_ints(text_wo_date)

        # Candidates in legal range are likely the draw numbers.
        candidates = [x for x in ints if min_num <= x <= max_num]
        needed = numbers_count + bonus_count
        if len(candidates) < needed:
            continue

        selected = candidates[-needed:]
        numbers = sorted(selected[:numbers_count])
        bonus: Optional[List[int]] = None
        if bonus_count:
            bonus = selected[numbers_count:numbers_count + bonus_count]

        # draw id: try to find an int that is NOT in number range (often the draw number)
        draw_id = None
        for x in ints:
            if x < min_num or x > max_num:
                # avoid picking odds like 2026 etc (already removed date, but just in case)
                if 1 <= x <= 999999:
                    draw_id = str(x)
                    break
        if not draw_id:
            # deterministic fallback: date + numbers
            draw_id = f"{draw_date.date().isoformat()}-" + "-".join(map(str, selected))

        draw = DrawResult(
            game_id=game_id,
            draw_id=draw_id,
            draw_date=draw_date,
            numbers=numbers,
            bonus_numbers=bonus,
            metadata={"parser": "heuristic_v1"},
            source_url=source_url,
            checksum="",
        )
        # checksum will be set by caller connector base; but we can mimic
        # caller will call BaseConnector.calculate_checksum
        draws.append(draw)

    return draws
