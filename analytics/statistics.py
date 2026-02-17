"""Statistical analysis engine"""

import numpy as np
from scipy import stats
from collections import Counter
import json
import logging

logger = logging.getLogger(__name__)

class StatisticsEngine:
    """Advanced statistical analysis for lottery data"""
    
    def __init__(self, game_config, draws):
        self.game = game_config
        self.draws = draws
        self.numbers = self._extract_numbers()
    
    def _extract_numbers(self):
        """Extract all numbers from draws"""
        all_numbers = []
        for draw in self.draws:
            try:
                results = json.loads(draw['results']) if isinstance(draw['results'], str) else draw['results']
                if isinstance(results, dict) and 'main_numbers' in results:
                    all_numbers.extend(results['main_numbers'])
                elif isinstance(results, list):
                    all_numbers.extend(results)
            except:
                continue
        return all_numbers
    
    def analyze(self):
        """Run full statistical analysis"""
        return {
            'frequency': self.frequency_analysis(),
            'distribution': self.distribution_analysis(),
            'patterns': self.pattern_analysis(),
            'fairness': self.fairness_tests(),
            'trends': self.trend_analysis()
        }
    
    def frequency_analysis(self):
        """Analyze number frequency"""
        if not self.numbers:
            return {}
        
        counter = Counter(self.numbers)
        total = len(self.numbers)
        
        return {
            'most_common': counter.most_common(10),
            'least_common': counter.most_common()[:-11:-1],
            'frequencies': dict(counter),
            'total_draws': len(self.draws),
            'total_numbers': total
        }
    
    def distribution_analysis(self):
        """Analyze statistical distribution"""
        if not self.numbers:
            return {}
        
        arr = np.array(self.numbers)
        
        return {
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'variance': float(np.var(arr)),
            'min': int(np.min(arr)),
            'max': int(np.max(arr)),
            'quartiles': {
                'q1': float(np.percentile(arr, 25)),
                'q2': float(np.percentile(arr, 50)),
                'q3': float(np.percentile(arr, 75))
            }
        }
    
    def pattern_analysis(self):
        """Detect patterns in draws"""
        if len(self.draws) < 10:
            return {}
        
        # Consecutive numbers
        consecutive_count = 0
        for i in range(len(self.draws) - 1):
            try:
                curr = json.loads(self.draws[i]['results']) if isinstance(self.draws[i]['results'], str) else self.draws[i]['results']
                next_draw = json.loads(self.draws[i+1]['results']) if isinstance(self.draws[i+1]['results'], str) else self.draws[i+1]['results']
                
                if isinstance(curr, dict):
                    curr = curr.get('main_numbers', [])
                if isinstance(next_draw, dict):
                    next_draw = next_draw.get('main_numbers', [])
                
                if set(curr) & set(next_draw):
                    consecutive_count += 1
            except:
                continue
        
        return {
            'consecutive_overlap_rate': consecutive_count / (len(self.draws) - 1) if len(self.draws) > 1 else 0,
            'sample_size': len(self.draws)
        }
    
    def fairness_tests(self):
        """Test draw fairness using statistical tests"""
        if not self.numbers or len(self.numbers) < 30:
            return {'status': 'insufficient_data'}
        
        try:
            # Chi-square goodness of fit test
            counter = Counter(self.numbers)
            observed = list(counter.values())
            expected_freq = len(self.numbers) / len(counter)
            expected = [expected_freq] * len(counter)
            
            chi2_stat, p_value = stats.chisquare(observed, expected)
            
            # Runs test for randomness
            median = np.median(self.numbers)
            runs_sequence = [1 if x > median else 0 for x in self.numbers]
            
            return {
                'chi_square': {
                    'statistic': float(chi2_stat),
                    'p_value': float(p_value),
                    'is_fair': p_value > 0.05,
                    'interpretation': 'התפלגות אחידה' if p_value > 0.05 else 'סטייה מהתפלגות אחידה'
                },
                'sample_size': len(self.numbers)
            }
        except Exception as e:
            logger.error(f"Fairness test error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def trend_analysis(self):
        """Analyze trends over time"""
        if len(self.draws) < 20:
            return {}
        
        # Recent vs historical frequency
        recent_count = min(50, len(self.draws) // 4)
        recent_draws = self.draws[:recent_count]
        historical_draws = self.draws[recent_count:]
        
        recent_numbers = []
        historical_numbers = []
        
        for draw in recent_draws:
            try:
                results = json.loads(draw['results']) if isinstance(draw['results'], str) else draw['results']
                if isinstance(results, dict):
                    recent_numbers.extend(results.get('main_numbers', []))
                elif isinstance(results, list):
                    recent_numbers.extend(results)
            except:
                continue
        
        for draw in historical_draws:
            try:
                results = json.loads(draw['results']) if isinstance(draw['results'], str) else draw['results']
                if isinstance(results, dict):
                    historical_numbers.extend(results.get('main_numbers', []))
                elif isinstance(results, list):
                    historical_numbers.extend(results)
            except:
                continue
        
        recent_counter = Counter(recent_numbers)
        historical_counter = Counter(historical_numbers)
        
        # Find "hot" and "cold" numbers
        all_nums = set(recent_counter.keys()) | set(historical_counter.keys())
        hot_numbers = []
        cold_numbers = []
        
        for num in all_nums:
            recent_freq = recent_counter.get(num, 0) / max(len(recent_numbers), 1)
            hist_freq = historical_counter.get(num, 0) / max(len(historical_numbers), 1)
            
            if recent_freq > hist_freq * 1.2:
                hot_numbers.append(num)
            elif recent_freq < hist_freq * 0.8:
                cold_numbers.append(num)
        
        return {
            'hot_numbers': sorted(hot_numbers)[:10],
            'cold_numbers': sorted(cold_numbers)[:10],
            'recent_sample': len(recent_numbers),
            'historical_sample': len(historical_numbers)
        }
