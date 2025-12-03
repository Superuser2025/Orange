"""
AppleTrader Pro - Dashboard Panel
Elegant market status display with smooth updates
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QProgressBar, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from config import settings
from core.data_manager import data_manager
from utils.logger import logger


class DashboardPanel(QWidget):
    """
    Market status dashboard with elegant design
    Displays regime, bias, session, filters, and performance metrics
    """

    def __init__(self):
        super().__init__()

        self.init_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(settings.app.ui_refresh_interval)

        logger.info("Dashboard panel initialized")

    def init_ui(self):
        """Initialize user interface"""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # ============================================================
        # HEADER
        # ============================================================
        header = self.create_section_header("📊 MARKET STATUS", settings.theme.text_primary)
        layout.addWidget(header)

        # ============================================================
        # MARKET CONTEXT SECTION
        # ============================================================
        context_section = self.create_market_context_section()
        layout.addWidget(context_section)

        # ============================================================
        # FILTER STATUS SECTION
        # ============================================================
        filters_section = self.create_filters_section()
        layout.addWidget(filters_section)

        # ============================================================
        # ACTIVE PATTERN SECTION
        # ============================================================
        pattern_section = self.create_pattern_section()
        layout.addWidget(pattern_section)

        # ============================================================
        # PERFORMANCE SECTION
        # ============================================================
        performance_section = self.create_performance_section()
        layout.addWidget(performance_section)

        layout.addStretch()

    def create_section_header(self, text: str, color: str) -> QLabel:
        """Create section header label"""

        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {settings.theme.font_size_xl}px;
                font-weight: 700;
                padding: 8px 0;
                background: transparent;
                border: none;
            }}
        """)
        return label

    def create_subsection_header(self, text: str) -> QLabel:
        """Create subsection header"""

        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                padding: 8px 0 4px 0;
                background: transparent;
                border: none;
            }}
        """)
        return label

    def create_market_context_section(self) -> QFrame:
        """Create market context section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Subsection header
        header = self.create_subsection_header("── MARKET CONTEXT ──")
        layout.addWidget(header)

        # Regime
        self.regime_label = self.create_status_label("Regime:", "UNKNOWN", settings.theme.text_secondary)
        layout.addWidget(self.regime_label)

        # Bias
        self.bias_label = self.create_status_label("Bias:", "NEUTRAL", settings.theme.text_secondary)
        layout.addWidget(self.bias_label)

        # Session
        self.session_label = self.create_status_label("Session:", "UNKNOWN", settings.theme.text_secondary)
        layout.addWidget(self.session_label)

        # Volatility
        self.volatility_label = self.create_status_label("Volatility:", "NORMAL", settings.theme.warning)
        layout.addWidget(self.volatility_label)

        return frame

    def create_filters_section(self) -> QFrame:
        """Create filter status section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Subsection header
        header = self.create_subsection_header("── FILTER STATUS ──")
        layout.addWidget(header)

        # Filter grid
        grid = QGridLayout()
        grid.setSpacing(10)

        # Create filter indicators
        self.filter_labels = {}

        filters = [
            ('volume_ok', 'Volume'),
            ('spread_ok', 'Spread'),
            ('session_ok', 'Session'),
            ('news_ok', 'News'),
            ('mtf_ok', 'MTF'),
            ('correlation_ok', 'Correlation'),
        ]

        row = 0
        col = 0
        for key, name in filters:
            label = self.create_filter_indicator(name, False)
            self.filter_labels[key] = label
            grid.addWidget(label, row, col)

            col += 1
            if col >= 2:  # 2 columns
                col = 0
                row += 1

        layout.addLayout(grid)

        return frame

    def create_pattern_section(self) -> QFrame:
        """Create active pattern section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Subsection header
        header = self.create_subsection_header("── ACTIVE PATTERN ──")
        layout.addWidget(header)

        # Pattern name
        self.pattern_name_label = QLabel("No active pattern")
        self.pattern_name_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                padding: 8px;
                background-color: {settings.theme.surface_light};
                border-radius: 6px;
                border: none;
            }}
        """)
        layout.addWidget(self.pattern_name_label)

        # Confluence score
        confluence_layout = QVBoxLayout()
        confluence_layout.setSpacing(6)

        self.confluence_title = QLabel("Confluence: 0/0")
        self.confluence_title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
                background: transparent;
                border: none;
            }}
        """)
        confluence_layout.addWidget(self.confluence_title)

        self.confluence_bar = QProgressBar()
        self.confluence_bar.setRange(0, 100)
        self.confluence_bar.setValue(0)
        self.confluence_bar.setTextVisible(False)
        self.confluence_bar.setFixedHeight(8)
        self.confluence_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {settings.theme.surface_light};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {settings.theme.success};
                border-radius: 4px;
            }}
        """)
        confluence_layout.addWidget(self.confluence_bar)

        layout.addLayout(confluence_layout)

        return frame

    def create_performance_section(self) -> QFrame:
        """Create performance metrics section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 1px solid {settings.theme.border_color};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Subsection header
        header = self.create_subsection_header("── PERFORMANCE ──")
        layout.addWidget(header)

        # Balance
        self.balance_label = self.create_metric_label("Balance:", "$0.00", settings.theme.text_primary)
        layout.addWidget(self.balance_label)

        # Daily P/L
        self.daily_pnl_label = self.create_metric_label("Daily P/L:", "$0.00", settings.theme.text_secondary)
        layout.addWidget(self.daily_pnl_label)

        # Open positions
        self.positions_label = self.create_metric_label("Positions:", "0/0", settings.theme.accent)
        layout.addWidget(self.positions_label)

        return frame

    def create_status_label(self, title: str, value: str, color: str) -> QWidget:
        """Create status label with title and value"""

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_md}px;
                background: transparent;
                border: none;
            }}
        """)

        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        return widget

    def create_filter_indicator(self, name: str, active: bool) -> QLabel:
        """Create filter status indicator"""

        status = "✓" if active else "✗"
        color = settings.theme.success if active else settings.theme.danger

        label = QLabel(f"{status} {name}")
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 500;
                padding: 6px 10px;
                background-color: {settings.theme.surface_light};
                border-radius: 6px;
                border: 1px solid {color};
            }}
        """)

        return label

    def create_metric_label(self, title: str, value: str, color: str) -> QWidget:
        """Create performance metric label"""

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_md}px;
                background: transparent;
                border: none;
            }}
        """)

        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                font-family: {settings.theme.font_family_mono};
                background: transparent;
                border: none;
            }}
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        return widget

    def update_dashboard(self):
        """Update dashboard with latest data"""

        try:
            # Get market state
            market_state = data_manager.get_market_state()

            # Update regime
            regime = market_state.get('regime', 'UNKNOWN')
            regime_color = self.get_regime_color(regime)
            self.update_label_value(self.regime_label, regime, regime_color)

            # Update bias
            bias = market_state.get('bias', 'NEUTRAL')
            bias_color = self.get_bias_color(bias)
            self.update_label_value(self.bias_label, bias, bias_color)

            # Update session
            session = market_state.get('session', 'UNKNOWN')
            self.update_label_value(self.session_label, session, settings.theme.text_primary)

            # Update volatility
            volatility = market_state.get('volatility', 'NORMAL')
            self.update_label_value(self.volatility_label, volatility, settings.theme.warning)

            # Update filters
            for key, label in self.filter_labels.items():
                active = market_state.get(key, False)
                self.update_filter_indicator(label, key.replace('_ok', '').upper(), active)

            # Update pattern (EA sends pattern as string like "NONE", "DOUBLE_TOP", etc.)
            pattern = market_state.get('pattern')
            if pattern and isinstance(pattern, str) and pattern != "NONE":
                self.pattern_name_label.setText(pattern)
                self.pattern_name_label.setStyleSheet(f"""
                    QLabel {{
                        color: {settings.theme.accent};
                        font-size: {settings.theme.font_size_md}px;
                        font-weight: 600;
                        padding: 8px;
                        background-color: {settings.theme.surface_light};
                        border-radius: 6px;
                        border: 1px solid {settings.theme.accent};
                    }}
                """)
            else:
                self.pattern_name_label.setText("No active pattern")
                self.pattern_name_label.setStyleSheet(f"""
                    QLabel {{
                        color: {settings.theme.text_secondary};
                        font-size: {settings.theme.font_size_md}px;
                        font-weight: 600;
                        padding: 8px;
                        background-color: {settings.theme.surface_light};
                        border-radius: 6px;
                        border: none;
                    }}
                """)

            # Update confluence
            decision = market_state.get('decision', {})
            confluence = decision.get('confluence', 0)
            required = decision.get('required', 0)

            if required > 0:
                percentage = int((confluence / required) * 100)
                self.confluence_bar.setValue(percentage)
                self.confluence_title.setText(f"Confluence: {confluence}/{required}")
            else:
                self.confluence_bar.setValue(0)
                self.confluence_title.setText("Confluence: 0/0")

            # Update performance
            account = data_manager.get_account_summary()
            self.update_label_value(
                self.balance_label,
                f"${account.get('balance', 0):.2f}",
                settings.theme.text_primary
            )

            daily_pnl = account.get('daily_pnl', 0)
            pnl_color = settings.theme.success if daily_pnl >= 0 else settings.theme.danger
            self.update_label_value(
                self.daily_pnl_label,
                f"${daily_pnl:+.2f}",
                pnl_color
            )

            positions_count = len(data_manager.get_positions())
            self.update_label_value(
                self.positions_label,
                f"{positions_count}/999",
                settings.theme.accent
            )

        except Exception as e:
            logger.exception(f"Error updating dashboard: {e}")

    def get_regime_color(self, regime: str) -> str:
        """Get color for regime"""

        regime_colors = {
            'TRENDING': settings.theme.success,
            'RANGING': settings.theme.warning,
            'CHOPPY': settings.theme.danger,
        }
        return regime_colors.get(regime, settings.theme.text_secondary)

    def get_bias_color(self, bias: str) -> str:
        """Get color for bias"""

        bias_colors = {
            'BULLISH': settings.theme.success,
            'BEARISH': settings.theme.danger,
            'NEUTRAL': settings.theme.text_secondary,
        }
        return bias_colors.get(bias, settings.theme.text_secondary)

    def update_label_value(self, widget: QWidget, value, color: str):
        """Update label value and color"""

        # Convert value to string if it's not already
        if not isinstance(value, str):
            if isinstance(value, float):
                value = f"{value:.4f}"
            else:
                value = str(value)

        value_label = widget.findChild(QLabel, "value")
        if value_label:
            value_label.setText(value)
            value_label.setStyleSheet(value_label.styleSheet().replace(
                value_label.styleSheet().split('color: ')[1].split(';')[0],
                color
            ))

    def update_filter_indicator(self, label: QLabel, name: str, active: bool):
        """Update filter indicator status"""

        status = "✓" if active else "✗"
        color = settings.theme.success if active else settings.theme.danger

        label.setText(f"{status} {name}")
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 500;
                padding: 6px 10px;
                background-color: {settings.theme.surface_light};
                border-radius: 6px;
                border: 1px solid {color};
            }}
        """)
