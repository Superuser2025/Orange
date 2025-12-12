"""
AppleTrader Pro - Authentication Service
JWT-based authentication and user session management
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.database import SessionLocal

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30


class AuthService:
    """Authentication service for user management"""

    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        """
        Create JWT refresh token

        Args:
            data: Data to encode in token

        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token to verify
            token_type: Expected token type (access or refresh)

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username/email and password

        Args:
            db: Database session
            username: Username or email
            password: User password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Try to find user by username or email
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            return None

        # Check if account is locked
        if user.is_locked():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked due to too many failed login attempts. Try again later."
            )

        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Verify password
        if not user.verify_password(password):
            user.increment_failed_login()
            db.commit()
            return None

        # Record successful login
        user.record_login()
        db.commit()

        return user

    @staticmethod
    def register_user(
        db: Session,
        email: str,
        username: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Register new user

        Args:
            db: Database session
            email: User email
            username: Username
            password: User password
            first_name: First name (optional)
            last_name: Last name (optional)

        Returns:
            Created User object

        Raises:
            HTTPException if user already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()

        if existing_user:
            if existing_user.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Create new user
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)

        # Generate email verification token
        user.email_verification_token = secrets.token_urlsafe(32)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def verify_email(db: Session, token: str) -> bool:
        """
        Verify user email with token

        Args:
            db: Database session
            token: Email verification token

        Returns:
            True if verification successful
        """
        user = db.query(User).filter(User.email_verification_token == token).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )

        user.is_verified = True
        user.email_verification_token = None
        db.commit()

        return True

    @staticmethod
    def request_password_reset(db: Session, email: str) -> str:
        """
        Request password reset for user

        Args:
            db: Database session
            email: User email

        Returns:
            Password reset token
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Don't reveal if email exists
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="If the email exists, a reset link has been sent"
            )

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)

        db.commit()

        return reset_token

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """
        Reset user password with token

        Args:
            db: Database session
            token: Password reset token
            new_password: New password

        Returns:
            True if reset successful
        """
        user = db.query(User).filter(User.password_reset_token == token).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        # Check if token expired
        if user.password_reset_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )

        # Update password
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.reset_failed_login()

        db.commit()

        return True

    @staticmethod
    def change_password(db: Session, user: User, old_password: str, new_password: str) -> bool:
        """
        Change user password

        Args:
            db: Database session
            user: User object
            old_password: Current password
            new_password: New password

        Returns:
            True if change successful
        """
        # Verify old password
        if not user.verify_password(old_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        user.set_password(new_password)
        db.commit()

        return True

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """
        Get current user from JWT token

        Args:
            db: Database session
            token: JWT access token

        Returns:
            User object

        Raises:
            HTTPException if token invalid or user not found
        """
        payload = AuthService.verify_token(token, token_type="access")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Update last activity
        user.update_activity()
        db.commit()

        return user

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> str:
        """
        Create new access token from refresh token

        Args:
            db: Database session
            refresh_token: JWT refresh token

        Returns:
            New JWT access token

        Raises:
            HTTPException if refresh token invalid
        """
        payload = AuthService.verify_token(refresh_token, token_type="refresh")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Verify user still exists and is active
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new access token
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )

        return access_token
