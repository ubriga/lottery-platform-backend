"""Recommendation engine using statistical analysis and simulations"""

import numpy as np
import json
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Generate recommendations based on analysis (NOT predictions)"""
    
    def __init__(self, game_config, draws):
        self.game = game_config
        self.draws = draws
    
    def generate(self):
        """Generate recommendations"""
        return {
            'diversified_sets': self.diversified_coverage(),
            'balanced_set': self.balanced_selection(),
            'hot_cold_mix': self.hot_cold_strategy(),
            'disclaimer': self._get_disclaimer()
        }
    
    def diversified_coverage(self, n_sets=3):
        """
        Generate diversified number sets to maximize coverage
        This is combinatorial optimization, not prediction
        """
        try:
            rules = self.game['rules']
            num_count = rules.get('main_numbers', 6)
            min_num, max_num = rules.get('main_range', [1, 37])
            
            sets = []
            all_nums = list(range(min_num, max_num + 1))
            
            for i in range(n_sets):
                # Ensure diversity by avoiding overlap
                if i == 0:
                    selected = np.random.choice(all_nums, num_count, replace=False)
                else:
                    # Prefer numbers not in previous sets
                    used = set([n for s in sets for n in s])
                    available = [n for n in all_nums if n not in used]
                    
                    if len(available) >= num_count:
                        selected = np.random.choice(available, num_count, replace=False)
                    else:
                        selected = np.random.choice(all_nums, num_count, replace=False)
                
                sets.append(sorted(selected.tolist()))
            
            return {
                'sets': sets,
                'strategy': 'פיזור מקסימלי - מזער חפיפה',
                'note': 'כל סט מכסה טווח מספרים שונה'
            }
        except Exception as e:
            logger.error(f"Diversification error: {e}")
            return {'status': 'error'}
    
    def balanced_selection(self):
        """Select balanced set (spread across range)"""
        try:
            rules = self.game['rules']
            num_count = rules.get('main_numbers', 6)
            min_num, max_num = rules.get('main_range', [1, 37])
            
            # Divide range into segments
            segment_size = (max_num - min_num + 1) / num_count
            selected = []
            
            for i in range(num_count):
                seg_start = int(min_num + i * segment_size)
                seg_end = int(min_num + (i + 1) * segment_size)
                selected.append(np.random.randint(seg_start, seg_end + 1))
            
            return {
                'numbers': sorted(selected),
                'strategy': 'בחירה מאוזנת לאורך הטווח',
                'note': 'מספר אחד מכל סגמנט בטווח'
            }
        except Exception as e:
            logger.error(f"Balanced selection error: {e}")
            return {'status': 'error'}
    
    def hot_cold_strategy(self):
        """Mix of frequently and rarely drawn numbers"""
        try:
            # Extract all numbers
            all_numbers = []
            for draw in self.draws[:100]:  # Last 100 draws
                try:
                    results = json.loads(draw['results']) if isinstance(draw['results'], str) else draw['results']
                    if isinstance(results, dict):
                        all_numbers.extend(results.get('main_numbers', []))
                    elif isinstance(results, list):
                        all_numbers.extend(results)
                except:
                    continue
            
            if not all_numbers:
                return {'status': 'no_data'}
            
            counter = Counter(all_numbers)
            most_common = counter.most_common(20)
            least_common = counter.most_common()[:-21:-1]
            
            rules = self.game['rules']
            num_count = rules.get('main_numbers', 6)
            
            # Mix hot and cold
            hot_nums = [n for n, _ in most_common]
            cold_nums = [n for n, _ in least_common]
            
            hot_count = num_count // 2
            cold_count = num_count - hot_count
            
            selected_hot = np.random.choice(hot_nums, min(hot_count, len(hot_nums)), replace=False)
            selected_cold = np.random.choice(cold_nums, min(cold_count, len(cold_nums)), replace=False)
            
            return {
                'numbers': sorted(list(selected_hot) + list(selected_cold)),
                'hot_numbers': sorted(selected_hot.tolist()),
                'cold_numbers': sorted(selected_cold.tolist()),
                'strategy': 'שילוב מספרים "חמים" ו"קרים"',
                'note': 'שילוב מספרים תכופים ונדירים'
            }
        except Exception as e:
            logger.error(f"Hot/cold strategy error: {e}")
            return {'status': 'error'}
    
    def _get_disclaimer(self):
        """Important disclaimer"""
        return {
            'he': 'המלצות אלו מבוססות על ניתוח סטטיסטי ואופטימיזציה קומבינטורית. הן אינן מבטיחות זכייה ואינן מעלות את סיכויי הזכייה. בהגרלות אקראיות, כל צירוף הוא שווה-סיכויים.',
            'en': 'These recommendations are based on statistical analysis and combinatorial optimization. They do NOT guarantee winnings and do NOT increase winning probability. In random lotteries, all combinations are equally likely.'
        }
