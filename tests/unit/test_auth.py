"""Unit tests for authentication modules."""

import pytest
from datetime import timedelta
from src.auth.password import hash_password, verify_password
from src.auth.jwt import create_access_token, verify_token


@pytest.mark.unit
def test_hash_password():
    """Test password hashing."""
    password = "testpassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 0


@pytest.mark.unit
def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "testpassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


@pytest.mark.unit
def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "testpassword123"
    hashed = hash_password(password)

    assert verify_password("wrongpassword", hashed) is False


@pytest.mark.unit
def test_password_hashing_unique():
    """Test that hashing the same password produces different hashes."""
    password = "testpassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Hashes should be different due to salt
    assert hash1 != hash2
    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


@pytest.mark.unit
def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.unit
def test_verify_token_valid():
    """Test JWT token verification with valid token."""
    data = {"sub": "test@example.com", "user_id": 123}
    token = create_access_token(data)

    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == "test@example.com"
    assert payload["user_id"] == 123
    assert "exp" in payload


@pytest.mark.unit
def test_verify_token_invalid():
    """Test JWT token verification with invalid token."""
    invalid_token = "invalid.token.here"

    payload = verify_token(invalid_token)

    assert payload is None


@pytest.mark.unit
def test_create_token_with_custom_expiration():
    """Test creating token with custom expiration."""
    data = {"sub": "test@example.com"}
    expires_delta = timedelta(minutes=60)

    token = create_access_token(data, expires_delta)

    assert token is not None
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test@example.com"


@pytest.mark.unit
def test_token_payload_isolation():
    """Test that tokens with different data are distinct."""
    token1 = create_access_token({"sub": "user1@example.com"})
    token2 = create_access_token({"sub": "user2@example.com"})

    assert token1 != token2

    payload1 = verify_token(token1)
    payload2 = verify_token(token2)

    assert payload1["sub"] == "user1@example.com"
    assert payload2["sub"] == "user2@example.com"
