"""
AppleTrader Pro - Subscription Models
Subscription, payment, and billing history management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .database import Base


class SubscriptionStatus(str, Enum):
    """Subscription status values"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAUSED = "paused"


class CancellationReason(str, Enum):
    """Reasons for subscription cancellation"""
    TOO_EXPENSIVE = "too_expensive"
    MISSING_FEATURES = "missing_features"
    SWITCHING_SERVICE = "switching_service"
    LOW_QUALITY = "low_quality"
    TOO_COMPLEX = "too_complex"
    NOT_USING = "not_using"
    TECHNICAL_ISSUES = "technical_issues"
    CUSTOMER_SERVICE = "customer_service"
    OTHER = "other"


class Subscription(Base):
    """
    Subscription model for managing user subscriptions
    """
    __tablename__ = "subscriptions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key to User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Plan Information
    plan_tier = Column(String(50), nullable=False)  # free, basic, pro, elite
    billing_period = Column(String(50), nullable=False)  # monthly, quarterly, annually

    # Status
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)

    # Stripe Integration
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_price_id = Column(String(255), nullable=True)
    stripe_latest_invoice_id = Column(String(255), nullable=True)

    # Billing Cycle
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(SQLEnum(CancellationReason), nullable=True)
    cancellation_feedback = Column(Text, nullable=True)
    cancellation_effective_date = Column(DateTime, nullable=True)

    # Pricing
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    discount_percent = Column(Float, default=0.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)

    # Renewal
    auto_renew = Column(Boolean, default=True, nullable=False)
    next_billing_date = Column(DateTime, nullable=True)

    # Usage Tracking
    api_calls_used = Column(Integer, default=0, nullable=False)
    api_calls_limit = Column(Integer, nullable=True)
    trades_this_month = Column(Integer, default=0, nullable=False)
    trades_limit = Column(Integer, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    history = relationship("SubscriptionHistory", back_populates="subscription", cascade="all, delete-orphan")

    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
            return False

        # Check if subscription has ended
        if self.ended_at and datetime.utcnow() > self.ended_at:
            return False

        # Check if current period has expired
        if datetime.utcnow() > self.current_period_end:
            return False

        return True

    def is_trial(self) -> bool:
        """Check if subscription is in trial period"""
        if self.status != SubscriptionStatus.TRIALING:
            return False
        if not self.trial_end:
            return False
        return datetime.utcnow() < self.trial_end

    def days_until_renewal(self) -> int:
        """Calculate days until next renewal"""
        if not self.next_billing_date:
            return 0
        delta = self.next_billing_date - datetime.utcnow()
        return max(0, delta.days)

    def days_in_current_period(self) -> int:
        """Calculate total days in current billing period"""
        delta = self.current_period_end - self.current_period_start
        return delta.days

    def days_remaining_in_period(self) -> int:
        """Calculate days remaining in current billing period"""
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)

    def cancel(self, reason: CancellationReason = None, feedback: str = None, immediate: bool = False):
        """
        Cancel subscription

        Args:
            reason: Reason for cancellation
            feedback: Additional feedback from user
            immediate: If True, cancel immediately; if False, cancel at period end
        """
        self.canceled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.cancellation_feedback = feedback

        if immediate:
            # Cancel immediately
            self.status = SubscriptionStatus.CANCELED
            self.ended_at = datetime.utcnow()
            self.cancellation_effective_date = datetime.utcnow()
            self.auto_renew = False
        else:
            # Cancel at period end
            self.cancel_at_period_end = True
            self.cancellation_effective_date = self.current_period_end
            self.auto_renew = False

        # Record in history
        self._record_history(
            event_type="cancellation_requested",
            description=f"Subscription cancellation requested ({'immediate' if immediate else 'at period end'})"
        )

    def reactivate(self):
        """Reactivate a canceled subscription"""
        if self.status == SubscriptionStatus.CANCELED and self.cancel_at_period_end:
            self.cancel_at_period_end = False
            self.canceled_at = None
            self.cancellation_reason = None
            self.cancellation_feedback = None
            self.cancellation_effective_date = None
            self.auto_renew = True
            self.status = SubscriptionStatus.ACTIVE

            self._record_history(
                event_type="reactivation",
                description="Subscription reactivated"
            )
            return True
        return False

    def pause(self, resume_date: datetime = None):
        """Pause subscription"""
        self.status = SubscriptionStatus.PAUSED
        if resume_date:
            self.next_billing_date = resume_date

        self._record_history(
            event_type="paused",
            description=f"Subscription paused until {resume_date.isoformat() if resume_date else 'manually resumed'}"
        )

    def resume(self):
        """Resume paused subscription"""
        if self.status == SubscriptionStatus.PAUSED:
            self.status = SubscriptionStatus.ACTIVE
            self._record_history(
                event_type="resumed",
                description="Subscription resumed"
            )
            return True
        return False

    def upgrade(self, new_plan_tier: str, new_billing_period: str = None):
        """Upgrade subscription to a higher tier"""
        old_tier = self.plan_tier
        self.plan_tier = new_plan_tier
        if new_billing_period:
            self.billing_period = new_billing_period

        self._record_history(
            event_type="upgrade",
            description=f"Upgraded from {old_tier} to {new_plan_tier}"
        )

    def downgrade(self, new_plan_tier: str, new_billing_period: str = None):
        """Downgrade subscription to a lower tier"""
        old_tier = self.plan_tier
        self.plan_tier = new_plan_tier
        if new_billing_period:
            self.billing_period = new_billing_period

        self._record_history(
            event_type="downgrade",
            description=f"Downgraded from {old_tier} to {new_plan_tier}"
        )

    def renew(self):
        """Renew subscription for next period"""
        # Calculate next period based on billing period
        if self.billing_period == "monthly":
            days = 30
        elif self.billing_period == "quarterly":
            days = 90
        else:  # annually
            days = 365

        self.current_period_start = self.current_period_end
        self.current_period_end = self.current_period_end + timedelta(days=days)
        self.next_billing_date = self.current_period_end

        # Reset monthly usage counters
        self.trades_this_month = 0
        self.api_calls_used = 0

        self._record_history(
            event_type="renewal",
            description=f"Subscription renewed for {self.billing_period} period"
        )

    def _record_history(self, event_type: str, description: str):
        """Record subscription event in history"""
        history_entry = SubscriptionHistory(
            subscription_id=self.id,
            event_type=event_type,
            plan_tier=self.plan_tier,
            billing_period=self.billing_period,
            amount=self.amount,
            status=self.status.value if isinstance(self.status, Enum) else self.status,
            description=description
        )
        self.history.append(history_entry)

    def calculate_prorated_refund(self) -> float:
        """Calculate prorated refund amount for immediate cancellation"""
        if not self.is_active():
            return 0.0

        days_used = (datetime.utcnow() - self.current_period_start).days
        total_days = self.days_in_current_period()
        days_remaining = total_days - days_used

        if days_remaining <= 0:
            return 0.0

        # Calculate prorated amount
        daily_rate = self.amount / total_days
        refund_amount = daily_rate * days_remaining

        return round(refund_amount, 2)

    def to_dict(self) -> Dict:
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_tier': self.plan_tier,
            'billing_period': self.billing_period,
            'status': self.status.value if isinstance(self.status, Enum) else self.status,
            'amount': self.amount,
            'currency': self.currency,
            'is_active': self.is_active(),
            'is_trial': self.is_trial(),
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'trial_end': self.trial_end.isoformat() if self.trial_end else None,
            'cancel_at_period_end': self.cancel_at_period_end,
            'canceled_at': self.canceled_at.isoformat() if self.canceled_at else None,
            'cancellation_effective_date': self.cancellation_effective_date.isoformat() if self.cancellation_effective_date else None,
            'days_remaining': self.days_remaining_in_period(),
            'days_until_renewal': self.days_until_renewal(),
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'auto_renew': self.auto_renew,
            'started_at': self.started_at.isoformat() if self.started_at else None,
        }

    def __repr__(self):
        return f"<Subscription {self.plan_tier} ({self.status})>"


