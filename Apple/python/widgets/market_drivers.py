"""
AppleTrader Pro - Market Drivers Widget
Shows key price-moving factors for the day, week, and overall market
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from typing import List, Dict

from config import settings
from utils.logger import logger


class MarketDriversWidget(QWidget):
    """
    Market Drivers and Economic Calendar
    Shows key factors that could move prices today/this week
    """

    def __init__(self):
        super().__init__()

        self.init_ui()

        # Update timer (refresh daily drivers every hour)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_drivers)
        self.update_timer.start(3600000)  # 1 hour

        # Initial update
        self.update_drivers()

        logger.info("Market Drivers widget initialized")

    def init_ui(self):
        """Initialize user interface"""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ============================================================
        # HEADER
        # ============================================================
        header = QLabel("📰 MARKET DRIVERS & CALENDAR")
        header.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_lg}px;
                font-weight: 700;
                padding: 8px 0;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(header)

        # Current date/time
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.datetime_label)

        # ============================================================
        # TODAY'S DRIVERS
        # ============================================================
        today_section = self.create_today_section()
        layout.addWidget(today_section)

        # ============================================================
        # THIS WEEK'S DRIVERS
        # ============================================================
        week_section = self.create_week_section()
        layout.addWidget(week_section)

        # ============================================================
        # GENERAL MARKET FACTORS
        # ============================================================
        market_section = self.create_market_factors_section()
        layout.addWidget(market_section)

        layout.addStretch()

        # Update datetime
        self.update_datetime()
        datetime_timer = QTimer()
        datetime_timer.timeout.connect(self.update_datetime)
        datetime_timer.start(1000)  # Update every second

    def create_today_section(self) -> QFrame:
        """Create today's drivers section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border-left: 4px solid {settings.theme.danger};
                border-radius: 8px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # Title
        title = QLabel("🔥 TODAY'S KEY DRIVERS")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.danger};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Event container
        self.today_events_layout = QVBoxLayout()
        self.today_events_layout.setSpacing(8)
        layout.addLayout(self.today_events_layout)

        return frame

    def create_week_section(self) -> QFrame:
        """Create this week's drivers section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border-left: 4px solid {settings.theme.warning};
                border-radius: 8px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # Title
        title = QLabel("📅 THIS WEEK'S EVENTS")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.warning};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Event container
        self.week_events_layout = QVBoxLayout()
        self.week_events_layout.setSpacing(8)
        layout.addLayout(self.week_events_layout)

        return frame

    def create_market_factors_section(self) -> QFrame:
        """Create general market factors section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border-left: 4px solid {settings.theme.info};
                border-radius: 8px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # Title
        title = QLabel("🌍 MARKET SENTIMENT")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.info};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Factors container
        self.market_factors_layout = QVBoxLayout()
        self.market_factors_layout.setSpacing(8)
        layout.addLayout(self.market_factors_layout)

        return frame

    def create_event_widget(self, time: str, event: str, impact: str, details: str = "") -> QWidget:
        """
        Create event display widget

        Args:
            time: Event time (e.g., "14:30 GMT")
            event: Event name (e.g., "US NFP")
            impact: Impact level ('high', 'medium', 'low')
            details: Additional details
        """

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Event header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Impact indicator
        impact_colors = {
            'high': settings.theme.danger,
            'medium': settings.theme.warning,
            'low': settings.theme.info,
        }
        impact_color = impact_colors.get(impact, settings.theme.text_secondary)

        impact_label = QLabel("●")
        impact_label.setStyleSheet(f"""
            QLabel {{
                color: {impact_color};
                font-size: {settings.theme.font_size_lg}px;
                background: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(impact_label)

        # Time
        time_label = QLabel(time)
        time_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
                font-family: {settings.theme.font_family_mono};
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(time_label)

        # Event name
        event_label = QLabel(event)
        event_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(event_label)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Details (if provided)
        if details:
            details_label = QLabel(details)
            details_label.setWordWrap(True)
            details_label.setStyleSheet(f"""
                QLabel {{
                    color: {settings.theme.text_disabled};
                    font-size: {settings.theme.font_size_xs}px;
                    padding-left: 28px;
                    background: transparent;
                    border: none;
                }}
            """)
            layout.addWidget(details_label)

        return widget

    def create_factor_widget(self, factor: str, description: str, sentiment: str = "neutral") -> QWidget:
        """
        Create market factor widget

        Args:
            factor: Factor name (e.g., "USD Strength")
            description: Factor description
            sentiment: 'bullish', 'bearish', or 'neutral'
        """

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Sentiment emoji
        sentiment_emojis = {
            'bullish': '📈',
            'bearish': '📉',
            'neutral': '➖',
        }
        emoji = sentiment_emojis.get(sentiment, '➖')

        sentiment_colors = {
            'bullish': settings.theme.success,
            'bearish': settings.theme.danger,
            'neutral': settings.theme.text_secondary,
        }
        color = sentiment_colors.get(sentiment, settings.theme.text_secondary)

        # Factor header
        factor_label = QLabel(f"{emoji} {factor}")
        factor_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(factor_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_disabled};
                font-size: {settings.theme.font_size_xs}px;
                padding-left: 20px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(desc_label)

        return widget

    def update_datetime(self):
        """Update current datetime display"""

        now = datetime.now()
        self.datetime_label.setText(now.strftime("%A, %B %d, %Y • %H:%M:%S GMT"))

    def update_drivers(self):
        """Update market drivers data"""

        # Clear existing events
        self.clear_layout(self.today_events_layout)
        self.clear_layout(self.week_events_layout)
        self.clear_layout(self.market_factors_layout)

        # Get current day of week
        today = datetime.now()
        day_name = today.strftime("%A")

        # ============================================================
        # TODAY'S DRIVERS (Example data - would come from API)
        # ============================================================
        today_events = self.get_todays_events()

        if today_events:
            for event in today_events:
                widget = self.create_event_widget(
                    event['time'],
                    event['event'],
                    event['impact'],
                    event.get('details', '')
                )
                self.today_events_layout.addWidget(widget)
        else:
            no_events = QLabel("No high-impact events scheduled for today")
            no_events.setStyleSheet(f"""
                QLabel {{
                    color: {settings.theme.text_secondary};
                    font-size: {settings.theme.font_size_sm}px;
                    font-style: italic;
                    background: transparent;
                    border: none;
                }}
            """)
            self.today_events_layout.addWidget(no_events)

        # ============================================================
        # THIS WEEK'S DRIVERS
        # ============================================================
        week_events = self.get_weeks_events()

        for event in week_events:
            widget = self.create_event_widget(
                event['time'],
                event['event'],
                event['impact'],
                event.get('details', '')
            )
            self.week_events_layout.addWidget(widget)

        # ============================================================
        # GENERAL MARKET FACTORS
        # ============================================================
        market_factors = self.get_market_factors()

        for factor in market_factors:
            widget = self.create_factor_widget(
                factor['factor'],
                factor['description'],
                factor.get('sentiment', 'neutral')
            )
            self.market_factors_layout.addWidget(widget)

    def get_todays_events(self) -> List[Dict]:
        """
        Get today's economic events
        In production, this would fetch from an economic calendar API
        """

        # Example data structure
        # In production: fetch from ForexFactory, Investing.com API, etc.

        today = datetime.now()
        day_name = today.strftime("%A")

        # Example events (customize based on actual calendar)
        sample_events = {
            'Monday': [
                {
                    'time': '14:00 GMT',
                    'event': 'US ISM Manufacturing PMI',
                    'impact': 'high',
                    'details': 'Manufacturing sector health indicator'
                }
            ],
            'Tuesday': [
                {
                    'time': '10:00 GMT',
                    'event': 'Eurozone CPI Flash Estimate',
                    'impact': 'high',
                    'details': 'Inflation data - ECB policy driver'
                }
            ],
            'Wednesday': [
                {
                    'time': '13:30 GMT',
                    'event': 'US ADP Employment Change',
                    'impact': 'medium',
                    'details': 'Private sector employment preview'
                },
                {
                    'time': '19:00 GMT',
                    'event': 'FOMC Meeting Minutes',
                    'impact': 'high',
                    'details': 'Insights into Fed policy thinking'
                }
            ],
            'Thursday': [
                {
                    'time': '13:30 GMT',
                    'event': 'US Initial Jobless Claims',
                    'impact': 'medium',
                    'details': 'Weekly unemployment indicator'
                }
            ],
            'Friday': [
                {
                    'time': '13:30 GMT',
                    'event': 'US Non-Farm Payrolls (NFP)',
                    'impact': 'high',
                    'details': 'Most important monthly jobs report - major volatility expected!'
                },
                {
                    'time': '13:30 GMT',
                    'event': 'US Unemployment Rate',
                    'impact': 'high',
                    'details': 'Released with NFP - watch for divergences'
                }
            ],
        }

        return sample_events.get(day_name, [])

    def get_weeks_events(self) -> List[Dict]:
        """Get this week's upcoming events"""

        # Example weekly events
        return [
            {
                'time': 'Mon 14:00',
                'event': 'US ISM Manufacturing',
                'impact': 'high',
            },
            {
                'time': 'Wed 19:00',
                'event': 'FOMC Minutes',
                'impact': 'high',
            },
            {
                'time': 'Fri 13:30',
                'event': 'US NFP & Unemployment',
                'impact': 'high',
            },
        ]

    def get_market_factors(self) -> List[Dict]:
        """Get general market factors and sentiment"""

        # Example factors (would be updated from news/analysis APIs)
        return [
            {
                'factor': 'USD Strength',
                'description': 'Dollar gaining on hawkish Fed expectations and safe-haven demand',
                'sentiment': 'bullish',
            },
            {
                'factor': 'Risk Sentiment',
                'description': 'Markets cautious ahead of NFP - reduced risk appetite',
                'sentiment': 'bearish',
            },
            {
                'factor': 'Oil Prices',
                'description': 'Crude rallying on OPEC+ production cuts - supports CAD',
                'sentiment': 'bullish',
            },
            {
                'factor': 'Central Bank Policy',
                'description': 'ECB dovish signals vs Fed hawkish stance - EUR weakness expected',
                'sentiment': 'bearish',
            },
            {
                'factor': 'Geopolitical Tensions',
                'description': 'Elevated uncertainty driving safe-haven flows to USD, JPY, CHF',
                'sentiment': 'neutral',
            },
        ]

    def clear_layout(self, layout):
        """Clear all widgets from layout"""

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
