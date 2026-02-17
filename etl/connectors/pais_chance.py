"""
Mifal HaPais Chance Connector - מחבר צ'אנס מפעל הפיס
מקור רשמי: https://www.pais.co.il/chance/archive.aspx
"""
from .pais_lotto import PaisLottoConnector

class PaisChanceConnector(PaisLottoConnector):
    """
    מחבר לצ'אנס מפעל הפיס
    משתמש באותו פורמט כמו לוטו אך עם URL שונה
    """
    
    OFFICIAL_URL = "https://www.pais.co.il/chance/archive.aspx"
    GAME_CONFIG = {
        'numbers_count': 6,
        'bonus_count': 1,
        'number_range': (1, 37),
        'draws_per_week': 1  # יום שישי
    }
    
    def __init__(self):
        # קורא ל-BaseConnector ישירות כדי לדלג על PaisLottoConnector.__init__
        super(PaisLottoConnector, self).__init__(
            game_name="pais_chance",
            official_domain="pais.co.il"
        )
