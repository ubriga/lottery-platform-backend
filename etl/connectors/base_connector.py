"""
Base Connector - תבנית בסיס לכל המחברים
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import hashlib
import requests
import time

@dataclass
class DrawResult:
    """Draw result structure"""
    game_id: str
    draw_id: str
    draw_date: datetime
    numbers: List[int]
    bonus_numbers: Optional[List[int]]
    metadata: Dict
    source_url: str
    checksum: str

class BaseConnector(ABC):
    """מחבר בסיס לכל מקורות הנתונים"""
    
    def __init__(self, game_name: str, official_domain: str):
        self.game_name = game_name
        self.official_domain = official_domain
        self.logger = logging.getLogger(f"connector.{game_name}")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Lottery Data Platform/1.0; +https://github.com/ubriga/lottery-platform-backend)'
        })
    
    @abstractmethod
    def fetch_latest(self, days: int = 7) -> List[DrawResult]:
        """משיכת תוצאות אחרונות"""
        pass
    
    @abstractmethod
    def fetch_historical(self, start_date: datetime, end_date: datetime) -> List[DrawResult]:
        """משיכת נתונים היסטוריים"""
        pass
    
    def validate_source(self, url: str) -> bool:
        """אימות שהמקור הוא רשמי"""
        return self.official_domain in url
    
    def calculate_checksum(self, draw: DrawResult) -> str:
        """חישוב checksum לזיהוי שינויים"""
        data = f"{draw.draw_id}|{draw.draw_date.isoformat()}|{sorted(draw.numbers)}"
        if draw.bonus_numbers:
            data += f"|{sorted(draw.bonus_numbers)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def fetch_with_retry(self, url: str, max_retries: int = 3, timeout: int = 30) -> Optional[str]:
        """משיכת נתונים עם retry logic"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                
                # אימות שלא היה redirect למקור לא רשמי
                if not self.validate_source(response.url):
                    self.logger.error(f"Redirected to non-official source: {response.url}")
                    return None
                
                return response.text
                
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
        
        return None