class SubscriptionHistory(Base):
    """
    Subscription history for tracking all subscription events
    """
    __tablename__ = "subscription_history"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key to Subscription
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)

    # Event Information
    event_type = Column(String(50), nullable=False)  # created, upgraded, downgraded, canceled, renewed, etc.
    plan_tier = Column(String(50), nullable=False)
    billing_period = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="history")

    def to_dict(self) -> Dict:
        """Convert history entry to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'plan_tier': self.plan_tier,
            'billing_period': self.billing_period,
            'amount': self.amount,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<SubscriptionHistory {self.event_type} at {self.created_at}>"


class PaymentMethod(Base):
    """
    Payment method model for storing user payment information
    """
    __tablename__ = "payment_methods"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key to User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Stripe Integration
    stripe_payment_method_id = Column(String(255), unique=True, nullable=False)

    # Payment Method Details
    type = Column(String(50), nullable=False)  # card, bank_account, etc.
    is_default = Column(Boolean, default=False, nullable=False)

    # Card Information (if type is card)
    card_brand = Column(String(50), nullable=True)  # visa, mastercard, amex, etc.
    card_last4 = Column(String(4), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)

    # Bank Information (if type is bank_account)
    bank_name = Column(String(100), nullable=True)
    bank_last4 = Column(String(4), nullable=True)

    # Billing Address
    billing_name = Column(String(200), nullable=True)
    billing_email = Column(String(255), nullable=True)
    billing_address_line1 = Column(String(255), nullable=True)
    billing_address_line2 = Column(String(255), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(100), nullable=True)
    billing_postal_code = Column(String(20), nullable=True)
    billing_country = Column(String(2), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="payment_methods")

    def to_dict(self) -> Dict:
        """Convert payment method to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'is_default': self.is_default,
            'card_brand': self.card_brand,
            'card_last4': self.card_last4,
            'card_exp_month': self.card_exp_month,
            'card_exp_year': self.card_exp_year,
            'bank_name': self.bank_name,
            'bank_last4': self.bank_last4,
            'billing_name': self.billing_name,
            'billing_country': self.billing_country,
            'is_active': self.is_active,
        }

    def __repr__(self):
        if self.type == "card":
            return f"<PaymentMethod {self.card_brand} ****{self.card_last4}>"
        return f"<PaymentMethod {self.type}>"
