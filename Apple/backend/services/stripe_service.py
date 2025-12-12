"""
AppleTrader Pro - Stripe Integration Service
Payment processing and subscription management with Stripe
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import stripe
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user import User
from ..models.subscription import Subscription, SubscriptionStatus, PaymentMethod
from ..config.subscription_plans import PlanTier, BillingPeriod, get_plan_pricing

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


class StripeService:
    """Service for Stripe payment and subscription management"""

    @staticmethod
    def create_customer(user: User, db: Session) -> str:
        """
        Create Stripe customer for user

        Args:
            user: User object
            db: Database session

        Returns:
            Stripe customer ID
        """
        try:
            # Check if customer already exists
            if user.stripe_customer_id:
                return user.stripe_customer_id

            # Create Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    'user_id': user.id,
                    'username': user.username,
                }
            )

            # Save customer ID to user
            user.stripe_customer_id = customer.id
            db.commit()

            return customer.id

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    @staticmethod
    def create_subscription(
        user: User,
        plan_tier: PlanTier,
        billing_period: BillingPeriod,
        payment_method_id: str,
        db: Session,
        trial_days: int = 0
    ) -> Subscription:
        """
        Create new subscription for user

        Args:
            user: User object
            plan_tier: Plan tier (FREE, BASIC, PRO, ELITE)
            billing_period: Billing period (MONTHLY, QUARTERLY, ANNUALLY)
            payment_method_id: Stripe payment method ID
            db: Database session
            trial_days: Number of trial days (default: 0)

        Returns:
            Created Subscription object
        """
        try:
            # Get plan pricing
            pricing = get_plan_pricing(plan_tier)

            # Determine price based on billing period
            if billing_period == BillingPeriod.MONTHLY:
                amount = pricing.monthly_price
                price_id = pricing.stripe_monthly_price_id
            elif billing_period == BillingPeriod.QUARTERLY:
                amount = pricing.quarterly_price
                price_id = pricing.stripe_quarterly_price_id
            else:  # ANNUALLY
                amount = pricing.annual_price
                price_id = pricing.stripe_annual_price_id

            # Free plan doesn't need Stripe subscription
            if plan_tier == PlanTier.FREE:
                return StripeService._create_free_subscription(user, db)

            # Ensure user has Stripe customer
            customer_id = StripeService.create_customer(user, db)

            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )

            # Set as default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )

            # Create Stripe subscription
            stripe_sub_params = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'metadata': {
                    'user_id': user.id,
                    'plan_tier': plan_tier.value,
                    'billing_period': billing_period.value,
                }
            }

            if trial_days > 0:
                stripe_sub_params['trial_period_days'] = trial_days

            stripe_subscription = stripe.Subscription.create(**stripe_sub_params)

            # Calculate period dates
            current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
            current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)

            # Create local subscription
            subscription = Subscription(
                user_id=user.id,
                plan_tier=plan_tier.value,
                billing_period=billing_period.value,
                status=SubscriptionStatus.TRIALING if trial_days > 0 else SubscriptionStatus.ACTIVE,
                stripe_subscription_id=stripe_subscription.id,
                stripe_price_id=price_id,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                next_billing_date=current_period_end,
                amount=amount,
                currency=pricing.currency,
            )

            if trial_days > 0:
                subscription.trial_start = datetime.utcnow()
                subscription.trial_end = datetime.utcnow() + timedelta(days=trial_days)

            db.add(subscription)
            db.commit()
            db.refresh(subscription)

            # Save payment method
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            StripeService._save_payment_method(user, payment_method, db, is_default=True)

            return subscription

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    @staticmethod
    def _create_free_subscription(user: User, db: Session) -> Subscription:
        """Create free tier subscription"""
        # Set up free trial for 14 days
        trial_days = 14
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=trial_days)

        subscription = Subscription(
            user_id=user.id,
            plan_tier=PlanTier.FREE.value,
            billing_period=BillingPeriod.MONTHLY.value,
            status=SubscriptionStatus.TRIALING,
            current_period_start=start_date,
            current_period_end=end_date,
            trial_start=start_date,
            trial_end=end_date,
            next_billing_date=end_date,
            amount=0.0,
            currency="USD",
        )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        return subscription

    @staticmethod
    def cancel_subscription(
        subscription: Subscription,
        db: Session,
        immediate: bool = False,
        reason: Optional[str] = None,
        feedback: Optional[str] = None
    ) -> Dict:
        """
        Cancel subscription

        Args:
            subscription: Subscription to cancel
            db: Database session
            immediate: Cancel immediately or at period end
            reason: Cancellation reason
            feedback: User feedback

        Returns:
            Cancellation details
        """
        try:
            if subscription.stripe_subscription_id:
                # Cancel in Stripe
                if immediate:
                    # Cancel immediately with proration
                    stripe_subscription = stripe.Subscription.delete(
                        subscription.stripe_subscription_id,
                        prorate=True
                    )
                else:
                    # Cancel at period end
                    stripe_subscription = stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=True,
                        metadata={
                            'cancellation_reason': reason if reason else 'not_specified',
                            'cancellation_feedback': feedback if feedback else ''
                        }
                    )

            # Update local subscription
            from ..models.subscription import CancellationReason
            cancellation_reason = None
            if reason:
                try:
                    cancellation_reason = CancellationReason(reason)
                except ValueError:
                    cancellation_reason = CancellationReason.OTHER

            subscription.cancel(
                reason=cancellation_reason,
                feedback=feedback,
                immediate=immediate
            )

            db.commit()

            # Calculate refund if immediate
            refund_amount = 0.0
            if immediate:
                refund_amount = subscription.calculate_prorated_refund()

            return {
                'success': True,
                'subscription_id': subscription.id,
                'cancellation_type': 'immediate' if immediate else 'at_period_end',
                'effective_date': subscription.cancellation_effective_date.isoformat() if subscription.cancellation_effective_date else None,
                'refund_amount': refund_amount,
                'days_remaining': subscription.days_remaining_in_period(),
            }

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    @staticmethod
    def reactivate_subscription(subscription: Subscription, db: Session) -> Dict:
        """
        Reactivate canceled subscription

        Args:
            subscription: Subscription to reactivate
            db: Database session

        Returns:
            Reactivation details
        """
        try:
            if not subscription.cancel_at_period_end:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subscription is not scheduled for cancellation"
                )

            if subscription.stripe_subscription_id:
                # Reactivate in Stripe
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=False
                )

            # Reactivate local subscription
            success = subscription.reactivate()

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to reactivate subscription"
                )

            db.commit()

            return {
                'success': True,
                'subscription_id': subscription.id,
                'status': subscription.status.value,
                'next_billing_date': subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
            }

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    @staticmethod
    def update_subscription(
        subscription: Subscription,
        new_plan_tier: PlanTier,
        new_billing_period: Optional[BillingPeriod],
        db: Session
    ) -> Subscription:
        """
        Update subscription plan (upgrade/downgrade)

        Args:
            subscription: Current subscription
            new_plan_tier: New plan tier
            new_billing_period: New billing period (optional)
            db: Database session

        Returns:
            Updated Subscription object
        """
        try:
            # Get new pricing
            pricing = get_plan_pricing(new_plan_tier)
            billing_period = new_billing_period if new_billing_period else BillingPeriod(subscription.billing_period)

            # Determine new price
            if billing_period == BillingPeriod.MONTHLY:
                amount = pricing.monthly_price
                price_id = pricing.stripe_monthly_price_id
            elif billing_period == BillingPeriod.QUARTERLY:
                amount = pricing.quarterly_price
                price_id = pricing.stripe_quarterly_price_id
            else:
                amount = pricing.annual_price
                price_id = pricing.stripe_annual_price_id

            if subscription.stripe_subscription_id:
                # Update Stripe subscription
                stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)

                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    items=[{
                        'id': stripe_subscription['items']['data'][0].id,
                        'price': price_id,
                    }],
                    proration_behavior='always_invoice',  # Charge/credit difference immediately
                )

            # Determine if upgrade or downgrade
            tier_order = [PlanTier.FREE, PlanTier.BASIC, PlanTier.PRO, PlanTier.ELITE]
            current_idx = tier_order.index(PlanTier(subscription.plan_tier))
            new_idx = tier_order.index(new_plan_tier)

            # Update local subscription
            if new_idx > current_idx:
                subscription.upgrade(new_plan_tier.value, billing_period.value if new_billing_period else None)
            else:
                subscription.downgrade(new_plan_tier.value, billing_period.value if new_billing_period else None)

            subscription.amount = amount
            subscription.stripe_price_id = price_id

            db.commit()
            db.refresh(subscription)

            return subscription

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    @staticmethod
    def _save_payment_method(
        user: User,
        stripe_payment_method: stripe.PaymentMethod,
        db: Session,
        is_default: bool = False
    ):
        """Save payment method to database"""
        payment_method = PaymentMethod(
            user_id=user.id,
            stripe_payment_method_id=stripe_payment_method.id,
            type=stripe_payment_method.type,
            is_default=is_default,
        )

        # Save card details if type is card
        if stripe_payment_method.type == 'card':
            card = stripe_payment_method.card
            payment_method.card_brand = card.brand
            payment_method.card_last4 = card.last4
            payment_method.card_exp_month = card.exp_month
            payment_method.card_exp_year = card.exp_year

        # Save billing details
        billing = stripe_payment_method.billing_details
        if billing:
            payment_method.billing_name = billing.name
            payment_method.billing_email = billing.email
            if billing.address:
                payment_method.billing_address_line1 = billing.address.line1
                payment_method.billing_address_line2 = billing.address.line2
                payment_method.billing_city = billing.address.city
                payment_method.billing_state = billing.address.state
                payment_method.billing_postal_code = billing.address.postal_code
                payment_method.billing_country = billing.address.country

        db.add(payment_method)
        db.commit()

    @staticmethod
    def create_setup_intent(user: User, db: Session) -> Dict:
        """
        Create Stripe Setup Intent for adding payment method

        Args:
            user: User object
            db: Database session

        Returns:
            Setup intent client secret
        """
        try:
            customer_id = StripeService.create_customer(user, db)

            setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=['card'],
            )

            return {
                'client_secret': setup_intent.client_secret,
                'setup_intent_id': setup_intent.id,
            }

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    @staticmethod
    def handle_webhook(payload: bytes, sig_header: str) -> Dict:
        """
        Handle Stripe webhook event

        Args:
            payload: Request body
            sig_header: Stripe signature header

        Returns:
            Event processing result
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )

            # Handle different event types
            event_type = event['type']
            data = event['data']['object']

            if event_type == 'customer.subscription.updated':
                return StripeService._handle_subscription_updated(data)
            elif event_type == 'customer.subscription.deleted':
                return StripeService._handle_subscription_deleted(data)
            elif event_type == 'invoice.payment_succeeded':
                return StripeService._handle_invoice_paid(data)
            elif event_type == 'invoice.payment_failed':
                return StripeService._handle_invoice_failed(data)
            else:
                return {'status': 'ignored', 'event_type': event_type}

        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")

    @staticmethod
    def _handle_subscription_updated(stripe_subscription: Dict):
        """Handle subscription update webhook"""
        # Implementation would update local subscription from Stripe data
        return {'status': 'processed', 'event': 'subscription_updated'}

    @staticmethod
    def _handle_subscription_deleted(stripe_subscription: Dict):
        """Handle subscription deletion webhook"""
        # Implementation would mark local subscription as canceled
        return {'status': 'processed', 'event': 'subscription_deleted'}

    @staticmethod
    def _handle_invoice_paid(invoice: Dict):
        """Handle successful invoice payment webhook"""
        # Implementation would record payment and renew subscription
        return {'status': 'processed', 'event': 'invoice_paid'}

    @staticmethod
    def _handle_invoice_failed(invoice: Dict):
        """Handle failed invoice payment webhook"""
        # Implementation would mark subscription as past_due
        return {'status': 'processed', 'event': 'invoice_failed'}
