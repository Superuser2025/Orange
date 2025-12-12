"""
AppleTrader Pro - Subscription Management Panel
PyQt6 UI for managing subscriptions and plan cancellation
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QMessageBox, QDialog,
    QDialogButtonBox, QTextEdit, QRadioButton, QButtonGroup, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
import requests


class CancelSubscriptionDialog(QDialog):
    """Dialog for subscription cancellation"""

    def __init__(self, subscription_data, parent=None):
        super().__init__(parent)
        self.subscription_data = subscription_data
        self.setup_ui()

    def setup_ui(self):
        """Setup cancellation dialog UI"""
        self.setWindowTitle("Cancel Subscription")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        # Warning message
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF3CD;
                border: 2px solid #FFE69C;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        warning_layout = QVBoxLayout(warning_frame)

        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("font-size: 32px;")
        warning_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        warning_title = QLabel("Are you sure you want to cancel?")
        warning_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #856404;")
        warning_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        warning_text = QLabel(
            "Canceling your subscription means you'll lose access to premium features. "
            "We'd hate to see you go!"
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet("color: #856404;")
        warning_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        warning_layout.addWidget(warning_icon)
        warning_layout.addWidget(warning_title)
        warning_layout.addWidget(warning_text)

        layout.addWidget(warning_frame)
        layout.addSpacing(20)

        # Cancellation timing
        timing_group = QGroupBox("When should we cancel?")
        timing_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #DEE2E6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        timing_layout = QVBoxLayout(timing_group)

        self.cancel_timing_group = QButtonGroup()

        # Option 1: Cancel at period end
        self.cancel_at_end_radio = QRadioButton()
        self.cancel_timing_group.addButton(self.cancel_at_end_radio, 0)
        self.cancel_at_end_radio.setChecked(True)

        end_date = self.subscription_data.get('current_period_end', 'period end')
        days_remaining = self.subscription_data.get('days_remaining', 0)

        cancel_at_end_layout = QHBoxLayout()
        cancel_at_end_text = QLabel(
            f"<b>Cancel at period end</b><br>"
            f"<span style='color: #6C757D;'>Keep access until {end_date} ({days_remaining} days remaining)</span><br>"
            f"<span style='color: #28A745;'>✓ No refund needed, use your remaining time</span>"
        )
        cancel_at_end_layout.addWidget(self.cancel_at_end_radio)
        cancel_at_end_layout.addWidget(cancel_at_end_text, 1)

        # Option 2: Cancel immediately
        self.cancel_now_radio = QRadioButton()
        self.cancel_timing_group.addButton(self.cancel_now_radio, 1)

        refund_amount = self.calculate_prorated_refund()

        cancel_now_layout = QHBoxLayout()
        cancel_now_text = QLabel(
            f"<b>Cancel immediately</b><br>"
            f"<span style='color: #6C757D;'>Lose access right away</span><br>"
            f"<span style='color: #FFC107;'>↻ Prorated refund: ${refund_amount:.2f}</span>"
        )
        cancel_now_layout.addWidget(self.cancel_now_radio)
        cancel_now_layout.addWidget(cancel_now_text, 1)

        timing_layout.addLayout(cancel_at_end_layout)
        timing_layout.addSpacing(10)
        timing_layout.addLayout(cancel_now_layout)

        layout.addWidget(timing_group)
        layout.addSpacing(20)

        # Cancellation reason
        reason_label = QLabel("Why are you canceling? (Optional)")
        reason_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(reason_label)

        self.reason_group = QButtonGroup()

        reasons = [
            ("too_expensive", "💰 Too expensive"),
            ("missing_features", "🔧 Missing features I need"),
            ("switching_service", "🔄 Switching to another service"),
            ("not_using", "📉 Not using it enough"),
            ("technical_issues", "⚙️ Technical issues"),
            ("too_complex", "🤯 Too complex to use"),
            ("customer_service", "📞 Customer service issues"),
            ("other", "📝 Other reason"),
        ]

        reasons_layout = QGridLayout()
        for idx, (value, label) in enumerate(reasons):
            radio = QRadioButton(label)
            self.reason_group.addButton(radio)
            radio.setProperty("reason_value", value)
            reasons_layout.addWidget(radio, idx // 2, idx % 2)

        layout.addLayout(reasons_layout)
        layout.addSpacing(10)

        # Feedback text
        feedback_label = QLabel("Additional feedback (Optional):")
        feedback_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(feedback_label)

        self.feedback_text = QTextEdit()
        self.feedback_text.setPlaceholderText(
            "Let us know what we could do better. Your feedback helps us improve!"
        )
        self.feedback_text.setMaximumHeight(100)
        self.feedback_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #CED4DA;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.feedback_text)

        layout.addSpacing(20)

        # Buttons
        button_box = QDialogButtonBox()
        button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Ok
        )

        cancel_btn = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn.setText("Cancel Subscription")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)

        keep_btn = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        keep_btn.setText("Keep Subscription")
        keep_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def calculate_prorated_refund(self):
        """Calculate prorated refund amount"""
        amount = self.subscription_data.get('amount', 0)
        days_remaining = self.subscription_data.get('days_remaining', 0)
        days_total = 30  # Approximate

        if 'billing_period' in self.subscription_data:
            period = self.subscription_data['billing_period']
            if period == 'quarterly':
                days_total = 90
            elif period == 'annually':
                days_total = 365

        if days_total > 0:
            return (amount / days_total) * days_remaining
        return 0.0

    def get_cancellation_data(self):
        """Get cancellation data from dialog"""
        immediate = self.cancel_timing_group.checkedId() == 1

        reason = None
        for button in self.reason_group.buttons():
            if button.isChecked():
                reason = button.property("reason_value")
                break

        feedback = self.feedback_text.toPlainText().strip()

        return {
            'immediate': immediate,
            'reason': reason,
            'feedback': feedback if feedback else None
        }


class SubscriptionPanel(QWidget):
    """Main subscription management panel"""

    subscription_updated = pyqtSignal(dict)

    def __init__(self, api_base_url="http://localhost:8000", parent=None):
        super().__init__(parent)
        self.api_base_url = api_base_url
        self.auth_token = None
        self.current_subscription = None
        self.setup_ui()

    def setup_ui(self):
        """Setup main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title = QLabel("Subscription Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setSpacing(20)

        # Current subscription card
        self.subscription_card = self.create_subscription_card()
        self.content_layout.addWidget(self.subscription_card)

        # Available plans
        self.plans_card = self.create_plans_card()
        self.content_layout.addWidget(self.plans_card)

        self.content_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Load initial data
        QTimer.singleShot(100, self.load_subscription_data)

    def create_subscription_card(self):
        """Create current subscription card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E1E8ED;
                border-radius: 12px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(card)

        # Header
        header_layout = QHBoxLayout()
        header_title = QLabel("Current Plan")
        header_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        self.status_badge = QLabel()
        self.status_badge.setStyleSheet("""
            QLabel {
                background-color: #28A745;
                color: white;
                padding: 5px 12px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        header_layout.addWidget(self.status_badge)

        layout.addLayout(header_layout)
        layout.addSpacing(15)

        # Plan info
        self.plan_name_label = QLabel("Loading...")
        self.plan_name_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #007AFF;")

        self.plan_price_label = QLabel()
        self.plan_price_label.setStyleSheet("font-size: 16px; color: #6C757D;")

        layout.addWidget(self.plan_name_label)
        layout.addWidget(self.plan_price_label)
        layout.addSpacing(15)

        # Billing info
        self.billing_info_layout = QVBoxLayout()
        layout.addLayout(self.billing_info_layout)

        layout.addSpacing(15)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self.manage_payment_btn = QPushButton("💳 Manage Payment")
        self.manage_payment_btn.setStyleSheet(self.get_button_style("#007AFF"))
        self.manage_payment_btn.clicked.connect(self.manage_payment_method)
        buttons_layout.addWidget(self.manage_payment_btn)

        self.upgrade_btn = QPushButton("⬆️ Upgrade Plan")
        self.upgrade_btn.setStyleSheet(self.get_button_style("#28A745"))
        self.upgrade_btn.clicked.connect(self.show_upgrade_options)
        buttons_layout.addWidget(self.upgrade_btn)

        self.cancel_btn = QPushButton("❌ Cancel Plan")
        self.cancel_btn.setStyleSheet(self.get_button_style("#DC3545"))
        self.cancel_btn.clicked.connect(self.cancel_subscription)
        buttons_layout.addWidget(self.cancel_btn)

        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        return card

    def create_plans_card(self):
        """Create available plans card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E1E8ED;
                border-radius: 12px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(card)

        title = QLabel("Available Plans")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)

        self.plans_layout = QGridLayout()
        self.plans_layout.setSpacing(15)
        layout.addLayout(self.plans_layout)

        return card

    def get_button_style(self, color):
        """Get button stylesheet"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
        """

    def set_auth_token(self, token):
        """Set authentication token"""
        self.auth_token = token

    def load_subscription_data(self):
        """Load current subscription data from API"""
        try:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'

            # Get current subscription
            response = requests.get(
                f"{self.api_base_url}/api/subscriptions/current",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                self.current_subscription = data.get('subscription')
                self.update_subscription_display()

            # Get available plans
            response = requests.get(f"{self.api_base_url}/api/subscriptions/plans")
            if response.status_code == 200:
                data = response.json()
                self.update_plans_display(data.get('plans', []))

        except Exception as e:
            print(f"Error loading subscription data: {e}")

    def update_subscription_display(self):
        """Update subscription display with current data"""
        if not self.current_subscription:
            self.plan_name_label.setText("No Active Plan")
            self.plan_price_label.setText("Sign up to start trading")
            self.status_badge.setText("Free")
            self.cancel_btn.setEnabled(False)
            return

        # Plan name
        tier = self.current_subscription.get('plan_tier', '').title()
        self.plan_name_label.setText(f"{tier} Plan")

        # Price
        amount = self.current_subscription.get('amount', 0)
        currency = self.current_subscription.get('currency', 'USD')
        billing_period = self.current_subscription.get('billing_period', 'monthly')
        self.plan_price_label.setText(f"${amount:.2f} {currency} / {billing_period}")

        # Status
        status = self.current_subscription.get('status', 'active')
        is_active = self.current_subscription.get('is_active', False)

        if is_active:
            self.status_badge.setText("✓ Active")
            self.status_badge.setStyleSheet("""
                QLabel {
                    background-color: #28A745;
                    color: white;
                    padding: 5px 12px;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
        else:
            self.status_badge.setText(f"⚠ {status.title()}")
            self.status_badge.setStyleSheet("""
                QLabel {
                    background-color: #FFC107;
                    color: black;
                    padding: 5px 12px;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)

        # Clear existing billing info
        while self.billing_info_layout.count():
            child = self.billing_info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Billing info
        info_items = []

        if self.current_subscription.get('is_trial'):
            trial_end = self.current_subscription.get('trial_end', '')
            info_items.append(("🎁 Trial ends:", trial_end))

        next_billing = self.current_subscription.get('next_billing_date', '')
        if next_billing:
            info_items.append(("📅 Next billing:", next_billing))

        days_remaining = self.current_subscription.get('days_remaining', 0)
        info_items.append(("⏱️ Days remaining:", str(days_remaining)))

        if self.current_subscription.get('cancel_at_period_end'):
            cancel_date = self.current_subscription.get('cancellation_effective_date', '')
            info_items.append(("🚫 Cancels on:", cancel_date))

        for label_text, value_text in info_items:
            item_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; color: #495057;")
            value = QLabel(value_text)
            value.setStyleSheet("color: #6C757D;")
            item_layout.addWidget(label)
            item_layout.addWidget(value)
            item_layout.addStretch()
            self.billing_info_layout.addLayout(item_layout)

        # Enable/disable cancel button
        can_cancel = is_active and not self.current_subscription.get('cancel_at_period_end')
        self.cancel_btn.setEnabled(can_cancel)

        # Update cancel button text if scheduled for cancellation
        if self.current_subscription.get('cancel_at_period_end'):
            self.cancel_btn.setText("↻ Reactivate Plan")
            self.cancel_btn.setStyleSheet(self.get_button_style("#28A745"))
            self.cancel_btn.clicked.disconnect()
            self.cancel_btn.clicked.connect(self.reactivate_subscription)
        else:
            self.cancel_btn.setText("❌ Cancel Plan")
            self.cancel_btn.setStyleSheet(self.get_button_style("#DC3545"))

    def update_plans_display(self, plans):
        """Update available plans display"""
        # Clear existing plans
        while self.plans_layout.count():
            child = self.plans_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for idx, plan in enumerate(plans):
            plan_card = self.create_plan_card(plan)
            row = idx // 2
            col = idx % 2
            self.plans_layout.addWidget(plan_card, row, col)

    def create_plan_card(self, plan):
        """Create individual plan card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 2px solid #DEE2E6;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(card)

        # Plan name
        pricing = plan.get('pricing', {})
        name = QLabel(pricing.get('name', ''))
        name.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(name)

        # Price
        monthly_price = pricing.get('monthly_price', 0)
        price = QLabel(f"${monthly_price:.2f}/month")
        price.setStyleSheet("font-size: 16px; color: #007AFF; font-weight: bold;")
        layout.addWidget(price)

        # Description
        desc = QLabel(pricing.get('description', ''))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6C757D; font-size: 13px;")
        layout.addWidget(desc)

        layout.addStretch()

        return card

    def cancel_subscription(self):
        """Show cancellation dialog"""
        if not self.current_subscription:
            return

        dialog = CancelSubscriptionDialog(self.current_subscription, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get cancellation data
            cancel_data = dialog.get_cancellation_data()

            # Confirm cancellation
            immediate = cancel_data['immediate']
            msg = "Are you absolutely sure you want to cancel your subscription"
            if immediate:
                msg += " immediately? You will lose access right away."
            else:
                msg += " at the end of your billing period?"

            reply = QMessageBox.question(
                self,
                "Confirm Cancellation",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.process_cancellation(cancel_data)

    def process_cancellation(self, cancel_data):
        """Process subscription cancellation"""
        try:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            headers['Content-Type'] = 'application/json'

            response = requests.post(
                f"{self.api_base_url}/api/subscriptions/cancel",
                json=cancel_data,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                QMessageBox.information(
                    self,
                    "Subscription Canceled",
                    data.get('message', 'Your subscription has been canceled.')
                )
                self.load_subscription_data()
                self.subscription_updated.emit(data.get('subscription', {}))
            else:
                QMessageBox.warning(
                    self,
                    "Cancellation Failed",
                    "Failed to cancel subscription. Please try again."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred: {str(e)}"
            )

    def reactivate_subscription(self):
        """Reactivate canceled subscription"""
        try:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'

            response = requests.post(
                f"{self.api_base_url}/api/subscriptions/reactivate",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                QMessageBox.information(
                    self,
                    "Subscription Reactivated",
                    "Your subscription has been reactivated!"
                )
                self.load_subscription_data()
                self.subscription_updated.emit(data.get('subscription', {}))
            else:
                QMessageBox.warning(
                    self,
                    "Reactivation Failed",
                    "Failed to reactivate subscription. Please try again."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred: {str(e)}"
            )

    def manage_payment_method(self):
        """Manage payment methods"""
        QMessageBox.information(
            self,
            "Payment Management",
            "Payment method management coming soon!"
        )

    def show_upgrade_options(self):
        """Show upgrade options"""
        QMessageBox.information(
            self,
            "Upgrade Plan",
            "Plan upgrade interface coming soon!"
        )
