"""API tests"""

import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """Test root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'running'

def test_health(client):
    """Test health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_games_list(client):
    """Test games list endpoint"""
    response = client.get('/api/games')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['games']) > 0
