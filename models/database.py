"""Database models and schema"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class Database:
    """SQLite database manager"""
    
    def __init__(self, db_path='data/lottery.db'):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Games table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    game_type TEXT NOT NULL,
                    rules JSON NOT NULL,
                    frequency TEXT,
                    start_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    official_source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Draws table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS draws (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    draw_number INTEGER NOT NULL,
                    draw_date DATE NOT NULL,
                    results JSON NOT NULL,
                    extra_data JSON,
                    source_url TEXT,
                    verified BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games(id),
                    UNIQUE(game_id, draw_number)
                )
            ''')
            
            # Ingestion runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ingestion_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT,
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    records_fetched INTEGER DEFAULT 0,
                    records_inserted INTEGER DEFAULT 0,
                    records_updated INTEGER DEFAULT 0,
                    errors JSON,
                    duration_seconds REAL,
                    checksum TEXT
                )
            ''')
            
            # Recommendations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT NOT NULL,
                    parameters JSON,
                    recommendations JSON NOT NULL,
                    confidence_score REAL,
                    FOREIGN KEY (game_id) REFERENCES games(id)
                )
            ''')
            
            # Admin users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'admin',
                    is_active BOOLEAN DEFAULT 1,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ETL schedules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS etl_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    schedule_type TEXT NOT NULL,
                    cron_expression TEXT,
                    is_enabled BOOLEAN DEFAULT 1,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games(id)
                )
            ''')
            
            logger.info("Database initialized successfully")
    
    def insert_game(self, game_data):
        """Insert or update game"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO games 
                (id, name, operator, game_type, rules, frequency, start_date, official_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game_data['id'],
                game_data['name'],
                game_data['operator'],
                game_data['game_type'],
                json.dumps(game_data['rules']),
                game_data.get('frequency'),
                game_data.get('start_date'),
                game_data.get('official_source')
            ))
            return cursor.lastrowid
    
    def insert_draw(self, draw_data):
        """Insert draw result (with duplicate prevention)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO draws 
                    (game_id, draw_number, draw_date, results, extra_data, source_url, verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    draw_data['game_id'],
                    draw_data['draw_number'],
                    draw_data['draw_date'],
                    json.dumps(draw_data['results']),
                    json.dumps(draw_data.get('extra_data', {})),
                    draw_data.get('source_url'),
                    draw_data.get('verified', False)
                ))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Already exists - update instead
                cursor.execute('''
                    UPDATE draws SET
                        results = ?,
                        extra_data = ?,
                        source_url = ?,
                        verified = ?
                    WHERE game_id = ? AND draw_number = ?
                ''', (
                    json.dumps(draw_data['results']),
                    json.dumps(draw_data.get('extra_data', {})),
                    draw_data.get('source_url'),
                    draw_data.get('verified', False),
                    draw_data['game_id'],
                    draw_data['draw_number']
                ))
                return None
    
    def get_draws(self, game_id, limit=100, offset=0):
        """Get draws for a game"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM draws 
                WHERE game_id = ?
                ORDER BY draw_date DESC
                LIMIT ? OFFSET ?
            ''', (game_id, limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def log_ingestion_run(self, run_data):
        """Log an ingestion run"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ingestion_runs
                (game_id, status, records_fetched, records_inserted, records_updated, errors, duration_seconds, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_data.get('game_id'),
                run_data['status'],
                run_data.get('records_fetched', 0),
                run_data.get('records_inserted', 0),
                run_data.get('records_updated', 0),
                json.dumps(run_data.get('errors', [])),
                run_data.get('duration_seconds'),
                run_data.get('checksum')
            ))
            return cursor.lastrowid
