# AppleTrader Pro - Subscription Management System

Complete subscription and plan management system with cancellation capabilities for AppleTrader Pro.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Subscription Plans](#subscription-plans)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Plan Cancellation](#plan-cancellation)
- [UI Components](#ui-components)
- [Email Notifications](#email-notifications)
- [Testing](#testing)

---

## 🎯 Overview

The subscription management system provides a complete solution for managing user subscriptions, payments, and plan cancellations in AppleTrader Pro. It includes:

- **Backend API**: FastAPI-based REST API for subscription management
- **Database Models**: SQLAlchemy models for users, subscriptions, and payments
- **Stripe Integration**: Full payment processing with Stripe
- **Authentication**: JWT-based user authentication
- **UI Components**: PyQt6 subscription management panel
- **Email Notifications**: Automated email notifications for subscription events
- **Plan Cancellation**: Comprehensive cancellation workflow with feedback collection

---

## ✨ Features

### Subscription Management
- ✅ Create and manage subscriptions
- ✅ Upgrade/downgrade between plans
- ✅ Cancel subscriptions (immediate or at period end)
- ✅ Reactivate canceled subscriptions
- ✅ Pause and resume subscriptions
- ✅ Usage tracking and limits

### Payment Processing
- ✅ Stripe integration for secure payments
- ✅ Support for multiple payment methods
- ✅ Automatic billing and renewals
- ✅ Prorated refunds for immediate cancellations
- ✅ Webhook handling for payment events

### User Management
- ✅ User registration and authentication
- ✅ JWT token-based authentication
- ✅ Email verification
- ✅ Password reset
- ✅ Account security features

### Plan Cancellation
- ✅ Cancel at period end (keep access)
- ✅ Cancel immediately (with prorated refund)
- ✅ Cancellation reason collection
- ✅ User feedback gathering
- ✅ Reactivation workflow

---

## 🏗️ Architecture

```
Apple/
├── backend/                         # Backend API
│   ├── main.py                      # FastAPI application
│   ├── config/
│   │   └── subscription_plans.py   # Plan configuration
│   ├── models/
│   │   ├── database.py              # Database setup
│   │   ├── user.py                  # User model
│   │   └── subscription.py          # Subscription models
│   ├── services/
│   │   ├── auth_service.py          # Authentication
│   │   ├── stripe_service.py        # Stripe integration
│   │   └── email_service.py         # Email notifications
│   ├── api/
│   │   └── subscription_routes.py   # API endpoints
│   └── requirements.txt             # Python dependencies
│
└── python/
    └── gui/
        └── subscription_panel.py    # PyQt6 subscription UI
```

---

## 💎 Subscription Plans

### Free Trial
- **Price**: $0/month
- **Trial**: 14 days
- **Features**:
  - 1 trading symbol
  - 3 trades per day
  - Basic filters and patterns
  - Fair Value Gaps analysis
  - Community support

### Basic - $49.99/month
- **Features**:
  - 3 trading symbols
  - 10 trades per day
  - All basic + advanced filters
  - All patterns
  - FVGs + Order Blocks
  - ML predictions
  - Multi-timeframe analysis
  - Email support
  - 3 years backtesting

### Pro - $149.99/month
- **Features**:
  - 10 trading symbols
  - 50 trades per day
  - All institutional filters
  - Complete SMC analysis
  - ML pattern scoring
  - Session momentum scanner
  - Order flow footprint
  - AI trade insights
  - News impact predictor
  - Priority support
  - API access
  - 5 years backtesting

### Elite - $499.99/month
- **Features**:
  - Unlimited symbols
  - Unlimited trades
  - All Pro features
  - Custom ML models
  - Dedicated support
  - 10 years backtesting

**Discounts**:
- Quarterly: 10% discount
- Annually: 17% discount

---

## 🚀 Installation

### 1. Install Backend Dependencies

```bash
cd Apple/backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file in `Apple/backend/`:

```env
# Database
DATABASE_URL=sqlite:///./appletrader.db
# For PostgreSQL: postgresql://user:password@localhost/appletrader

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SMTP Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@appletrader.com
FROM_NAME=AppleTrader Pro
```

### 3. Initialize Database

```bash
cd Apple/backend
python -c "from models.database import init_db; init_db()"
```

### 4. Start Backend Server

```bash
cd Apple/backend
python main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

---

## ⚙️ Configuration

### Stripe Setup

1. **Create Stripe Account**: https://dashboard.stripe.com/register
2. **Get API Keys**: Dashboard → Developers → API keys
3. **Create Products**: Dashboard → Products
4. **Create Price IDs** for each plan tier and billing period
5. **Update** `subscription_plans.py` with your Stripe price IDs:

```python
PLAN_PRICING: Dict[PlanTier, PlanPricing] = {
    PlanTier.BASIC: PlanPricing(
        ...
        stripe_monthly_price_id="price_YOUR_ACTUAL_PRICE_ID",
        stripe_quarterly_price_id="price_YOUR_ACTUAL_PRICE_ID",
        stripe_annual_price_id="price_YOUR_ACTUAL_PRICE_ID",
    ),
}
```

6. **Setup Webhooks**: Dashboard → Developers → Webhooks
   - Add endpoint: `https://your-domain.com/api/stripe/webhook`
   - Select events:
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

### Email Configuration

For Gmail:
1. Enable 2-factor authentication
2. Generate App Password: Google Account → Security → 2-Step Verification → App passwords
3. Use App Password in `SMTP_PASSWORD`

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/verify-email` - Verify email
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### Subscriptions
- `GET /api/subscriptions/plans` - Get all available plans
- `GET /api/subscriptions/plans/{tier}` - Get specific plan details
- `GET /api/subscriptions/compare` - Compare two plans
- `GET /api/subscriptions/current` - Get current subscription
- `GET /api/subscriptions/history` - Get subscription history
- `POST /api/subscriptions/create` - Create new subscription
- `PUT /api/subscriptions/update` - Update subscription (upgrade/downgrade)
- `POST /api/subscriptions/cancel` - Cancel subscription
- `POST /api/subscriptions/reactivate` - Reactivate canceled subscription
- `POST /api/subscriptions/pause` - Pause subscription
- `POST /api/subscriptions/resume` - Resume paused subscription
- `GET /api/subscriptions/usage` - Get usage statistics
- `POST /api/subscriptions/setup-intent` - Create Stripe Setup Intent

---

## ❌ Plan Cancellation

### Cancellation Options

#### 1. Cancel at Period End (Recommended)
- User keeps access until current billing period ends
- No refund issued
- Can be reactivated before period end
- Automatic email notification

**Example Request:**
```json
POST /api/subscriptions/cancel
{
  "immediate": false,
  "reason": "not_using",
  "feedback": "I'm not trading as much as I expected"
}
```

#### 2. Cancel Immediately
- User loses access immediately
- Prorated refund calculated and issued
- Cannot be reactivated
- Automatic email notification

**Example Request:**
```json
POST /api/subscriptions/cancel
{
  "immediate": true,
  "reason": "switching_service",
  "feedback": "Found a better alternative"
}
```

### Cancellation Reasons

- `too_expensive` - Price too high
- `missing_features` - Missing needed features
- `switching_service` - Switching to competitor
- `not_using` - Not using enough
- `technical_issues` - Technical problems
- `too_complex` - Too difficult to use
- `customer_service` - Customer service issues
- `other` - Other reason

### Reactivation

Users can reactivate subscriptions that were canceled at period end:

```json
POST /api/subscriptions/reactivate
```

---

## 🎨 UI Components

### Subscription Panel

The `SubscriptionPanel` widget provides a complete UI for subscription management:

```python
from Apple.python.gui.subscription_panel import SubscriptionPanel

# Create panel
panel = SubscriptionPanel(api_base_url="http://localhost:8000")

# Set authentication token
panel.set_auth_token("your-jwt-token")

# Load subscription data
panel.load_subscription_data()

# Listen for updates
panel.subscription_updated.connect(on_subscription_updated)
```

### Features:
- Current subscription display
- Plan comparison cards
- Cancellation dialog with:
  - Timing options (immediate vs. period end)
  - Reason selection
  - Feedback collection
  - Prorated refund calculation
- Reactivation button
- Payment method management
- Upgrade/downgrade options

---

## 📧 Email Notifications

Automated emails are sent for:

1. **Welcome Email** - New user registration
2. **Subscription Created** - New subscription activated
3. **Subscription Canceled** - Subscription canceled
4. **Subscription Reactivated** - Canceled subscription reactivated
5. **Subscription Upgraded** - Plan upgraded
6. **Payment Succeeded** - Successful payment
7. **Payment Failed** - Failed payment

### Email Service Usage

```python
from Apple.backend.services.email_service import EmailService

email_service = EmailService()

# Send cancellation email
email_service.send_subscription_canceled_email(
    user_email="user@example.com",
    username="John",
    subscription_data={
        'plan_tier': 'pro',
        'cancellation_effective_date': '2025-01-15',
        'days_remaining': 10
    },
    immediate=False
)
```

---

## 🧪 Testing

### Run Backend Tests

```bash
cd Apple/backend
pytest
```

### Test Cancellation Flow

1. **Create Test User**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

2. **Create Subscription**:
```bash
curl -X POST http://localhost:8000/api/subscriptions/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "plan_tier": "basic",
    "billing_period": "monthly",
    "payment_method_id": "pm_test_..."
  }'
```

3. **Cancel Subscription**:
```bash
curl -X POST http://localhost:8000/api/subscriptions/cancel \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "immediate": false,
    "reason": "not_using",
    "feedback": "Testing cancellation"
  }'
```

4. **Reactivate Subscription**:
```bash
curl -X POST http://localhost:8000/api/subscriptions/reactivate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Stripe Test Cards

Use Stripe test cards for testing:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Insufficient funds**: `4000 0000 0000 9995`

Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits

---

## 🔐 Security

- JWT tokens expire after 60 minutes
- Refresh tokens expire after 30 days
- Passwords hashed with bcrypt
- Account lockout after 5 failed login attempts
- Email verification required
- Stripe handles all payment data (PCI compliant)
- Webhook signature verification
- SQL injection protection with SQLAlchemy
- CORS configuration for API

---

## 📊 Database Schema

### Users Table
- User authentication and profile
- Stripe customer ID
- MT5 account integration
- Security features (2FA, email verification)

### Subscriptions Table
- Plan tier and billing period
- Status and dates
- Stripe integration
- Cancellation information
- Usage tracking

### Subscription History Table
- Event tracking
- Audit trail
- Change history

### Payment Methods Table
- Stored payment methods
- Card/bank details
- Billing addresses

---

## 🤝 Integration with Existing App

To integrate with the existing AppleTrader Pro application:

1. **Add Subscription Panel to Main Window**:

```python
from Apple.python.gui.subscription_panel import SubscriptionPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create subscription panel
        self.subscription_panel = SubscriptionPanel()

        # Add to tab widget or as separate window
        self.tabs.addTab(self.subscription_panel, "Subscription")
```

2. **Start Backend Server**:

```python
import subprocess

# Start backend API in background
backend_process = subprocess.Popen([
    "python", "Apple/backend/main.py"
])
```

3. **Enforce Plan Limits**:

```python
from Apple.backend.config.subscription_plans import get_plan_features

def check_trading_limits(user):
    subscription = user.active_subscription
    if subscription:
        features = get_plan_features(subscription.plan_tier)

        # Check symbol limit
        if len(active_symbols) > features.max_symbols:
            raise Exception("Symbol limit exceeded for your plan")

        # Check daily trades
        if trades_today >= features.max_daily_trades:
            raise Exception("Daily trade limit reached")
```

---

## 📝 License

This subscription system is part of AppleTrader Pro.

---

## 🆘 Support

For issues or questions:
- Email: support@appletrader.com
- Documentation: `/docs`
- GitHub Issues: [Report Issue]

---

## 🎉 Summary

You now have a complete subscription management system with:

✅ 4 subscription tiers (Free, Basic, Pro, Elite)
✅ Stripe payment integration
✅ JWT authentication
✅ Plan cancellation with feedback
✅ Prorated refunds
✅ Email notifications
✅ PyQt6 UI components
✅ RESTful API
✅ Database models
✅ Comprehensive documentation

The system is production-ready and fully integrated with AppleTrader Pro!
