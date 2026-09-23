import pytest
from app import app
from utils.database import register_user

@pytest.fixture
def client():
    """Sets up a Flask test client with clean session testing."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_home_page_public(client):
    """Test that the public landing page loads without authentication (HTTP 200)."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"OptiCrop" in rv.data

def test_unauthenticated_protected_routes_redirect(client):
    """Test that accessing protected features without login redirects to /login."""
    protected_routes = ['/predict', '/dashboard', '/history', '/profile']
    for route in protected_routes:
        rv = client.get(route)
        assert rv.status_code == 302
        assert "/login" in rv.headers["Location"]

def test_signup_flow(client):
    """Test user signup via web form."""
    rv = client.post('/signup', data=dict(
        name="Web Farmer",
        email="web_farmer_signup@opticrop.io",
        password="secretpassword123",
        confirm_password="secretpassword123",
        farm_name="Web Valley"
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b"Crop Recommendation Engine" in rv.data
    assert b"Web Farmer" in rv.data

def test_signup_password_mismatch(client):
    """Test signup fails when passwords do not match."""
    rv = client.post('/signup', data=dict(
        name="Mismatch Farmer",
        email="mismatch@opticrop.io",
        password="password123",
        confirm_password="different_password",
        farm_name="Farm"
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b"Passwords do not match" in rv.data

def test_login_flow(client):
    """Test login with valid credentials."""
    # Register user first
    register_user("Login Test User", "login_test@opticrop.io", "loginpass123")

    rv = client.post('/login', data=dict(
        email="login_test@opticrop.io",
        password="loginpass123"
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b"Crop Recommendation Engine" in rv.data
    assert b"Login Test User" in rv.data

def test_login_invalid_credentials(client):
    """Test login with invalid password."""
    rv = client.post('/login', data=dict(
        email="login_test@opticrop.io",
        password="wrong_password"
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b"Invalid email or password" in rv.data

def test_authenticated_predict_flow(client):
    """Test authenticated user submitting prediction."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_session_1'
        sess['user_name'] = 'Session User'
        sess['user_email'] = 'session_user@opticrop.io'

    rv = client.post('/predict', data=dict(
        N=90, P=42, K=43, temperature=20.8, humidity=82.0, ph=6.5, rainfall=202.9,
        farm_name="Session Farm", farmer_name="Session Farmer"
    ))
    assert rv.status_code == 200
    assert b"The Best Crop to Cultivate is" in rv.data
    assert b"rice" in rv.data.lower()

def test_logout_clears_session(client):
    """Test that logout invalidates session and redirects to /login."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'logged_in_user'

    rv = client.get('/logout', follow_redirects=True)
    assert rv.status_code == 200
    assert b"Welcome back" in rv.data or b"Welcome Back" in rv.data or b"Log in" in rv.data

    # Now verify /predict redirects to login
    rv2 = client.get('/predict')
    assert rv2.status_code == 302
    assert "/login" in rv2.headers["Location"]

def test_404_error(client):
    """Test custom 404 error page."""
    rv = client.get('/non-existent-page-url')
    assert rv.status_code == 404
    assert b"Oops! This page has gone to seed." in rv.data


def test_google_auth_routes(client):
    """Test that /auth/google redirects and /auth/google/dev-preview renders."""
    rv = client.get('/auth/google', follow_redirects=True)
    assert rv.status_code == 200
    assert b"Google" in rv.data

    rv_preview = client.get('/auth/google/dev-preview')
    assert rv_preview.status_code == 200
    assert b"Google OAuth Configuration" in rv_preview.data


def test_google_dev_mock_login(client):
    """Test mock Google sign-in creates session and unlocks protected features."""
    rv = client.post('/auth/google/dev-mock-login', data=dict(
        name="Test Google Farmer",
        email="test_google_integration@gmail.com"
    ), follow_redirects=True)
    assert rv.status_code == 200
    assert b"Signed in with Google" in rv.data

    # Verify session is established by accessing /predict
    rv_predict = client.get('/predict')
    assert rv_predict.status_code == 200


def test_forgot_password_and_reset_flow(client):
    """Test complete forgot password and reset token web flow."""
    # Register user first
    email = "forgot_pwd_web@opticrop.io"
    register_user("Forgot Farmer", email, "OldPassword123")

    # Access forgot password page
    rv_get = client.get('/forgot-password')
    assert rv_get.status_code == 200
    assert b"Reset Password" in rv_get.data
    assert b"Google" in rv_get.data

    # Submit email to get reset link
    rv_post = client.post('/forgot-password', data=dict(email=email))
    assert rv_post.status_code == 200
    assert b"Password recovery link generated" in rv_post.data

    # Generate token to test reset page
    from utils.database import generate_password_reset_token
    token, _ = generate_password_reset_token(email)
    assert token is not None

    # Visit reset password page
    rv_reset_page = client.get(f'/reset-password/{token}')
    assert rv_reset_page.status_code == 200
    assert b"Set New Password" in rv_reset_page.data

    # Submit new password
    rv_reset_submit = client.post(f'/reset-password/{token}', data=dict(
        password="BrandNewPassword789!",
        confirm_password="BrandNewPassword789!"
    ), follow_redirects=True)
    assert rv_reset_submit.status_code == 200
    assert b"Password reset successfully" in rv_reset_submit.data

