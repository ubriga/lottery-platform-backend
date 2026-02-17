import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1)))
    JWT_TOKEN_LOCATION = ['headers']
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///lottery.db')
    
    # Admin
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # ETL Configuration
    ETL_SCHEDULE_CRON = os.getenv('ETL_SCHEDULE_CRON', '0 3 * * *')
    ETL_MAX_RETRIES = int(os.getenv('ETL_MAX_RETRIES', 3))
    ETL_TIMEOUT = int(os.getenv('ETL_TIMEOUT', 300))
    
    # Official Data Sources
    DATA_SOURCES = {
        'pais_lotto': os.getenv('PAIS_LOTTO_URL', 'https://www.pais.co.il/lotto/archive.aspx'),
        'pais_chance': os.getenv('PAIS_CHANCE_URL', 'https://www.pais.co.il/chance/archive.aspx'),
        'pais_777': os.getenv('PAIS_777_URL', 'https://www.pais.co.il/777/archive.aspx'),
        'sportoto_winner': os.getenv('SPORTOTO_WINNER_URL', 'https://www.sportoto.co.il'),
    }
    
    # GitHub
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_REPO = os.getenv('GITHUB_REPO', 'ubriga/lottery-data-archive')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
