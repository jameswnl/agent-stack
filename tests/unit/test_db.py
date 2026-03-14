"""Unit tests for database operations."""

import pytest
from src.db.crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
    delete_user
)
from src.db.models import User


@pytest.mark.unit
def test_create_user(db_session):
    """Test creating a user."""
    user = create_user(
        db=db_session,
        email="newuser@example.com",
        password="password123",
        full_name="New User"
    )

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.full_name == "New User"
    assert user.hashed_password != "password123"  # Should be hashed
    assert user.is_active is True
    assert user.is_superuser is False


@pytest.mark.unit
def test_get_user_by_email(db_session, test_user):
    """Test retrieving user by email."""
    user = get_user_by_email(db_session, test_user.email)

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.unit
def test_get_user_by_email_not_found(db_session):
    """Test retrieving non-existent user by email."""
    user = get_user_by_email(db_session, "nonexistent@example.com")

    assert user is None


@pytest.mark.unit
def test_get_user_by_id(db_session, test_user):
    """Test retrieving user by ID."""
    user = get_user_by_id(db_session, test_user.id)

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.unit
def test_get_user_by_id_not_found(db_session):
    """Test retrieving non-existent user by ID."""
    user = get_user_by_id(db_session, 99999)

    assert user is None


@pytest.mark.unit
def test_update_user(db_session, test_user):
    """Test updating user fields."""
    updated_user = update_user(
        db_session,
        test_user.id,
        full_name="Updated Name",
        is_active=False
    )

    assert updated_user is not None
    assert updated_user.id == test_user.id
    assert updated_user.full_name == "Updated Name"
    assert updated_user.is_active is False
    assert updated_user.email == test_user.email  # Unchanged


@pytest.mark.unit
def test_update_user_not_found(db_session):
    """Test updating non-existent user."""
    result = update_user(db_session, 99999, full_name="Test")

    assert result is None


@pytest.mark.unit
def test_delete_user(db_session, test_user):
    """Test deleting a user."""
    user_id = test_user.id

    result = delete_user(db_session, user_id)

    assert result is True

    # Verify user is deleted
    user = get_user_by_id(db_session, user_id)
    assert user is None


@pytest.mark.unit
def test_delete_user_not_found(db_session):
    """Test deleting non-existent user."""
    result = delete_user(db_session, 99999)

    assert result is False


@pytest.mark.unit
def test_user_email_unique_constraint(db_session, test_user):
    """Test that email uniqueness is enforced."""
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        create_user(
            db=db_session,
            email=test_user.email,  # Duplicate email
            password="password123"
        )
