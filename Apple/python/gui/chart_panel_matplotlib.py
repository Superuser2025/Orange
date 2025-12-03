"""
AppleTrader Pro - Matplotlib Chart Panel
Professional candlestick charts without WebEngine dependencies
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from datetime import datetime
import MetaTrader5 as mt5

from config import settings, TIMEFRAMES
from core.data_manager import data_manager
from utils.logger import logger


class MplCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas for embedding in PyQt"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Create figure with dark theme
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#0A0E27')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#0A0E27')
        super().__init__(self.fig)


class ChartPanel(QWidget):
    """
    Professional matplotlib-based charting panel
    No WebEngine dependencies - works on all systems
    """

    # Signals
    timeframe_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.current_symbol = settings.app.default_symbol
        self.current_timeframe = settings.app.default_timeframe

        # Sample data for demonstration
        self.candle_data = []

        # Loading flag to prevent updates during data reload
        self.is_loading = False

        # MT5 connection status
        self.mt5_initialized = False
        self.init_mt5_connection()

        self.init_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_chart)
        self.update_timer.start(settings.app.chart_refresh_interval)

    def init_ui(self):
        """Initialize UI components"""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # Chart canvas
        self.canvas = MplCanvas(self, width=10, height=6, dpi=100)
        layout.addWidget(self.canvas)

        # Initialize chart
        self.init_chart()

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

        # Symbol selector (allow user to view any symbol)
        symbol_label_text = QLabel("Symbol:")
        symbol_label_text.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_md}px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(symbol_label_text)

        # Symbol dropdown
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(['GBPUSD', 'EURUSD', 'USDJPY', 'AUDUSD', 'USDCAD',
                                     'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY'])
        self.symbol_combo.setCurrentText(self.current_symbol)
        self.symbol_combo.currentTextChanged.connect(self.on_symbol_changed)
        self.symbol_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 100px;
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
            }}
            QComboBox:hover {{
                border-color: {settings.theme.accent};
            }}
            QComboBox QAbstractItemView {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                selection-background-color: {settings.theme.accent};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
            }}
        """)
        layout.addWidget(self.symbol_combo)

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

        # Status label
        self.status_label = QLabel("Chart Ready")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.success};
                font-size: {settings.theme.font_size_sm}px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(self.status_label)

        return toolbar

    def init_mt5_connection(self):
        """Initialize connection to MetaTrader5"""
        try:
            if not mt5.initialize():
                logger.error("MT5 initialize() failed")
                self.mt5_initialized = False
                return

            self.mt5_initialized = True
            logger.info(f"✓ MT5 connection established: {mt5.terminal_info()}")

        except Exception as e:
            logger.error(f"Failed to initialize MT5: {e}")
            self.mt5_initialized = False

    def get_mt5_timeframe(self, timeframe_str: str):
        """Convert timeframe string to MT5 constant"""
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
        }
        return timeframe_map.get(timeframe_str, mt5.TIMEFRAME_M5)

    def load_historical_data(self, symbol: str = None, timeframe: str = None, count: int = 100):
        """Load historical candles from MT5"""
        if not self.mt5_initialized:
            logger.warning("MT5 not initialized, cannot load historical data")
            return False

        try:
            # Try to get symbol from data_manager (what EA is actually trading)
            if symbol is None:
                price_data = data_manager.get_latest_price()
                symbol = price_data.get('symbol', self.current_symbol)
                # Update current_symbol to match what EA is trading
                if symbol and symbol != self.current_symbol:
                    self.current_symbol = symbol
                    # Also update the dropdown to match EA's symbol
                    self.symbol_combo.setCurrentText(symbol)
                    logger.info(f"Symbol updated to match EA: {symbol}")

            timeframe = timeframe or self.current_timeframe
            mt5_timeframe = self.get_mt5_timeframe(timeframe)

            # Get historical rates from MT5
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)

            if rates is None or len(rates) == 0:
                logger.warning(f"No historical data received from MT5 for {symbol} {timeframe}")
                return False

            # Convert to our candle format
            self.candle_data = []
            for i, rate in enumerate(rates):
                candle = {
                    'time': i,
                    'open': rate['open'],
                    'high': rate['high'],
                    'low': rate['low'],
                    'close': rate['close'],
                    'timestamp': rate['time']
                }
                self.candle_data.append(candle)

            logger.info(f"✓ Loaded {len(self.candle_data)} historical candles for {symbol} {timeframe}")
            return True

        except Exception as e:
            logger.exception(f"Error loading historical data: {e}")
            return False

    def init_chart(self):
        """Initialize chart with historical and live MT5 data"""

        # First, try to load historical data from MT5
        if self.mt5_initialized:
            success = self.load_historical_data()
            if success:
                logger.info(f"Chart initialized with {len(self.candle_data)} historical candles")
            else:
                # Fallback to live data if historical load fails
                logger.info("Historical data load failed, using live data only")
                self.candle_data = []
                self.get_live_mt5_data()
        else:
            # MT5 not available, use live data from JSON
            logger.info("MT5 not initialized, using live data from JSON")
            self.candle_data = []
            self.get_live_mt5_data()

        self.plot_candlesticks()

    def get_live_mt5_data(self):
        """Get live price from MT5 data manager"""

        try:
            # Get current price from data manager
            price_data = data_manager.get_latest_price()

            bid = price_data.get('bid', 1.32000)
            ask = price_data.get('ask', 1.32020)
            mid_price = (bid + ask) / 2

            # Create a simple candle from current price
            if len(self.candle_data) == 0:
                # First candle - use current price
                new_candle = {
                    'time': 0,
                    'open': mid_price,
                    'high': ask,
                    'low': bid,
                    'close': mid_price
                }
            else:
                # Add new candle
                new_candle = {
                    'time': len(self.candle_data),
                    'open': self.candle_data[-1]['close'],
                    'high': ask,
                    'low': bid,
                    'close': mid_price
                }

            self.candle_data.append(new_candle)

            # Keep only last 50 candles
            if len(self.candle_data) > 50:
                self.candle_data.pop(0)
                # Adjust time indices
                for i, c in enumerate(self.candle_data):
                    c['time'] = i

        except Exception as e:
            logger.warning(f"Could not get MT5 data, using defaults: {e}")

    def plot_candlesticks(self):
        """Plot candlestick chart"""

        self.canvas.axes.clear()

        if not self.candle_data:
            return

        # Extract data (use indices for plotting positions)
        indices = list(range(len(self.candle_data)))
        opens = [c['open'] for c in self.candle_data]
        highs = [c['high'] for c in self.candle_data]
        lows = [c['low'] for c in self.candle_data]
        closes = [c['close'] for c in self.candle_data]
        timestamps = [c.get('timestamp', 0) for c in self.candle_data]

        # Plot candlesticks
        for i, (idx, o, h, l, c) in enumerate(zip(indices, opens, highs, lows, closes)):
            color = '#10B981' if c >= o else '#EF4444'  # Green if bullish, red if bearish

            # Draw wick
            self.canvas.axes.plot([idx, idx], [l, h], color=color, linewidth=1)

            # Draw body
            body_height = abs(c - o)
            body_bottom = min(o, c)
            rect = Rectangle((idx - 0.3, body_bottom), 0.6, body_height,
                           facecolor=color, edgecolor=color)
            self.canvas.axes.add_patch(rect)

        # Styling
        self.canvas.axes.set_facecolor('#0A0E27')
        self.canvas.axes.grid(True, alpha=0.2, color='#1E293B')
        self.canvas.axes.set_xlabel('Time', color='#94A3B8', fontsize=10)
        self.canvas.axes.set_ylabel('Price', color='#94A3B8', fontsize=10)
        self.canvas.axes.tick_params(colors='#94A3B8', labelsize=9)

        # Set X-axis to show actual times instead of candle numbers
        if timestamps and timestamps[0] > 0:
            # Show time labels at regular intervals
            num_labels = min(8, len(indices))  # Show max 8 time labels
            step = max(1, len(indices) // num_labels)

            tick_positions = indices[::step]
            tick_labels = []

            for i in tick_positions:
                if i < len(timestamps):
                    ts = timestamps[i]
                    # Format timestamp as readable time
                    dt = datetime.fromtimestamp(ts)
                    # For intraday: show time (HH:MM)
                    # For daily: show date (MM/DD)
                    if self.current_timeframe in ['M1', 'M5', 'M15', 'M30', 'H1', 'H4']:
                        label = dt.strftime('%H:%M')
                    else:
                        label = dt.strftime('%m/%d')
                    tick_labels.append(label)

            self.canvas.axes.set_xticks(tick_positions)
            self.canvas.axes.set_xticklabels(tick_labels, rotation=0, ha='center')

        # Set title
        if self.candle_data:
            current_price = self.candle_data[-1]['close']
            self.canvas.axes.set_title(
                f'{self.current_symbol} - {self.current_timeframe} | Price: {current_price:.5f}',
                color='#F8FAFC',
                fontsize=12,
                fontweight='bold',
                pad=10
            )

        # Draw institutional overlays (FVG, OB, Liquidity)
        self.draw_chart_overlays()

        # Adjust layout with proper margins
        try:
            self.canvas.fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.08)
        except:
            pass  # Ignore layout warnings

        self.canvas.draw()

    def update_last_candle_only(self):
        """Update only the last (forming) candle with current price"""
        if not self.candle_data:
            return

        try:
            # Get current price from data_manager (EA's live data)
            price_data = data_manager.get_latest_price()
            bid = price_data.get('bid')
            ask = price_data.get('ask')

            if bid is None or ask is None:
                return

            mid_price = (bid + ask) / 2

            # Update the last candle (the forming one)
            last_candle = self.candle_data[-1]
            last_candle['close'] = mid_price
            last_candle['high'] = max(last_candle['high'], ask)
            last_candle['low'] = min(last_candle['low'], bid)

            # Note: We don't change 'open' - it stays as it was when candle started

        except Exception as e:
            logger.debug(f"Could not update last candle: {e}")

    def draw_chart_overlays(self):
        """Draw FVG/OB/Liquidity zones on chart"""
        try:
            # Get zone data from data_manager
            market_state = data_manager.get_market_state()

            # For now, draw sample zones
            # In production, this reads actual zone data from EA
            self.draw_sample_fvg()
            self.draw_sample_order_block()
            self.draw_sample_liquidity()

        except Exception as e:
            logger.debug(f"Could not draw overlays: {e}")

    def draw_sample_fvg(self):
        """Draw Fair Value Gap rectangle (sample)"""
        if not self.candle_data or len(self.candle_data) < 20:
            return

        # Sample FVG in middle of chart
        start_idx = len(self.candle_data) // 3
        end_idx = start_idx + 5
        low_price = min([c['low'] for c in self.candle_data[start_idx:end_idx]])
        high_price = max([c['high'] for c in self.candle_data[start_idx:end_idx]])

        # Draw FVG rectangle (cyan with transparency)
        rect = Rectangle(
            (start_idx, low_price),
            end_idx - start_idx,
            high_price - low_price,
            linewidth=2,
            edgecolor='#06B6D4',
            facecolor='#06B6D4',
            alpha=0.15,
            linestyle='--',
            label='FVG'
        )
        self.canvas.axes.add_patch(rect)

        # Add label
        self.canvas.axes.text(
            start_idx + 0.5,
            high_price,
            'FVG',
            fontsize=8,
            color='#06B6D4',
            weight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0A0E27', edgecolor='#06B6D4', alpha=0.8)
        )

    def draw_sample_order_block(self):
        """Draw Order Block rectangle (sample)"""
        if not self.candle_data or len(self.candle_data) < 40:
            return

        # Sample OB in latter part of chart
        start_idx = len(self.candle_data) // 2
        end_idx = start_idx + 8
        low_price = min([c['low'] for c in self.candle_data[start_idx:end_idx]])
        high_price = max([c['high'] for c in self.candle_data[start_idx:end_idx]])

        # Draw OB rectangle (yellow/orange)
        color = '#F59E0B'  # Orange for bearish OB
        rect = Rectangle(
            (start_idx, low_price),
            end_idx - start_idx,
            high_price - low_price,
            linewidth=2,
            edgecolor=color,
            facecolor=color,
            alpha=0.20,
            linestyle='-',
            label='Order Block'
        )
        self.canvas.axes.add_patch(rect)

        # Add label
        self.canvas.axes.text(
            start_idx + 1,
            low_price,
            'OB',
            fontsize=8,
            color=color,
            weight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0A0E27', edgecolor=color, alpha=0.8)
        )

    def draw_sample_liquidity(self):
        """Draw Liquidity horizontal lines (sample)"""
        if not self.candle_data or len(self.candle_data) < 10:
            return

        # Find a swing high for liquidity
        highs = [c['high'] for c in self.candle_data]
        liquidity_price = max(highs[len(highs)//3:len(highs)//2])

        # Draw liquidity line (red)
        self.canvas.axes.axhline(
            y=liquidity_price,
            color='#EF4444',
            linestyle=':',
            linewidth=2,
            alpha=0.7,
            label='Liquidity'
        )

        # Add label
        self.canvas.axes.text(
            len(self.candle_data) - 5,
            liquidity_price,
            'LIQUIDITY',
            fontsize=8,
            color='#EF4444',
            weight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0A0E27', edgecolor='#EF4444', alpha=0.8)
        )

    def update_chart(self):
        """Update chart with latest price (only updates last candle, no reload)"""

        try:
            # Skip update if we're currently loading new data (symbol/timeframe change)
            if self.is_loading:
                return

            # Update only the last candle with current price
            # DO NOT reload all 100 candles - that causes the "morphing" issue!
            self.update_last_candle_only()

            if self.candle_data:
                self.plot_candlesticks()
                self.status_label.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
                self.status_label.setStyleSheet(f"""
                    QLabel {{
                        color: {settings.theme.success};
                        font-size: {settings.theme.font_size_sm}px;
                        background: transparent;
                    }}
                """)

        except Exception as e:
            logger.exception(f"Error updating chart: {e}")
            self.status_label.setText("Update Error")
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    color: {settings.theme.danger};
                    font-size: {settings.theme.font_size_sm}px;
                    background: transparent;
                }}
            """)

    def on_timeframe_changed(self, timeframe: str):
        """Handle timeframe change"""

        # Set loading flag to prevent update_chart from interfering
        self.is_loading = True

        self.current_timeframe = timeframe
        self.timeframe_changed.emit(timeframe)

        # Reload historical data for new timeframe
        if self.mt5_initialized:
            success = self.load_historical_data(timeframe=timeframe)
            if not success:
                # Fallback to live data if historical load fails
                self.candle_data = []
                self.get_live_mt5_data()
        else:
            # MT5 not available, use live data
            self.candle_data = []
            self.get_live_mt5_data()

        self.plot_candlesticks()

        # Clear loading flag - updates can resume
        self.is_loading = False

        logger.info(f"Timeframe changed to: {timeframe}")

    def on_symbol_changed(self, symbol: str):
        """Handle symbol change - allows viewing any symbol independent of EA"""

        # Set loading flag to prevent update_chart from interfering
        self.is_loading = True

        self.current_symbol = symbol

        # Reload historical data for new symbol
        if self.mt5_initialized:
            success = self.load_historical_data(symbol=symbol)
            if not success:
                # Fallback to live data if historical load fails
                self.candle_data = []
                self.get_live_mt5_data()
        else:
            # MT5 not available, use live data
            self.candle_data = []
            self.get_live_mt5_data()

        self.plot_candlesticks()

        # Clear loading flag - updates can resume
        self.is_loading = False

        logger.info(f"Symbol changed to: {symbol}")
