"""Pattern detection algorithms"""

import numpy as np
from sklearn.cluster import KMeans
import json
import logging

logger = logging.getLogger(__name__)

class PatternDetector:
    """Advanced pattern detection in lottery draws"""
    
    def __init__(self, game_config, draws):
        self.game = game_config
        self.draws = draws
    
    def detect_all(self):
        """Run all pattern detection algorithms"""
        return {
            'clusters': self.cluster_analysis(),
            'gaps': self.gap_analysis(),
            'sequences': self.sequence_analysis()
        }
    
    def cluster_analysis(self):
        """Cluster analysis of number combinations"""
        if len(self.draws) < 20:
            return {'status': 'insufficient_data'}
        
        try:
            # Extract number vectors
            vectors = []
            for draw in self.draws[:100]:  # Last 100 draws
                try:
                    results = json.loads(draw['results']) if isinstance(draw['results'], str) else draw['results']
                    if isinstance(results, dict):
                        nums = results.get('main_numbers', [])
                    else:
                        nums = results
                    
                    # Create binary vector
                    max_num = self.game['rules'].get('main_range', [1, 50])[1]
                    vector = [1 if i in nums else 0 for i in range(1, max_num + 1)]
                    vectors.append(vector)
                except:
                    continue
            
            if len(vectors) < 10:
                return {'status': 'insufficient_valid_data'}
            
            # K-means clustering
            n_clusters = min(5, len(vectors) // 5)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            kmeans.fit(vectors)
            
            return {
                'n_clusters': n_clusters,
                'cluster_sizes': [int(np.sum(kmeans.labels_ == i)) for i in range(n_clusters)],
                'interpretation': f'זוהו {n_clusters} קבוצות עיקריות של תבניות מספרים'
            }
        except Exception as e:
            logger.error(f"Cluster analysis error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def gap_analysis(self):
        """Analyze gaps between number appearances"""
        if len(self.draws) < 10:
            return {}
        
        # Track last appearance of each number
        max_num = self.game['rules'].get('main_range', [1, 50])[1]
        last_seen = {i: -1 for i in range(1, max_num + 1)}
        gaps = {i: [] for i in range(1, max_num + 1)}
        
        for idx, draw in enumerate(reversed(self.draws)):  # Oldest to newest
            try:
                results = json.loads(draw['results']) if isinstance(draw['results'], str) else draw['results']
                if isinstance(results, dict):
                    nums = results.get('main_numbers', [])
                else:
                    nums = results
                
                for num in nums:
                    if num in last_seen:
                        if last_seen[num] >= 0:
                            gaps[num].append(idx - last_seen[num])
                        last_seen[num] = idx
            except:
                continue
        
        # Calculate average gaps
        avg_gaps = {}
        for num, gap_list in gaps.items():
            if gap_list:
                avg_gaps[num] = np.mean(gap_list)
        
        # Find numbers with longest current gap
        current_gaps = [(num, len(self.draws) - last_seen[num] - 1) 
                       for num in last_seen if last_seen[num] >= 0]
        current_gaps.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'longest_gaps': current_gaps[:10],
            'average_gaps': dict(sorted(avg_gaps.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def sequence_analysis(self):
        """Detect sequential patterns"""
        if len(self.draws) < 5:
            return {}
        
        consecutive_pairs = 0
        total_pairs = 0
        
        for draw in self.draws:
            try:
                results = json.loads(draw['results']) if isinstance(draw['results'], str) else draw['results']
                if isinstance(results, dict):
                    nums = sorted(results.get('main_numbers', []))
                else:
                    nums = sorted(results)
                
                for i in range(len(nums) - 1):
                    total_pairs += 1
                    if nums[i+1] - nums[i] == 1:
                        consecutive_pairs += 1
            except:
                continue
        
        return {
            'consecutive_rate': consecutive_pairs / max(total_pairs, 1),
            'total_analyzed': total_pairs
        }
