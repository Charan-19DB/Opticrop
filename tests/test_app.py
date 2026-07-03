import pytest
from app import app

@pytest.fixture
def client():
    """Sets up a Flask test client for mimicking HTTP requests."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test if the home page loads successfully (HTTP 200)."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"OptiCrop" in rv.data

def test_predict_get(client):
    """Test if the prediction form renders correctly."""
    rv = client.get('/predict')
    assert rv.status_code == 200
    assert b"Crop Recommendation Engine" in rv.data

def test_predict_post_valid(client):
    """Test a valid form submission to the /predict route."""
    rv = client.post('/predict', data=dict(
        N=90, P=42, K=43, temperature=20.8, humidity=82.0, ph=6.5, rainfall=202.9
    ))
    assert rv.status_code == 200
    assert b"The Best Crop to Cultivate is" in rv.data

def test_predict_post_invalid(client):
    """Test form submission with missing/invalid inputs (should flash error and redirect)."""
    rv = client.post('/predict', data=dict(
        N="ninety", P=42, K=43, temperature=20.8, humidity=82.0, ph=6.5, rainfall=202.9
    ))
    # Flask redirect status code is 302
    assert rv.status_code == 302
    
def test_dashboard_page(client):
    """Test if the dashboard loads data correctly."""
    rv = client.get('/dashboard')
    assert rv.status_code == 200
    assert b"Visualization Dashboard" in rv.data

def test_404_error(client):
    """Test the custom 404 error handler."""
    rv = client.get('/this-route-does-not-exist')
    assert rv.status_code == 404
    assert b"Oops! This page has gone to seed." in rv.data
