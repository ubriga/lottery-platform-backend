"""Game definitions and configurations"""

GAMES_REGISTRY = {
    'lotto': {
        'id': 'lotto',
        'name': 'לוטו',
        'operator': 'מפעל הפיס',
        'game_type': 'lottery',
        'rules': {
            'main_numbers': 6,
            'main_range': [1, 37],
            'bonus_numbers': 1,
            'bonus_range': [1, 7],
            'strong_number': True
        },
        'frequency': 'twice_weekly',
        'start_date': '1987-01-01',
        'official_source': 'https://www.pais.co.il/lotto/archive.aspx'
    },
    'chance': {
        'id': 'chance',
        'name': 'צ׳אנס',
        'operator': 'מפעל הפיס',
        'game_type': 'lottery',
        'rules': {
            'main_numbers': 6,
            'main_range': [1, 37],
            'bonus_numbers': 1,
            'bonus_range': [1, 7]
        },
        'frequency': 'daily',
        'start_date': '1989-01-01',
        'official_source': 'https://www.pais.co.il/chance/archive.aspx'
    },
    '777': {
        'id': '777',
        'name': '777',
        'operator': 'מפעל הפיס',
        'game_type': 'lottery',
        'rules': {
            'main_numbers': 7,
            'main_range': [0, 9],
            'digit_game': True
        },
        'frequency': 'weekly',
        'start_date': '1990-01-01',
        'official_source': 'https://www.pais.co.il/777/archive.aspx'
    },
    '123': {
        'id': '123',
        'name': '123',
        'operator': 'מפעל הפיס',
        'game_type': 'lottery',
        'rules': {
            'main_numbers': 3,
            'main_range': [0, 9],
            'digit_game': True
        },
        'frequency': 'daily',
        'start_date': '2000-01-01',
        'official_source': 'https://www.pais.co.il/123/archive.aspx'
    },
    'winner16': {
        'id': 'winner16',
        'name': 'ווינר 16 / טוטו',
        'operator': 'ספורטוטו',
        'game_type': 'sports_betting',
        'rules': {
            'matches': 16,
            'outcomes': ['1', 'X', '2'],
            'min_correct': 14
        },
        'frequency': 'weekly',
        'start_date': '1972-01-01',
        'official_source': 'https://www.sportoto.co.il'
    },
    'winner_global': {
        'id': 'winner_global',
        'name': 'ווינר עולמי',
        'operator': 'ספורטוטו',
        'game_type': 'sports_betting',
        'rules': {
            'matches': 14,
            'outcomes': ['1', 'X', '2'],
            'min_correct': 12
        },
        'frequency': 'weekly',
        'start_date': '2000-01-01',
        'official_source': 'https://www.sportoto.co.il'
    },
    'winner_millionaire': {
        'id': 'winner_millionaire',
        'name': 'ווינר מיליונר',
        'operator': 'ספורטוטו',
        'game_type': 'sports_betting',
        'rules': {
            'matches': 16,
            'outcomes': ['1', 'X', '2'],
            'jackpot_game': True
        },
        'frequency': 'special',
        'start_date': '2010-01-01',
        'official_source': 'https://www.sportoto.co.il'
    },
    'winner_horses': {
        'id': 'winner_horses',
        'name': 'ווינר מרוצים',
        'operator': 'ספורטוטו',
        'game_type': 'horse_racing',
        'rules': {
            'races': 7,
            'bet_types': ['win', 'place', 'exacta', 'trifecta']
        },
        'frequency': 'weekly',
        'start_date': '1975-01-01',
        'official_source': 'https://www.sportoto.co.il'
    }
}

def get_game(game_id):
    """Get game configuration by ID"""
    return GAMES_REGISTRY.get(game_id)

def get_all_games():
    """Get all game configurations"""
    return list(GAMES_REGISTRY.values())

def get_games_by_operator(operator):
    """Get games by operator"""
    return [g for g in GAMES_REGISTRY.values() if g['operator'] == operator]
