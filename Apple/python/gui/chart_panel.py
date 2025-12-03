"""
AppleTrader Pro - Chart Panel
TradingView-inspired charting with smooth animations and modern design
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve

# Try to import WebEngine, fallback to simple widget if not available
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage
    WEBENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Warning: PyQt6-WebEngine not available: {e}")
    print("  Chart panel will use simplified view")
    WEBENGINE_AVAILABLE = False
    QWebEngineView = None
    QWebEnginePage = None

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

from config import settings, TIMEFRAMES
from core.data_manager import data_manager
from utils.logger import logger


class ChartPanel(QWidget):
    """
    Professional charting panel with TradingView-inspired design
    Features:
    - Smooth candlestick charts with Plotly
    - Real-time updates
    - Pattern overlays
    - Zone visualization
    - Interactive crosshair
    - Zoom and pan
    """

    # Signals
    timeframe_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.current_symbol = settings.app.default_symbol
        self.current_timeframe = settings.app.default_timeframe

        self.init_ui()
        self.init_chart()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_chart)
        self.update_timer.start(settings.app.chart_refresh_interval)

        logger.info("Chart panel initialized")

    def init_ui(self):
        """Initialize user interface"""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ============================================================
        # CHART TOOLBAR (Top)
        # ============================================================
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # ============================================================
        # CHART CONTAINER (Main)
        # ============================================================
        if WEBENGINE_AVAILABLE:
            self.chart_view = QWebEngineView()
            self.chart_view.setStyleSheet("""
                QWebEngineView {
                    background-color: #0A0E27;
                    border: none;
                }
            """)
        else:
            # Fallback: Simple label when WebEngine not available
            self.chart_view = QLabel("📊 Chart View (WebEngine not available)\n\n"
                                      "Market data is being received from MT5 successfully.\n"
                                      "All other panels are fully functional.\n\n"
                                      "To enable charts, install Visual C++ Redistributable:\n"
                                      "https://aka.ms/vs/17/release/vc_redist.x64.exe")
            self.chart_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.chart_view.setStyleSheet(f"""
                QLabel {{
                    background-color: {settings.theme.surface};
                    color: {settings.theme.text_secondary};
                    border: none;
                    font-size: {settings.theme.font_size_md}px;
                    padding: 40px;
                }}
            """)

        layout.addWidget(self.chart_view)

    def create_toolbar(self) -> QFrame:
        """Create chart toolbar with controls"""

        toolbar = QFrame()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border-bottom: 1px solid {settings.theme.border_color};
                border-radius: 0;
            }}
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(16, 8, 16, 8)

        # Symbol label
        symbol_label = QLabel(f"📈 {self.current_symbol}")
        symbol_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_xl}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(symbol_label)

        layout.addSpacing(20)

        # Timeframe selector
        tf_label = QLabel("Timeframe:")
        tf_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_md}px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(tf_label)

        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1'])
        self.timeframe_combo.setCurrentText(self.current_timeframe)
        self.timeframe_combo.currentTextChanged.connect(self.on_timeframe_changed)
        self.timeframe_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 80px;
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
            }}
            QComboBox:hover {{
                border-color: {settings.theme.accent};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                selection-background-color: {settings.theme.accent};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
            }}
        """)
        layout.addWidget(self.timeframe_combo)

        layout.addStretch()

        # Chart type buttons (future feature)
        # For now, just visual placeholders

        # Candlestick button (active)
        candle_btn = QPushButton("🕯️ Candles")
        candle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.theme.accent};
                color: {settings.theme.background};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(candle_btn)

        # Indicators button
        indicators_btn = QPushButton("📊 Indicators")
        indicators_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {settings.theme.text_secondary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {settings.theme.font_size_sm}px;
            }}
            QPushButton:hover {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border-color: {settings.theme.accent};
            }}
        """)
        layout.addWidget(indicators_btn)

        # Patterns button
        patterns_btn = QPushButton("🎯 Patterns")
        patterns_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {settings.theme.text_secondary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {settings.theme.font_size_sm}px;
            }}
            QPushButton:hover {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border-color: {settings.theme.accent};
            }}
        """)
        layout.addWidget(patterns_btn)

        return toolbar

    def init_chart(self):
        """Initialize empty chart"""

        if not WEBENGINE_AVAILABLE:
            return  # Skip chart initialization if WebEngine not available

        # Create initial chart with placeholder data
        fig = self.create_empty_chart()

        # Convert to HTML and display
        html = self.fig_to_html(fig)
        self.chart_view.setHtml(html)

    def create_empty_chart(self) -> go.Figure:
        """Create empty chart template"""

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('', 'Volume')
        )

        # Configure layout with TradingView-inspired theme
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor=settings.theme.background,
            plot_bgcolor=settings.theme.background,
            font=dict(
                family=settings.theme.font_family_main,
                size=settings.theme.font_size_sm,
                color=settings.theme.text_secondary
            ),
            xaxis=dict(
                gridcolor=settings.theme.chart_grid,
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                gridcolor=settings.theme.chart_grid,
                showgrid=True,
                zeroline=False,
                side='right'  # Price axis on right (TradingView style)
            ),
            margin=dict(l=10, r=10, t=40, b=40),
            hovermode='x unified',
            dragmode='pan',
        )

        return fig

    def create_chart_from_data(self, df: pd.DataFrame) -> go.Figure:
        """
        Create chart from candlestick data

        Args:
            df: DataFrame with columns: time, open, high, low, close, tick_volume
        """

        if df is None or len(df) == 0:
            return self.create_empty_chart()

        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('', 'Volume')
        )

        # ============================================================
        # CANDLESTICK CHART (Row 1)
        # ============================================================
        candlestick = go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing=dict(
                line=dict(color='#26A69A'),  # TradingView teal
                fillcolor='#26A69A'
            ),
            decreasing=dict(
                line=dict(color='#EF5350'),  # TradingView coral red
                fillcolor='#EF5350'
            ),
            hoverinfo='x+y'
        )

        fig.add_trace(candlestick, row=1, col=1)

        # ============================================================
        # VOLUME BARS (Row 2)
        # ============================================================
        colors = ['#26A69A' if close >= open else '#EF5350'
                  for open, close in zip(df['open'], df['close'])]

        volume = go.Bar(
            x=df['time'],
            y=df['tick_volume'],
            name='Volume',
            marker=dict(
                color=colors,
                opacity=0.5
            ),
            hoverinfo='x+y'
        )

        fig.add_trace(volume, row=2, col=1)

        # ============================================================
        # LAYOUT CONFIGURATION (TradingView Style)
        # ============================================================
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor=settings.theme.background,
            plot_bgcolor=settings.theme.background,
            font=dict(
                family=settings.theme.font_family_main,
                size=settings.theme.font_size_sm,
                color=settings.theme.text_secondary
            ),
            xaxis=dict(
                gridcolor=settings.theme.chart_grid,
                showgrid=True,
                zeroline=False,
                rangeslider=dict(visible=False)  # Hide range slider
            ),
            xaxis2=dict(
                gridcolor=settings.theme.chart_grid,
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                gridcolor=settings.theme.chart_grid,
                showgrid=True,
                zeroline=False,
                side='right',  # Price on right (TradingView style)
                title='Price'
            ),
            yaxis2=dict(
                gridcolor=settings.theme.chart_grid,
                showgrid=True,
                zeroline=False,
                side='right',
                title='Volume'
            ),
            margin=dict(l=10, r=80, t=40, b=40),
            hovermode='x unified',
            dragmode='pan',
            showlegend=False,
            # Smooth animations
            transition=dict(
                duration=settings.app.chart_refresh_interval,
                easing='cubic-in-out'
            )
        )

        # Configure axes
        fig.update_xaxes(rangeslider_visible=False)

        return fig

    def fig_to_html(self, fig: go.Figure) -> str:
        """Convert Plotly figure to HTML"""

        # Get HTML with configuration
        html = fig.to_html(
            include_plotlyjs='cdn',
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                'responsive': True
            }
        )

        # Add custom CSS to match theme
        custom_css = f"""
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: {settings.theme.background};
                overflow: hidden;
            }}
            .plotly-graph-div {{
                height: 100vh;
                width: 100vw;
            }}
            .modebar {{
                background-color: {settings.theme.surface} !important;
                border-radius: 6px;
            }}
            .modebar-btn {{
                color: {settings.theme.text_secondary} !important;
            }}
            .modebar-btn:hover {{
                background-color: {settings.theme.surface_hover} !important;
                color: {settings.theme.accent} !important;
            }}
        </style>
        """

        # Insert CSS before </head>
        html = html.replace('</head>', f'{custom_css}</head>')

        return html

    def update_chart(self):
        """Update chart with latest data"""

        if not WEBENGINE_AVAILABLE:
            return  # Skip chart updates if WebEngine not available

        try:
            # Get latest candles from data manager
            df = data_manager.get_candles_df(count=settings.app.chart_candles_visible)

            if df is not None and len(df) > 0:
                # Create chart from data
                fig = self.create_chart_from_data(df)

                # TODO: Add pattern overlays
                # TODO: Add zone overlays
                # TODO: Add indicator overlays

                # Convert to HTML and update view
                html = self.fig_to_html(fig)
                self.chart_view.setHtml(html)

                logger.debug(f"Chart updated with {len(df)} candles")

        except Exception as e:
            logger.exception(f"Error updating chart: {e}")

    def on_timeframe_changed(self, timeframe: str):
        """Handle timeframe change"""

        self.current_timeframe = timeframe
        logger.info(f"Timeframe changed to: {timeframe}")

        # Emit signal
        self.timeframe_changed.emit(timeframe)

        # Update chart
        self.update_chart()

    def set_symbol(self, symbol: str):
        """Change trading symbol"""

        self.current_symbol = symbol
        logger.info(f"Symbol changed to: {symbol}")

        # Update chart
        self.update_chart()

    def add_pattern_overlay(self, pattern: dict):
        """Add pattern visualization to chart (future feature)"""

        # TODO: Implement pattern boxes and labels
        pass

    def add_zone_overlay(self, zone: dict):
        """Add zone visualization to chart (future feature)"""

        # TODO: Implement FVG, OB, Liquidity zones
        pass

    def add_indicator(self, indicator_type: str, params: dict):
        """Add technical indicator to chart (future feature)"""

        # TODO: Implement MA, EMA, RSI, etc.
        pass
