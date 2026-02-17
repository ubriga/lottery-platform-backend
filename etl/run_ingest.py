from __future__ import annotations

import argparse
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

from etl.connectors.base_connector import BaseConnector, DrawResult
from etl.connectors.pais_lotto import PaisLottoConnector
from etl.connectors.pais_chance import PaisChanceConnector
from etl.parsers.pais_heuristic import parse_pais_archive_html
from etl.utils.jsonio import dump_json, load_json
from etl.utils.ndjson import utc_now_iso, write_ndjson


LOGGER = logging.getLogger("etl.run_ingest")


GAMES: Dict[str, dict] = {
    "pais_lotto": {
        "connector": PaisLottoConnector,
        "source_url": PaisLottoConnector.OFFICIAL_URL,
        "numbers_count": 6,
        "bonus_count": 1,
        "min_num": 1,
        "max_num": 37,
        "data_subdir": "datasets/pais/lotto/ndjson",
    },
    "pais_chance": {
        "connector": PaisChanceConnector,
        "source_url": PaisChanceConnector.OFFICIAL_URL,
        "numbers_count": 6,
        "bonus_count": 1,
        "min_num": 1,
        "max_num": 37,
        "data_subdir": "datasets/pais/chance/ndjson",
    },
}


def _configure_logging(log_path: Path | None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logging.getLogger().addHandler(fh)


def _year_file(base: Path, d: datetime) -> Path:
    return base / f"{d.year}.ndjson"


def _load_existing_ids(year_path: Path) -> set[str]:
    if not year_path.exists():
        return set()
    ids = set()
    # For safety, read all for now; can be optimized later.
    for line in year_path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            # minimal parse to avoid json module overhead is possible later
            import json

            obj = json.loads(line)
            if "draw_id" in obj:
                ids.add(str(obj["draw_id"]))
        except Exception:
            continue
    return ids


def ingest_game(data_repo: Path, game_id: str) -> dict:
    cfg = GAMES[game_id]
    connector: BaseConnector = cfg["connector"]()

    html = connector.fetch_with_retry(cfg["source_url"], max_retries=3)
    if not html:
        raise RuntimeError(f"Failed to fetch {cfg['source_url']}")

    # Use heuristic parser to avoid brittle selectors.
    draws: List[DrawResult] = parse_pais_archive_html(
        html,
        game_id=game_id,
        source_url=cfg["source_url"],
        numbers_count=cfg["numbers_count"],
        bonus_count=cfg["bonus_count"],
        min_num=cfg["min_num"],
        max_num=cfg["max_num"],
    )

    # Compute checksum using connector helper
    for d in draws:
        d.checksum = connector.calculate_checksum(d)

    # Write per-year NDJSON with dedup by draw_id
    base_dir = data_repo / cfg["data_subdir"]
    added = 0
    last_date = None

    # Group by year
    by_year: Dict[int, List[DrawResult]] = {}
    for d in draws:
        by_year.setdefault(d.draw_date.year, []).append(d)

    for year, year_draws in by_year.items():
        year_path = base_dir / f"{year}.ndjson"
        existing = _load_existing_ids(year_path)

        payloads = []
        for d in sorted(year_draws, key=lambda x: (x.draw_date, x.draw_id)):
            if d.draw_id in existing:
                continue
            payloads.append(
                {
                    "game_id": d.game_id,
                    "draw_id": d.draw_id,
                    "date": d.draw_date.date().isoformat(),
                    "numbers": d.numbers,
                    "bonus": d.bonus_numbers,
                    "source": d.source_url,
                    "checksum": d.checksum,
                    "metadata": d.metadata,
                }
            )
            existing.add(d.draw_id)
            added += 1
            last_date = d.draw_date

        if payloads:
            write_ndjson(year_path, payloads)

    return {
        "game_id": game_id,
        "fetched": len(draws),
        "added": added,
        "last_draw_date": last_date.date().isoformat() if last_date else None,
        "source": cfg["source_url"],
    }


def update_coverage(data_repo: Path, game_results: List[dict]) -> None:
    cov_path = data_repo / "datasets/_meta/coverage.json"
    cov = load_json(cov_path, default={"last_updated": None, "games": {}})

    cov["last_updated"] = utc_now_iso()

    for r in game_results:
        gid = r["game_id"]
        cov.setdefault("games", {}).setdefault(gid, {})
        g = cov["games"][gid]
        g["last_draw_date"] = r["last_draw_date"]
        g["coverage_status"] = "incremental" if r["added"] else g.get("coverage_status", "initial")
        g["last_ingest"] = {
            "utc": utc_now_iso(),
            "fetched": r["fetched"],
            "added": r["added"],
            "source": r["source"],
        }

    dump_json(cov_path, cov)


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest official Israeli lottery archives into the data repo")
    ap.add_argument("--data-repo-path", required=True, help="Path to checked-out lottery-data-archive repo")
    ap.add_argument("--games", default="all", help="Comma-separated game ids or 'all'")
    ap.add_argument("--mode", default="incremental", choices=["incremental", "full"], help="Ingestion mode")
    ap.add_argument("--log-path", default=None, help="Optional log file path")
    args = ap.parse_args()

    data_repo = Path(args.data_repo_path).resolve()
    log_path = Path(args.log_path).resolve() if args.log_path else None
    _configure_logging(log_path)

    if args.games.strip().lower() == "all":
        game_ids = list(GAMES.keys())
    else:
        game_ids = [g.strip() for g in args.games.split(",") if g.strip()]

    LOGGER.info(f"Starting ingestion: games={game_ids}, mode={args.mode}, data_repo={data_repo}")

    results: List[dict] = []
    for gid in game_ids:
        if gid not in GAMES:
            LOGGER.warning(f"Unknown game id: {gid} (skipping)")
            continue
        try:
            r = ingest_game(data_repo, gid)
            LOGGER.info(f"Ingested {gid}: fetched={r['fetched']} added={r['added']} last={r['last_draw_date']}")
            results.append(r)
        except Exception as e:
            LOGGER.exception(f"Failed ingest for {gid}: {e}")

    update_coverage(data_repo, results)
    LOGGER.info("Ingestion complete")


if __name__ == "__main__":
    main()
