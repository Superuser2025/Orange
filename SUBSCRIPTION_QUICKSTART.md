# 🚀 Subscription System - Quick Start Guide

Get the AppleTrader Pro subscription system up and running in 5 minutes!

## ⚡ Quick Setup

### 1. Install Dependencies

```bash
cd /home/user/Orange/Apple/backend
pip install -r requirements.txt
```

### 2. Create Environment File

Create `Apple/backend/.env`:

```env
# Database (SQLite for quick start)
DATABASE_URL=sqlite:///./appletrader.db

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=your-secret-key-here

# Stripe Test Keys (get from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_your_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email (optional for quick start)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@appletrader.com
```

### 3. Initialize Database

```bash
cd Apple/backend
python -c "from models.database import init_db; init_db()"
```

### 4. Start API Server

```bash
python main.py
```

✅ API running at `http://localhost:8000`

✅ Docs at `http://localhost:8000/docs`

---

## 🧪 Test the System

### 1. Check Health

```bash
curl http://localhost:8000/health
```

### 2. Get Available Plans

```bash
curl http://localhost:8000/api/subscriptions/plans
```

### 3. Test with UI

```python
from PyQt6.QtWidgets import QApplication
from Apple.python.gui.subscription_panel import SubscriptionPanel
import sys

app = QApplication(sys.argv)
panel = SubscriptionPanel(api_base_url="http://localhost:8000")
panel.show()
sys.exit(app.exec())
```

---

## 💳 Stripe Test Mode

Use these test cards:

| Card Number | Description |
|-------------|-------------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |
| `4000 0000 0000 9995` | Insufficient funds |

- **Expiry**: Any future date
- **CVC**: Any 3 digits
- **ZIP**: Any valid ZIP code

---

## 🎯 Common Workflows

### Create Subscription

```bash
curl -X POST http://localhost:8000/api/subscriptions/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "plan_tier": "basic",
    "billing_period": "monthly",
    "payment_method_id": "pm_test_card",
    "trial_days": 14
  }'
```

### Cancel Subscription (Keep Access)

```bash
curl -X POST http://localhost:8000/api/subscriptions/cancel \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "immediate": false,
    "reason": "not_using",
    "feedback": "Not trading enough"
  }'
```

### Cancel Immediately (With Refund)

```bash
curl -X POST http://localhost:8000/api/subscriptions/cancel \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "immediate": true,
    "reason": "too_expensive"
  }'
```

### Reactivate Subscription

```bash
curl -X POST http://localhost:8000/api/subscriptions/reactivate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📱 UI Integration

Add to your main window:

```python
from Apple.python.gui.subscription_panel import SubscriptionPanel

# In your main window __init__
self.subscription_panel = SubscriptionPanel(
    api_base_url="http://localhost:8000"
)

# Set user token after login
self.subscription_panel.set_auth_token(user_token)

# Add to your layout
self.tabs.addTab(self.subscription_panel, "💎 Subscription")

# Listen for subscription updates
self.subscription_panel.subscription_updated.connect(
    self.on_subscription_changed
)
```

---

## 🔧 Troubleshooting

### Database locked error
```bash
# Delete database and reinitialize
rm Apple/backend/appletrader.db
python -c "from models.database import init_db; init_db()"
```

### Stripe errors
- Verify `STRIPE_SECRET_KEY` starts with `sk_test_`
- Check your Stripe Dashboard for error details
- Ensure price IDs in `subscription_plans.py` match your Stripe products

### Email not sending
- Email is optional for testing
- Use Gmail App Passwords (not account password)
- Check SMTP settings for your provider

### Import errors
```bash
pip install -r Apple/backend/requirements.txt
```

---

## 🎉 Success!

You now have:

✅ Backend API running
✅ Database initialized
✅ Subscription plans configured
✅ Cancellation workflow ready
✅ UI components available

## Next Steps

1. **Configure Stripe Products**: Match your actual Stripe price IDs in `subscription_plans.py`
2. **Set up Webhooks**: Configure Stripe webhooks for production
3. **Customize Plans**: Adjust pricing and features as needed
4. **Add Authentication**: Implement user login/registration
5. **Test Cancellation Flow**: Try canceling and reactivating subscriptions

## 📚 Full Documentation

See `SUBSCRIPTION_SYSTEM.md` for complete documentation including:
- Detailed architecture
- All API endpoints
- Security features
- Production deployment
- Email notifications
- Advanced configuration

---

## 🆘 Need Help?

- **API Docs**: http://localhost:8000/docs
- **Full Documentation**: SUBSCRIPTION_SYSTEM.md
- **Stripe Docs**: https://stripe.com/docs
- **Support**: support@appletrader.com

Happy Trading! 🍎📈
