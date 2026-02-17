"""
ETL Connectors - מחברים למקורות רשמיים בלבד
"""
from .base_connector import BaseConnector, DrawResult
from .pais_lotto import PaisLottoConnector
from .pais_chance import PaisChanceConnector

__all__ = [
    'BaseConnector',
    'DrawResult',
    'PaisLottoConnector',
    'PaisChanceConnector',
]
