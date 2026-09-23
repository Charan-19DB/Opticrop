import os
import pytest
from utils.database import (
    init_db, register_user, authenticate_user, get_user_by_id, get_user_stats,
    add_prediction, get_predictions, delete_prediction, clear_predictions,
    save_farm_plot, get_farm_plots, save_chat_message, get_chat_history,
    get_or_create_google_user, generate_password_reset_token, verify_and_reset_password
)


def test_user_registration_and_hashing():
    """Test user sign up with encrypted password storage."""
    email = "test_user_alpha@opticrop.io"
    user = register_user(
        name="Alpha Farmer",
        email=email,
        password="SecurePassword123!",
        farm_name="Alpha Acres"
    )
    assert user is not None
    assert user["email"] == email
    assert user["name"] == "Alpha Farmer"
    assert "password_hash" not in user  # Plain/hashed password not exposed in returned dict

def test_duplicate_user_rejection():
    """Test duplicate account registration is rejected."""
    email = "test_duplicate@opticrop.io"
    register_user(name="Original User", email=email, password="password123")
    
    with pytest.raises(ValueError, match="already exists"):
        register_user(name="Duplicate User", email=email, password="password456")

def test_user_authentication():
    """Test login verification with valid and invalid passwords."""
    email = "test_auth_check@opticrop.io"
    register_user(name="Auth Check", email=email, password="MySecretPassword123")

    # Valid login
    user = authenticate_user(email, "MySecretPassword123")
    assert user is not None
    assert user["email"] == email

    # Invalid login - wrong password
    invalid_user = authenticate_user(email, "WrongPassword")
    assert invalid_user is None

    # Invalid login - non-existent user
    non_existent = authenticate_user("nobody@opticrop.io", "SomePassword")
    assert non_existent is None

def test_user_data_isolation_predictions():
    """Test that predictions made by User A are invisible to and cannot be deleted by User B."""
    user_a = register_user("User A", "user_a_isolation@opticrop.io", "passwordA123")
    user_b = register_user("User B", "user_b_isolation@opticrop.io", "passwordB123")

    # User A adds a prediction
    pred_id = add_prediction(
        N=90, P=42, K=43, temperature=24.0, humidity=80.0,
        ph=6.5, rainfall=200.0, predicted_crop='rice',
        confidence=95.0, farm_name="User A Farm", user_id=user_a["id"]
    )

    # User A can see their prediction
    preds_a = get_predictions(user_id=user_a["id"])
    assert any(p["farm_name"] == "User A Farm" for p in preds_a)

    # User B CANNOT see User A's prediction
    preds_b = get_predictions(user_id=user_b["id"])
    assert not any(p["farm_name"] == "User A Farm" for p in preds_b)

    # User B CANNOT delete User A's prediction
    delete_result = delete_prediction(pred_id, user_id=user_b["id"])
    assert delete_result is False

    # User A CAN delete their own prediction
    delete_a_result = delete_prediction(pred_id, user_id=user_a["id"])
    assert delete_a_result is True

def test_user_data_isolation_farm_plots():
    """Test that saved farm presets are isolated per user."""
    user_a = register_user("User Plot A", "user_plot_a@opticrop.io", "passwordPlot1")
    user_b = register_user("User Plot B", "user_plot_b@opticrop.io", "passwordPlot2")

    save_farm_plot(
        user_id=user_a["id"], plot_name="Private Acre A", farmer_name="Owner A",
        N=50, P=40, K=30, temperature=25.0, humidity=70.0, ph=6.5, rainfall=120.0
    )

    plots_a = get_farm_plots(user_id=user_a["id"])
    assert any(p["plot_name"] == "Private Acre A" for p in plots_a)

    plots_b = get_farm_plots(user_id=user_b["id"])
    assert not any(p["plot_name"] == "Private Acre A" for p in plots_b)

def test_user_data_isolation_chat_memory():
    """Test that OptiBot chat history is strictly scoped to the user."""
    user_a = register_user("User Chat A", "user_chat_a@opticrop.io", "passwordChat1")
    user_b = register_user("User Chat B", "user_chat_b@opticrop.io", "passwordChat2")

    save_chat_message(user_id=user_a["id"], session_id="session_101", role="user", content="User A secret query")
    save_chat_message(user_id=user_b["id"], session_id="session_101", role="user", content="User B query")

    chat_a = get_chat_history(user_id=user_a["id"], session_id="session_101")
    contents_a = [m["content"] for m in chat_a]
    assert "User A secret query" in contents_a
    assert "User B query" not in contents_a

    chat_b = get_chat_history(user_id=user_b["id"], session_id="session_101")
    contents_b = [m["content"] for m in chat_b]
    assert "User B query" in contents_b
    assert "User A secret query" not in contents_b


def test_google_user_creation_and_linking():
    """Test creating and linking a Google OAuth authenticated user."""
    email = "google_farmer_unique@gmail.com"
    user = get_or_create_google_user(
        email=email,
        name="Google Farmer",
        google_id="gid_123456789",
        avatar_url="https://example.com/photo.jpg"
    )
    assert user is not None
    assert user["email"] == email
    assert user["auth_provider"] == "google"
    assert user["google_id"] == "gid_123456789"

    # Subsequent login links and updates last_login
    user_again = get_or_create_google_user(
        email=email,
        name="Google Farmer Updated",
        google_id="gid_123456789",
        avatar_url="https://example.com/new_photo.jpg"
    )
    assert user_again["id"] == user["id"]
    assert user_again["email"] == email


def test_password_reset_token_flow():
    """Test generating a reset token and resetting a user's password."""
    email = "reset_user_test@opticrop.io"
    user = register_user(name="Reset User", email=email, password="InitialPassword123")
    assert user is not None

    # Generate token
    token, info = generate_password_reset_token(email)
    assert token is not None
    assert info["email"] == email

    # Non-existent user returns None
    invalid_token, no_info = generate_password_reset_token("nonexistent_user@opticrop.io")
    assert invalid_token is None

    # Reset password with valid token
    success, msg = verify_and_reset_password(token, "NewSecurePassword456!")
    assert success is True

    # User can now authenticate with the new password
    auth_new = authenticate_user(email, "NewSecurePassword456!")
    assert auth_new is not None
    assert auth_new["email"] == email

    # Old password no longer works
    auth_old = authenticate_user(email, "InitialPassword123")
    assert auth_old is None

    # Used token cannot be reused
    reused_success, reused_msg = verify_and_reset_password(token, "AnotherPassword789!")
    assert reused_success is False

