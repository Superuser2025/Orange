"""
AppleTrader Pro - Subscription API Routes
RESTful API endpoints for subscription management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..models.database import get_db
from ..models.user import User
from ..models.subscription import Subscription, CancellationReason
from ..services.auth_service import AuthService
from ..services.stripe_service import StripeService
from ..config.subscription_plans import PlanTier, BillingPeriod, get_all_plans, get_plan_features, compare_plans

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


# Request/Response Models
class CreateSubscriptionRequest(BaseModel):
    plan_tier: str = Field(..., description="Plan tier: free, basic, pro, elite")
    billing_period: str = Field(..., description="Billing period: monthly, quarterly, annually")
    payment_method_id: Optional[str] = Field(None, description="Stripe payment method ID")
    trial_days: int = Field(0, description="Number of trial days")


class UpdateSubscriptionRequest(BaseModel):
    plan_tier: str = Field(..., description="New plan tier")
    billing_period: Optional[str] = Field(None, description="New billing period (optional)")


class CancelSubscriptionRequest(BaseModel):
    immediate: bool = Field(False, description="Cancel immediately or at period end")
    reason: Optional[str] = Field(None, description="Cancellation reason")
    feedback: Optional[str] = Field(None, description="Additional feedback")


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_tier: str
    billing_period: str
    status: str
    amount: float
    currency: str
    is_active: bool
    is_trial: bool
    current_period_start: Optional[str]
    current_period_end: Optional[str]
    trial_end: Optional[str]
    cancel_at_period_end: bool
    canceled_at: Optional[str]
    cancellation_effective_date: Optional[str]
    days_remaining: int
    days_until_renewal: int
    next_billing_date: Optional[str]
    auto_renew: bool


class PlanComparisonResponse(BaseModel):
    is_upgrade: bool
    price_change: float
    added_features: List[str]
    removed_features: List[str]
    current_tier: str
    new_tier: str


# Dependency to get current user from token
async def get_current_user(
    token: str = Depends(lambda: None),  # Will be extracted from Authorization header
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    # In production, extract token from Authorization header
    # For now, this is a placeholder
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return AuthService.get_current_user(db, token)


@router.get("/plans", summary="Get all available subscription plans")
async def get_subscription_plans():
    """
    Get all available subscription plans with features and pricing
    """
    return {
        'success': True,
        'plans': get_all_plans()
    }


@router.get("/plans/{tier}", summary="Get specific plan details")
async def get_plan_details(tier: str):
    """
    Get details for a specific plan tier
    """
    try:
        plan_tier = PlanTier(tier.lower())
        features = get_plan_features(plan_tier)
        from ..config.subscription_plans import get_plan_pricing
        pricing = get_plan_pricing(plan_tier)

        return {
            'success': True,
            'plan': {
                'tier': plan_tier.value,
                'pricing': {
                    'name': pricing.name,
                    'description': pricing.description,
                    'monthly_price': pricing.monthly_price,
                    'quarterly_price': pricing.quarterly_price,
                    'annual_price': pricing.annual_price,
                    'quarterly_discount': pricing.quarterly_discount_pct,
                    'annual_discount': pricing.annual_discount_pct,
                    'currency': pricing.currency,
                },
                'features': features.__dict__,
            }
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan tier '{tier}' not found"
        )


@router.get("/compare", summary="Compare two subscription plans")
async def compare_subscription_plans(
    current_tier: str = Query(..., description="Current plan tier"),
    new_tier: str = Query(..., description="New plan tier to compare")
):
    """
    Compare two subscription plans and show differences
    """
    try:
        current = PlanTier(current_tier.lower())
        new = PlanTier(new_tier.lower())
        comparison = compare_plans(current, new)

        return {
            'success': True,
            'comparison': comparison
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid plan tier: {str(e)}"
        )


@router.get("/current", summary="Get current user's subscription")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's active subscription
    """
    subscription = current_user.active_subscription

    if not subscription:
        return {
            'success': True,
            'subscription': None,
            'message': 'No active subscription'
        }

    return {
        'success': True,
        'subscription': subscription.to_dict()
    }


