"""Admin API routes"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.database import Database
from datetime import datetime
import logging
import hashlib

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)
db = Database()

def hash_password(password):
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Missing credentials'}), 400
        
        # Check credentials (simplified - use proper auth in production)
        from flask import current_app
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            access_token = create_access_token(identity=username)
            return jsonify({
                'success': True,
                'access_token': access_token,
                'username': username
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/trigger-etl', methods=['POST'])
@jwt_required()
def trigger_etl():
    """Manually trigger ETL process"""
    try:
        current_user = get_jwt_identity()
        logger.info(f"ETL triggered by {current_user}")
        
        data = request.get_json() or {}
        game_id = data.get('game_id', 'all')
        mode = data.get('mode', 'incremental')
        
        # Import and run ETL
        from scripts.etl_runner import run_etl
        result = run_etl(game_id=game_id, mode=mode)
        
        return jsonify({
            'success': True,
            'message': 'ETL completed',
            'result': result
        }), 200
    except Exception as e:
        logger.error(f"ETL trigger error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/ingestion-logs', methods=['GET'])
@jwt_required()
def get_ingestion_logs():
    """Get ETL ingestion logs"""
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM ingestion_runs
                ORDER BY run_date DESC
                LIMIT ?
            ''', (limit,))
            logs = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'logs': logs
        }), 200
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    """Get ETL schedules"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM etl_schedules ORDER BY game_id')
            schedules = [dict(row) for row in cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'schedules': schedules
        }), 200
    except Exception as e:
        logger.error(f"Error fetching schedules: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/schedules', methods=['POST'])
@jwt_required()
def update_schedule():
    """Update ETL schedule"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        cron_expression = data.get('cron_expression')
        is_enabled = data.get('is_enabled', True)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO etl_schedules
                (game_id, schedule_type, cron_expression, is_enabled, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (game_id, 'cron', cron_expression, is_enabled, datetime.now()))
        
        return jsonify({
            'success': True,
            'message': 'Schedule updated'
        }), 200
    except Exception as e:
        logger.error(f"Error updating schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/stats/system', methods=['GET'])
@jwt_required()
def get_system_stats():
    """Get system statistics"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total draws
            cursor.execute('SELECT COUNT(*) as count FROM draws')
            total_draws = cursor.fetchone()['count']
            
            # Draws by game
            cursor.execute('''
                SELECT game_id, COUNT(*) as count
                FROM draws
                GROUP BY game_id
            ''')
            draws_by_game = {row['game_id']: row['count'] for row in cursor.fetchall()}
            
            # Recent ingestion runs
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM ingestion_runs
                WHERE run_date > datetime('now', '-7 days')
                GROUP BY status
            ''')
            recent_runs = {row['status']: row['count'] for row in cursor.fetchall()}
        
        return jsonify({
            'success': True,
            'stats': {
                'total_draws': total_draws,
                'draws_by_game': draws_by_game,
                'recent_ingestion_runs': recent_runs
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
