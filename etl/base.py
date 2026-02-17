"""Base ETL class"""

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class BaseETL(ABC):
    """Base class for all ETL processes"""
    
    def __init__(self, game_config, db):
        self.game_config = game_config
        self.db = db
        self.game_id = game_config['id']
        self.source_url = game_config.get('official_source')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @abstractmethod
    def fetch_data(self, mode='incremental'):
        """
        Fetch data from source
        mode: 'full' or 'incremental'
        """
        pass
    
    @abstractmethod
    def parse_data(self, raw_data):
        """Parse raw data into structured format"""
        pass
    
    def validate_draw(self, draw_data):
        """Validate draw data structure"""
        required_fields = ['draw_number', 'draw_date', 'results']
        return all(field in draw_data for field in required_fields)
    
    def run(self, mode='incremental'):
        """Execute full ETL pipeline"""
        start_time = time.time()
        run_data = {
            'game_id': self.game_id,
            'status': 'started'
        }
        
        try:
            logger.info(f"Starting ETL for {self.game_id} in {mode} mode")
            
            # Fetch
            raw_data = self.fetch_data(mode=mode)
            run_data['records_fetched'] = len(raw_data) if isinstance(raw_data, list) else 0
            
            # Parse
            parsed_draws = self.parse_data(raw_data)
            
            # Load
            inserted = 0
            updated = 0
            errors = []
            
            for draw in parsed_draws:
                if not self.validate_draw(draw):
                    errors.append(f"Invalid draw: {draw}")
                    continue
                
                draw['game_id'] = self.game_id
                result = self.db.insert_draw(draw)
                
                if result is not None:
                    inserted += 1
                else:
                    updated += 1
            
            run_data['status'] = 'success'
            run_data['records_inserted'] = inserted
            run_data['records_updated'] = updated
            run_data['errors'] = errors
            
            logger.info(f"ETL completed for {self.game_id}: {inserted} inserted, {updated} updated")
            
        except Exception as e:
            logger.error(f"ETL failed for {self.game_id}: {e}")
            run_data['status'] = 'failed'
            run_data['errors'] = [str(e)]
        
        finally:
            run_data['duration_seconds'] = time.time() - start_time
            self.db.log_ingestion_run(run_data)
        
        return run_data
    
    def fetch_url(self, url, params=None, timeout=30):
        """Fetch URL with error handling"""
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            raise
    
    def parse_html(self, html_content):
        """Parse HTML content"""
        return BeautifulSoup(html_content, 'html.parser')
