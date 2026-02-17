#!/usr/bin/env python3
"""ETL orchestration script"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from models.database import Database
from models.games import get_game, get_all_games
from etl.pais import LottoETL, ChanceETL, Pais777ETL, Pais123ETL
from etl.sportoto import Winner16ETL, WinnerGlobalETL, WinnerMillionaireETL, WinnerHorsesETL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ETL_CLASSES = {
    'lotto': LottoETL,
    'chance': ChanceETL,
    '777': Pais777ETL,
    '123': Pais123ETL,
    'winner16': Winner16ETL,
    'winner_global': WinnerGlobalETL,
    'winner_millionaire': WinnerMillionaireETL,
    'winner_horses': WinnerHorsesETL,
}

def run_etl(game_id='all', mode='incremental'):
    """Run ETL for specified game(s)"""
    db = Database()
    results = {}
    
    if game_id == 'all':
        games = get_all_games()
        game_ids = [g['id'] for g in games]
    else:
        game_ids = [game_id]
    
    for gid in game_ids:
        game = get_game(gid)
        if not game:
            logger.warning(f"Game {gid} not found")
            continue
        
        etl_class = ETL_CLASSES.get(gid)
        if not etl_class:
            logger.warning(f"No ETL implementation for {gid}")
            results[gid] = {'status': 'not_implemented'}
            continue
        
        logger.info(f"Running ETL for {game['name']}")
        etl = etl_class(game, db)
        result = etl.run(mode=mode)
        results[gid] = result
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Run lottery ETL')
    parser.add_argument('--game', default='all', help='Game ID or "all"')
    parser.add_argument('--mode', default='incremental', choices=['full', 'incremental'])
    
    args = parser.parse_args()
    
    results = run_etl(game_id=args.game, mode=args.mode)
    
    logger.info("ETL Results:")
    for game_id, result in results.items():
        logger.info(f"  {game_id}: {result['status']} - "
                   f"Inserted: {result.get('records_inserted', 0)}, "
                   f"Updated: {result.get('records_updated', 0)}")

if __name__ == '__main__':
    main()
