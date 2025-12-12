"""
AppleTrader Pro - User Model
User account management with authentication
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from .database import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    User model for authentication and account management
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Profile Information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Trading Profile
    mt5_login = Column(Integer, nullable=True)
    mt5_server = Column(String(100), nullable=True)
    mt5_broker = Column(String(100), nullable=True)
    preferred_symbols = Column(Text, nullable=True)  # JSON array of symbols
    timezone = Column(String(50), default="UTC", nullable=False)

    # Security & Verification
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    two_factor_secret = Column(String(255), nullable=True)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)

    # Usage Tracking
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Stripe Integration
    stripe_customer_id = Column(String(255), unique=True, nullable=True)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payment_methods = relationship("PaymentMethod", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Hash and set user password"""
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.hashed_password)

    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def increment_failed_login(self):
        """Increment failed login attempts and lock if necessary"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)

    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None

    def record_login(self):
        """Record successful login"""
        self.last_login = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.login_count += 1
        self.reset_failed_login()

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def active_subscription(self) -> Optional['Subscription']:
        """Get user's active subscription (if any)"""
        for sub in self.subscriptions:
            if sub.is_active():
                return sub
        return None

    @property
    def current_plan_tier(self) -> str:
        """Get user's current plan tier"""
        sub = self.active_subscription
        if sub:
            return sub.plan_tier
        return "free"

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'timezone': self.timezone,
            'current_plan_tier': self.current_plan_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

        if include_sensitive:
            data.update({
                'mt5_login': self.mt5_login,
                'mt5_server': self.mt5_server,
                'mt5_broker': self.mt5_broker,
                'preferred_symbols': self.preferred_symbols,
                'stripe_customer_id': self.stripe_customer_id,
                'two_factor_enabled': self.two_factor_enabled,
            })

        return data

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
