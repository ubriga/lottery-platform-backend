"""Main API routes"""

from flask import Blueprint, jsonify, request
from models.database import Database
from models.games import get_all_games, get_game
from analytics.statistics import StatisticsEngine
from analytics.recommendations import RecommendationEngine
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)
db = Database()

@api_bp.route('/games', methods=['GET'])
def list_games():
    """List all available games"""
    try:
        games = get_all_games()
        return jsonify({
            'success': True,
            'count': len(games),
            'games': games
        }), 200
    except Exception as e:
        logger.error(f"Error listing games: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/games/<game_id>', methods=['GET'])
def get_game_details(game_id):
    """Get details for a specific game"""
    try:
        game = get_game(game_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404
        
        # Get draw count
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM draws WHERE game_id = ?', (game_id,))
            draw_count = cursor.fetchone()['count']
        
        game['total_draws'] = draw_count
        return jsonify({'success': True, 'game': game}), 200
    except Exception as e:
        logger.error(f"Error getting game {game_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/draws/<game_id>', methods=['GET'])
def get_draws(game_id):
    """Get draw results for a game"""
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        
        draws = db.get_draws(game_id, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'count': len(draws),
            'limit': limit,
            'offset': offset,
            'draws': draws
        }), 200
    except Exception as e:
        logger.error(f"Error getting draws for {game_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/draws/<game_id>/latest', methods=['GET'])
def get_latest_draw(game_id):
    """Get the latest draw for a game"""
    try:
        draws = db.get_draws(game_id, limit=1)
        if not draws:
            return jsonify({'success': False, 'error': 'No draws found'}), 404
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'draw': draws[0]
        }), 200
    except Exception as e:
        logger.error(f"Error getting latest draw for {game_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/stats/<game_id>', methods=['GET'])
def get_statistics(game_id):
    """Get statistical analysis for a game"""
    try:
        game = get_game(game_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404
        
        draws = db.get_draws(game_id, limit=1000)
        if not draws:
            return jsonify({'success': False, 'error': 'No data available'}), 404
        
        stats_engine = StatisticsEngine(game, draws)
        stats = stats_engine.analyze()
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'statistics': stats,
            'sample_size': len(draws),
            'last_updated': draws[0]['draw_date'] if draws else None
        }), 200
    except Exception as e:
        logger.error(f"Error calculating stats for {game_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/recommendations/<game_id>', methods=['GET'])
def get_recommendations(game_id):
    """Get recommendations based on analysis"""
    try:
        game = get_game(game_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404
        
        draws = db.get_draws(game_id, limit=1000)
        if not draws:
            return jsonify({'success': False, 'error': 'No data available'}), 404
        
        rec_engine = RecommendationEngine(game, draws)
        recommendations = rec_engine.generate()
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'recommendations': recommendations,
            'disclaimer': 'המלצות אלו מבוססות על ניתוח סטטיסטי ואינן מבטיחות זכייה'
        }), 200
    except Exception as e:
        logger.error(f"Error generating recommendations for {game_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/coverage', methods=['GET'])
def get_data_coverage():
    """Get data coverage report"""
    try:
        coverage = []
        games = get_all_games()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            for game in games:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_draws,
                        MIN(draw_date) as first_draw,
                        MAX(draw_date) as last_draw,
                        SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as verified_draws
                    FROM draws
                    WHERE game_id = ?
                ''', (game['id'],))
                
                data = cursor.fetchone()
                coverage.append({
                    'game_id': game['id'],
                    'game_name': game['name'],
                    'total_draws': data['total_draws'] or 0,
                    'first_draw': data['first_draw'],
                    'last_draw': data['last_draw'],
                    'verified_draws': data['verified_draws'] or 0,
                    'official_source': game.get('official_source')
                })
        
        return jsonify({
            'success': True,
            'coverage': coverage
        }), 200
    except Exception as e:
        logger.error(f"Error getting coverage: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
