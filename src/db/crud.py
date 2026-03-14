"""CRUD operations for database models."""

from sqlalchemy.orm import Session
from typing import Optional
from .models import User, Conversation
from ..auth.password import hash_password


def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: str | None = None
) -> User:
    """Create a new user.

    Args:
        db: Database session
        email: User email (must be unique)
        password: Plain text password (will be hashed)
        full_name: Optional full name

    Returns:
        Created user instance
    """
    hashed_password = hash_password(password)
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email.

    Args:
        db: Database session
        email: User email

    Returns:
        User instance or None if not found
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User instance or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user(
    db: Session,
    user_id: int,
    **kwargs
) -> Optional[User]:
    """Update user fields.

    Args:
        db: Database session
        user_id: User ID
        **kwargs: Fields to update

    Returns:
        Updated user instance or None if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if deleted, False if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True
