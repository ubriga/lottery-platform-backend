#!/usr/bin/env python3
"""Initialize database with game definitions"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Database
from models.games import get_all_games
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize database"""
    logger.info("Initializing database...")
    
    # Create database
    db = Database()
    
    # Insert all games
    games = get_all_games()
    for game in games:
        logger.info(f"Inserting game: {game['name']}")
        db.insert_game(game)
    
    logger.info(f"Database initialized with {len(games)} games")

if __name__ == '__main__':
    main()
