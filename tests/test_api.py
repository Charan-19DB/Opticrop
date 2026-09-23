import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_unauthenticated_api_predict_returns_401(client):
    """Test that unauthenticated API calls are blocked with 401 Unauthorized."""
    payload = {'N': 90, 'P': 42, 'K': 43, 'temperature': 20.8, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9}
    rv = client.post('/api/predict', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 401
    data = json.loads(rv.data)
    assert data['success'] is False

def test_authenticated_api_predict(client):
    """Test authenticated API predict call succeeds."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'api_test_user'
        sess['user_name'] = 'API Tester'

    payload = {
        'N': 90, 'P': 42, 'K': 43,
        'temperature': 20.8, 'humidity': 82.0,
        'ph': 6.5, 'rainfall': 202.9,
        'farm_name': 'API Test Farm'
    }
    rv = client.post('/api/predict', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['success'] is True
    assert data['prediction'] == 'rice'
    assert len(data['top_candidates']) == 3

def test_authenticated_api_chat(client):
    """Test OptiBot AI chat endpoint with authenticated user session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'api_chat_user'
        sess['user_name'] = 'Chat Tester'

    payload = {
        'question': 'What fertilizer should I use for Rice?',
        'current_crop': 'rice'
    }
    rv = client.post('/api/chat', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['success'] is True
    assert 'answer' in data

def test_public_api_weather(client):
    """Test public real-time weather API endpoint."""
    rv = client.get('/api/weather?lat=28.6&lon=77.2')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['success'] is True
    assert 'temperature' in data

def test_public_health_check(client):
    """Test health check returns status and database info."""
    rv = client.get('/health')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['status'] == 'healthy'
    assert 'database' in data

def test_authenticated_download_json(client):
    """Test user-scoped JSON export."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'download_user_1'

    rv = client.get('/download_json')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert isinstance(data, list)
