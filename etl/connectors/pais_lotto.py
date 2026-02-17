"""
Mifal HaPais Lotto Connector - מחבר לוטו מפעל הפיס
מקור רשמי: https://www.pais.co.il/lotto/archive.aspx
"""
from datetime import datetime, timedelta
from typing import List
from bs4 import BeautifulSoup
import re
from .base_connector import BaseConnector, DrawResult

class PaisLottoConnector(BaseConnector):
    """מחבר ללוטו מפעל הפיס"""
    
    OFFICIAL_URL = "https://www.pais.co.il/lotto/archive.aspx"
    GAME_CONFIG = {
        'numbers_count': 6,
        'bonus_count': 1,
        'number_range': (1, 37),
        'draws_per_week': 2  # שבת ושלישי
    }
    
    def __init__(self):
        super().__init__(
            game_name="pais_lotto",
            official_domain="pais.co.il"
        )
    
    def fetch_latest(self, days: int = 7) -> List[DrawResult]:
        """משיכת הגרלות אחרונות"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return self.fetch_historical(start_date, end_date)
    
    def fetch_historical(self, start_date: datetime, end_date: datetime) -> List[DrawResult]:
        """
        משיכת ארכיון מלא
        
        הערה: זהו קוד דוגמה - צריך להתאים למבנה HTML האמיתי של האתר
        כדי להשלים את המימוש, יש לבדוק את המבנה המדויק בדפדפן ולעדכן את ה-selectors
        """
        results = []
        
        html = self.fetch_with_retry(self.OFFICIAL_URL)
        if not html:
            self.logger.error("Failed to fetch archive page")
            return results
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # דוגמה - צריך להתאים למבנה האמיתי
            # הנחה: כל הגרלה היא שורה בטבלה
            draw_rows = soup.find_all('tr', class_='draw-row')  # דוגמה - לא המחלקה האמיתית
            
            for row in draw_rows:
                try:
                    draw = self._parse_draw_row(row)
                    if draw and start_date <= draw.draw_date <= end_date:
                        results.append(draw)
                except Exception as e:
                    self.logger.error(f"Failed to parse draw row: {e}", exc_info=True)
                    continue
            
            self.logger.info(f"Fetched {len(results)} draws from {start_date} to {end_date}")
            
        except Exception as e:
            self.logger.error(f"Failed to parse archive page: {e}", exc_info=True)
        
        return results
    
    def _parse_draw_row(self, row) -> DrawResult:
        """
        פרסור שורת הגרלה בודדת
        
        צריך להתאים למבנה האמיתי של ה-HTML:
        - מספר הגרלה
        - תאריך
        - 6 מספרים ראשיים
        - מספר חזק (בונוס)
        """
        # דוגמה - צריך לאתר את ה-selectors הנכונים
        draw_id = row.find('td', class_='draw-number').text.strip()
        date_text = row.find('td', class_='draw-date').text.strip()
        
        # פרסור תאריך (פורמט ישראלי: DD/MM/YYYY)
        draw_date = datetime.strptime(date_text, '%d/%m/%Y')
        
        # מספרים
        number_cells = row.find_all('td', class_='number')
        numbers = [int(cell.text.strip()) for cell in number_cells[:6]]
        
        # מספר חזק
        bonus_cell = row.find('td', class_='bonus-number')
        bonus_numbers = [int(bonus_cell.text.strip())] if bonus_cell else None
        
        # בניית אובייקט DrawResult
        draw = DrawResult(
            game_id=self.game_name,
            draw_id=draw_id,
            draw_date=draw_date,
            numbers=sorted(numbers),
            bonus_numbers=bonus_numbers,
            metadata={
                'game_type': 'lotto',
                'operator': 'mifal_hapais'
            },
            source_url=self.OFFICIAL_URL,
            checksum=''  # יושלם בשלב הבא
        )
        
        # חישוב checksum
        draw.checksum = self.calculate_checksum(draw)
        
        return draw
    
    def validate_draw(self, draw: DrawResult) -> bool:
        """אימות תקינות הגרלה"""
        # בדיקת כמות מספרים
        if len(draw.numbers) != self.GAME_CONFIG['numbers_count']:
            self.logger.error(f"Invalid number count: {len(draw.numbers)}")
            return False
        
        # בדיקת טווח
        min_num, max_num = self.GAME_CONFIG['number_range']
        if not all(min_num <= num <= max_num for num in draw.numbers):
            self.logger.error(f"Numbers out of range: {draw.numbers}")
            return False
        
        # בדיקת יחידות
        if len(draw.numbers) != len(set(draw.numbers)):
            self.logger.error(f"Duplicate numbers: {draw.numbers}")
            return False
        
        return True