@router.get("/history", summary="Get subscription history")
async def get_subscription_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's subscription history
    """
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).order_by(Subscription.created_at.desc()).all()

    return {
        'success': True,
        'subscriptions': [sub.to_dict() for sub in subscriptions]
    }


@router.post("/create", summary="Create new subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new subscription for user
    """
    try:
        # Validate plan tier and billing period
        plan_tier = PlanTier(request.plan_tier.lower())
        billing_period = BillingPeriod(request.billing_period.lower())

        # Check if user already has active subscription
        if current_user.active_subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active subscription. Please cancel or upgrade existing subscription."
            )

        # Create subscription
        subscription = StripeService.create_subscription(
            user=current_user,
            plan_tier=plan_tier,
            billing_period=billing_period,
            payment_method_id=request.payment_method_id,
            db=db,
            trial_days=request.trial_days
        )

        return {
            'success': True,
            'subscription': subscription.to_dict(),
            'message': 'Subscription created successfully'
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )


@router.put("/update", summary="Update subscription (upgrade/downgrade)")
async def update_subscription(
    request: UpdateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's subscription (upgrade or downgrade)
    """
    try:
        # Get current subscription
        subscription = current_user.active_subscription
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )

        # Validate new plan
        new_plan_tier = PlanTier(request.plan_tier.lower())
        new_billing_period = BillingPeriod(request.billing_period.lower()) if request.billing_period else None

        # Update subscription
        updated_subscription = StripeService.update_subscription(
            subscription=subscription,
            new_plan_tier=new_plan_tier,
            new_billing_period=new_billing_period,
            db=db
        )

        return {
            'success': True,
            'subscription': updated_subscription.to_dict(),
            'message': 'Subscription updated successfully'
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )


@router.post("/cancel", summary="Cancel subscription")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's subscription

    - Set immediate=False to cancel at period end (default)
    - Set immediate=True to cancel immediately with prorated refund
    """
    # Get current subscription
    subscription = current_user.active_subscription
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription to cancel"
        )

    # Check if already canceled
    if subscription.status == "canceled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription is already canceled"
        )

    # Cancel subscription
    result = StripeService.cancel_subscription(
        subscription=subscription,
        db=db,
        immediate=request.immediate,
        reason=request.reason,
        feedback=request.feedback
    )

    return {
        'success': True,
        'cancellation': result,
        'message': f"Subscription {'canceled immediately' if request.immediate else 'will be canceled at period end'}",
        'subscription': subscription.to_dict()
    }


@router.post("/reactivate", summary="Reactivate canceled subscription")
async def reactivate_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reactivate a subscription that was scheduled to be canceled at period end
    """
    # Get current subscription
    subscription = current_user.active_subscription
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    # Reactivate subscription
    result = StripeService.reactivate_subscription(
        subscription=subscription,
        db=db
    )

    return {
        'success': True,
        'reactivation': result,
        'message': 'Subscription reactivated successfully',
        'subscription': subscription.to_dict()
    }


@router.post("/pause", summary="Pause subscription")
async def pause_subscription(
    resume_date: Optional[str] = Body(None, description="Date to resume subscription (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pause subscription temporarily
    """
    subscription = current_user.active_subscription
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    from datetime import datetime
    resume_datetime = datetime.fromisoformat(resume_date) if resume_date else None

    subscription.pause(resume_date=resume_datetime)
    db.commit()

    return {
        'success': True,
        'message': 'Subscription paused successfully',
        'subscription': subscription.to_dict()
    }


@router.post("/resume", summary="Resume paused subscription")
async def resume_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resume a paused subscription
    """
    subscription = current_user.active_subscription
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    success = subscription.resume()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription is not paused"
        )

    db.commit()

    return {
        'success': True,
        'message': 'Subscription resumed successfully',
        'subscription': subscription.to_dict()
    }


@router.get("/usage", summary="Get subscription usage statistics")
async def get_subscription_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current subscription usage and limits
    """
    subscription = current_user.active_subscription
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    features = get_plan_features(PlanTier(subscription.plan_tier))

    return {
        'success': True,
        'usage': {
            'trades_this_month': subscription.trades_this_month,
            'trades_limit': features.max_daily_trades * 30,  # Approximate monthly limit
            'api_calls_used': subscription.api_calls_used,
            'api_calls_limit': subscription.api_calls_limit,
            'max_symbols': features.max_symbols,
            'max_position_size': features.max_position_size,
        },
        'limits': {
            'trades_remaining': (features.max_daily_trades * 30) - subscription.trades_this_month,
            'api_calls_remaining': subscription.api_calls_limit - subscription.api_calls_used if subscription.api_calls_limit else None,
        }
    }


@router.post("/setup-intent", summary="Create Stripe Setup Intent for payment method")
async def create_setup_intent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe Setup Intent for adding a payment method
    """
    result = StripeService.create_setup_intent(current_user, db)

    return {
        'success': True,
        'setup_intent': result
    }
