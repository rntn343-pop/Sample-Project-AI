from __future__ import annotations

import re
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User
from ..security import hash_password, is_valid_username, verify_password

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def create_user(db: Session, username: str, email: str, password: str) -> User:
    username = username.strip()
    email = email.strip().lower()
    if not is_valid_username(username):
        raise ValueError("Username must be 3-50 characters and contain only letters, numbers, '.', '_' or '-'.")
    if not EMAIL_RE.match(email):
        raise ValueError("Enter a valid email address.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    existing_username = db.scalar(select(User).where(User.username == username))
    if existing_username:
        raise ValueError("Username is already registered.")
    existing_email = db.scalar(select(User).where(User.email == email))
    if existing_email:
        raise ValueError("Email is already registered.")
    user = User(username=username, email=email, password_hash=hash_password(password), session_data={})
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.username == username.strip()))
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
