"""
AppleTrader Pro - Email Notification Service
Send email notifications for subscription events
"""

import os
from typing import Dict, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template


class EmailService:
    """Service for sending email notifications"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@appletrader.com")
        self.from_name = os.getenv("FROM_NAME", "AppleTrader Pro")

    def send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None):
        """
        Send email via SMTP

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Attach text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            print(f"✉️ Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False

    def send_welcome_email(self, user_email: str, username: str):
        """Send welcome email to new user"""
        subject = "Welcome to AppleTrader Pro! 🎉"

        html_body = self._render_template('welcome', {
            'username': username,
        })

        text_body = f"""
        Welcome to AppleTrader Pro, {username}!

        Thank you for joining AppleTrader Pro, the institutional-grade trading platform for MetaTrader 5.

        Get started:
        - Complete your profile setup
        - Connect your MT5 account
        - Explore our trading features

        Need help? Visit our support center or contact us anytime.

        Happy trading!
        The AppleTrader Pro Team
        """

        return self.send_email(user_email, subject, html_body, text_body)

    def send_subscription_created_email(self, user_email: str, username: str, subscription_data: Dict):
        """Send email when subscription is created"""
        subject = f"Subscription Activated: {subscription_data['plan_tier'].title()} Plan"

        html_body = self._render_template('subscription_created', {
            'username': username,
            'plan_tier': subscription_data['plan_tier'].title(),
            'billing_period': subscription_data['billing_period'],
            'amount': subscription_data['amount'],
            'currency': subscription_data['currency'],
            'next_billing_date': subscription_data.get('next_billing_date', ''),
        })

        text_body = f"""
        Subscription Activated!

        Hi {username},

        Your {subscription_data['plan_tier'].title()} subscription has been activated!

        Plan: {subscription_data['plan_tier'].title()}
        Billing: ${subscription_data['amount']:.2f} {subscription_data['currency']} / {subscription_data['billing_period']}
        Next billing: {subscription_data.get('next_billing_date', 'N/A')}

        Thank you for subscribing to AppleTrader Pro!

        Best regards,
        The AppleTrader Pro Team
        """

        return self.send_email(user_email, subject, html_body, text_body)

    def send_subscription_canceled_email(
        self,
        user_email: str,
        username: str,
        subscription_data: Dict,
        immediate: bool = False
    ):
        """Send email when subscription is canceled"""
        if immediate:
            subject = "Subscription Canceled - Immediate"
        else:
            subject = "Subscription Canceled - Access Until Period End"

        html_body = self._render_template('subscription_canceled', {
            'username': username,
            'plan_tier': subscription_data['plan_tier'].title(),
            'immediate': immediate,
            'effective_date': subscription_data.get('cancellation_effective_date', ''),
            'days_remaining': subscription_data.get('days_remaining', 0),
        })

        if immediate:
            text_body = f"""
            Subscription Canceled

            Hi {username},

            Your {subscription_data['plan_tier'].title()} subscription has been canceled immediately.

            Your access to premium features has ended. We're sorry to see you go!

            If you change your mind, you can resubscribe anytime from your account dashboard.

            We'd love to hear your feedback on how we can improve.

            Best regards,
            The AppleTrader Pro Team
            """
        else:
            text_body = f"""
            Subscription Canceled - Access Until {subscription_data.get('cancellation_effective_date', 'period end')}

            Hi {username},

            Your {subscription_data['plan_tier'].title()} subscription has been scheduled for cancellation.

            You will continue to have access to premium features until {subscription_data.get('cancellation_effective_date', 'the end of your billing period')}.

            Days remaining: {subscription_data.get('days_remaining', 0)}

            If you change your mind, you can reactivate your subscription anytime before it expires.

            We'd love to hear your feedback on how we can improve.

            Best regards,
            The AppleTrader Pro Team
            """

        return self.send_email(user_email, subject, html_body, text_body)

    def send_subscription_reactivated_email(self, user_email: str, username: str, subscription_data: Dict):
        """Send email when subscription is reactivated"""
        subject = "Subscription Reactivated! 🎉"

        html_body = self._render_template('subscription_reactivated', {
            'username': username,
            'plan_tier': subscription_data['plan_tier'].title(),
            'next_billing_date': subscription_data.get('next_billing_date', ''),
        })

        text_body = f"""
        Welcome Back!

        Hi {username},

        Great news! Your {subscription_data['plan_tier'].title()} subscription has been reactivated.

        Your premium features are now available again, and your next billing date is {subscription_data.get('next_billing_date', 'TBD')}.

        We're glad to have you back!

        Best regards,
        The AppleTrader Pro Team
        """

        return self.send_email(user_email, subject, html_body, text_body)

    def send_subscription_upgraded_email(
        self,
        user_email: str,
        username: str,
        old_tier: str,
        new_tier: str,
        subscription_data: Dict
    ):
        """Send email when subscription is upgraded"""
        subject = f"Subscription Upgraded to {new_tier.title()}! 🚀"

        html_body = self._render_template('subscription_upgraded', {
            'username': username,
            'old_tier': old_tier.title(),
            'new_tier': new_tier.title(),
            'amount': subscription_data['amount'],
            'currency': subscription_data['currency'],
            'billing_period': subscription_data['billing_period'],
        })

        text_body = f"""
        Subscription Upgraded!

        Hi {username},

        Your subscription has been upgraded from {old_tier.title()} to {new_tier.title()}!

        New plan: {new_tier.title()}
        New billing: ${subscription_data['amount']:.2f} {subscription_data['currency']} / {subscription_data['billing_period']}

        Enjoy your new premium features!

        Best regards,
        The AppleTrader Pro Team
        """

        return self.send_email(user_email, subject, html_body, text_body)

    def send_payment_failed_email(self, user_email: str, username: str, amount: float, currency: str):
        """Send email when payment fails"""
        subject = "Payment Failed - Action Required ⚠️"

        html_body = self._render_template('payment_failed', {
            'username': username,
            'amount': amount,
            'currency': currency,
        })

        text_body = f"""
        Payment Failed - Action Required

        Hi {username},

        We were unable to process your payment of ${amount:.2f} {currency}.

        To continue your subscription, please update your payment method in your account settings.

        If you don't update your payment method, your subscription will be suspended.

        Need help? Contact our support team.

        Best regards,
        The AppleTrader Pro Team
        """

        return self.send_email(user_email, subject, html_body, text_body)

    def send_payment_succeeded_email(
        self,
        user_email: str,
        username: str,
        amount: float,
        currency: str,
        invoice_url: Optional[str] = None
    ):
        """Send email when payment succeeds"""
        subject = "Payment Receipt - Thank You! 💳"

        html_body = self._render_template('payment_succeeded', {
            'username': username,
            'amount': amount,
            'currency': currency,
            'invoice_url': invoice_url,
            'date': datetime.now().strftime("%B %d, %Y"),
        })

        text_body = f"""
        Payment Receipt

        Hi {username},

        Thank you for your payment!

        Amount: ${amount:.2f} {currency}
        Date: {datetime.now().strftime("%B %d, %Y")}

        {'View invoice: ' + invoice_url if invoice_url else ''}

        Thank you for being a valued AppleTrader Pro customer!

        Best regards,
        The AppleTrader Pro Team
        """

        return self.send_email(user_email, subject, html_body, text_body)

    def _render_template(self, template_name: str, context: Dict) -> str:
        """
        Render email template with context

        Args:
            template_name: Name of the template
            context: Template context data

        Returns:
            Rendered HTML
        """
        # Basic email template
        base_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }
                .container {
                    background-color: white;
                    border-radius: 8px;
                    padding: 40px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .logo {
                    font-size: 32px;
                    font-weight: bold;
                    color: #007AFF;
                }
                .content {
                    margin-bottom: 30px;
                }
                .button {
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #007AFF;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    margin: 20px 0;
                }
                .footer {
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                }
                .highlight {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🍎 AppleTrader Pro</div>
                </div>
                <div class="content">
                    {{ content }}
                </div>
                <div class="footer">
                    <p>© 2025 AppleTrader Pro. All rights reserved.</p>
                    <p>Questions? Contact us at support@appletrader.com</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Template content variations
        templates = {
            'welcome': """
                <h2>Welcome to AppleTrader Pro, {{ username }}! 🎉</h2>
                <p>Thank you for joining AppleTrader Pro, the institutional-grade trading platform for MetaTrader 5.</p>
                <p>Get started with these steps:</p>
                <ul>
                    <li>Complete your profile setup</li>
                    <li>Connect your MT5 account</li>
                    <li>Explore our advanced trading features</li>
                </ul>
                <a href="#" class="button">Get Started</a>
            """,
            'subscription_created': """
                <h2>Subscription Activated! 🎉</h2>
                <p>Hi {{ username }},</p>
                <p>Your <strong>{{ plan_tier }}</strong> subscription has been activated!</p>
                <div class="highlight">
                    <p><strong>Plan:</strong> {{ plan_tier }}</p>
                    <p><strong>Billing:</strong> ${{ amount }} {{ currency }} / {{ billing_period }}</p>
                    <p><strong>Next billing:</strong> {{ next_billing_date }}</p>
                </div>
                <p>Thank you for subscribing to AppleTrader Pro!</p>
            """,
            'subscription_canceled': """
                <h2>Subscription Canceled</h2>
                <p>Hi {{ username }},</p>
                {% if immediate %}
                <p>Your <strong>{{ plan_tier }}</strong> subscription has been canceled immediately.</p>
                <p>Your access to premium features has ended. We're sorry to see you go!</p>
                {% else %}
                <p>Your <strong>{{ plan_tier }}</strong> subscription has been scheduled for cancellation.</p>
                <div class="highlight">
                    <p><strong>Access until:</strong> {{ effective_date }}</p>
                    <p><strong>Days remaining:</strong> {{ days_remaining }}</p>
                </div>
                <p>You can reactivate your subscription anytime before it expires.</p>
                {% endif %}
                <p>We'd love to hear your feedback on how we can improve.</p>
            """,
            'subscription_reactivated': """
                <h2>Welcome Back! 🎉</h2>
                <p>Hi {{ username }},</p>
                <p>Great news! Your <strong>{{ plan_tier }}</strong> subscription has been reactivated.</p>
                <p>Your premium features are now available again.</p>
                <div class="highlight">
                    <p><strong>Next billing:</strong> {{ next_billing_date }}</p>
                </div>
                <p>We're glad to have you back!</p>
            """,
            'subscription_upgraded': """
                <h2>Subscription Upgraded! 🚀</h2>
                <p>Hi {{ username }},</p>
                <p>Your subscription has been upgraded from <strong>{{ old_tier }}</strong> to <strong>{{ new_tier }}</strong>!</p>
                <div class="highlight">
                    <p><strong>New plan:</strong> {{ new_tier }}</p>
                    <p><strong>New billing:</strong> ${{ amount }} {{ currency }} / {{ billing_period }}</p>
                </div>
                <p>Enjoy your new premium features!</p>
            """,
            'payment_failed': """
                <h2>Payment Failed - Action Required ⚠️</h2>
                <p>Hi {{ username }},</p>
                <p>We were unable to process your payment of <strong>${{ amount }} {{ currency }}</strong>.</p>
                <p>To continue your subscription, please update your payment method in your account settings.</p>
                <a href="#" class="button">Update Payment Method</a>
                <p>If you don't update your payment method, your subscription will be suspended.</p>
            """,
            'payment_succeeded': """
                <h2>Payment Receipt 💳</h2>
                <p>Hi {{ username }},</p>
                <p>Thank you for your payment!</p>
                <div class="highlight">
                    <p><strong>Amount:</strong> ${{ amount }} {{ currency }}</p>
                    <p><strong>Date:</strong> {{ date }}</p>
                </div>
                {% if invoice_url %}
                <a href="{{ invoice_url }}" class="button">View Invoice</a>
                {% endif %}
                <p>Thank you for being a valued AppleTrader Pro customer!</p>
            """,
        }

        # Get template content
        content_template = templates.get(template_name, "<p>{{ username }}</p>")

        # Render content with context
        content = Template(content_template).render(**context)

        # Render full template
        return Template(base_template).render(content=content)
