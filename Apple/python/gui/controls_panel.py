"""
AppleTrader Pro - Controls Panel
All EA settings, filters, risk management, and trading controls
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QSlider, QFrame, QGroupBox, QComboBox, QSpinBox,
    QDoubleSpinBox, QScrollArea, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from config import settings, UpdateSpeed, UPDATE_SPEED_CONFIGS
from utils.logger import logger


class ControlsPanel(QWidget):
    """
    Trading controls panel with all EA settings
    Features:
    - Trading mode toggle
    - Update speed selector
    - Filter controls
    - Risk management
    - Quick order buttons
    - ML settings
    - Visual toggles
    """

    # Signals
    setting_changed = pyqtSignal(str, object)  # (setting_name, value)
    order_requested = pyqtSignal(str)  # 'BUY' or 'SELL'

    def __init__(self):
        super().__init__()

        self.init_ui()

        logger.info("Controls panel initialized")

    def init_ui(self):
        """Initialize user interface"""

        # Main scroll area for all controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {settings.theme.background};
                border: none;
            }}
        """)

        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # ============================================================
        # HEADER
        # ============================================================
        header = QLabel("⚙️ CONTROLS")
        header.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_xl}px;
                font-weight: 700;
                padding: 8px 0;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(header)

        # ============================================================
        # TRADING MODE (Big Toggle)
        # ============================================================
        mode_section = self.create_trading_mode_section()
        layout.addWidget(mode_section)

        # ============================================================
        # UPDATE SPEED SELECTOR
        # ============================================================
        speed_section = self.create_update_speed_section()
        layout.addWidget(speed_section)

        # ============================================================
        # QUICK ORDER BUTTONS
        # ============================================================
        orders_section = self.create_quick_orders_section()
        layout.addWidget(orders_section)

        # ============================================================
        # RISK MANAGEMENT
        # ============================================================
        risk_section = self.create_risk_section()
        layout.addWidget(risk_section)

        # ============================================================
        # INSTITUTIONAL FILTERS
        # ============================================================
        filters_section = self.create_filters_section()
        layout.addWidget(filters_section)

        # ============================================================
        # SMART MONEY CONCEPTS
        # ============================================================
        smc_section = self.create_smc_section()
        layout.addWidget(smc_section)

        # ============================================================
        # MACHINE LEARNING
        # ============================================================
        ml_section = self.create_ml_section()
        layout.addWidget(ml_section)

        # ============================================================
        # VISUAL CONTROLS
        # ============================================================
        visual_section = self.create_visual_section()
        layout.addWidget(visual_section)

        layout.addStretch()

        scroll.setWidget(container)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def create_trading_mode_section(self) -> QFrame:
        """Create trading mode toggle section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 2px solid {settings.theme.accent};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Title
        title = QLabel("TRADING MODE")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_lg}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Toggle button (big and obvious)
        self.mode_button = QPushButton("🔴 INDICATOR MODE")
        self.mode_button.setCheckable(True)
        self.mode_button.setChecked(False)
        self.mode_button.clicked.connect(self.toggle_trading_mode)
        self.mode_button.setFixedHeight(60)
        self.mode_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.theme.warning};
                color: {settings.theme.background};
                border: none;
                border-radius: 10px;
                font-size: {settings.theme.font_size_xl}px;
                font-weight: 700;
            }}
            QPushButton:checked {{
                background-color: {settings.theme.success};
            }}
            QPushButton:hover {{
            }}
        """)
        layout.addWidget(self.mode_button)

        return frame

    def create_update_speed_section(self) -> QFrame:
        """Create update speed selector"""

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

        # Title
        title = QLabel("⚡ Update Speed")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Speed selector
        self.speed_combo = QComboBox()
        for speed in UpdateSpeed:
            if speed != UpdateSpeed.CUSTOM:
                config = UPDATE_SPEED_CONFIGS[speed]
                self.speed_combo.addItem(config['description'], speed)

        # Set current speed
        current_index = list(UpdateSpeed).index(settings.app.update_speed_preset)
        if current_index < self.speed_combo.count():
            self.speed_combo.setCurrentIndex(current_index)

        self.speed_combo.currentIndexChanged.connect(self.on_speed_changed)
        self.speed_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 6px;
                padding: 10px;
                font-size: {settings.theme.font_size_sm}px;
            }}
            QComboBox:hover {{
                border-color: {settings.theme.accent};
            }}
            QComboBox QAbstractItemView {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                selection-background-color: {settings.theme.accent};
                border: 1px solid {settings.theme.border_color};
            }}
        """)
        layout.addWidget(self.speed_combo)

        return frame

    def create_quick_orders_section(self) -> QFrame:
        """Create GUERILLA TRADER section"""

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {settings.theme.surface};
                border: 2px solid {settings.theme.warning};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        # Title with toggle
        header_layout = QHBoxLayout()

        title = QLabel("⚡ GUERILLA TRADER")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.warning};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Proxy mode toggle
        self.proxy_mode_checkbox = QCheckBox("Proxy Mode")
        self.proxy_mode_checkbox.setChecked(True)
        self.proxy_mode_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {settings.theme.success};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                spacing: 4px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {settings.theme.success};
                border-radius: 3px;
                background-color: {settings.theme.surface_light};
            }}
            QCheckBox::indicator:checked {{
                background-color: {settings.theme.success};
            }}
        """)
        header_layout.addWidget(self.proxy_mode_checkbox)

        layout.addLayout(header_layout)

        # Symbol selector
        symbol_layout = QHBoxLayout()
        symbol_label = QLabel("Symbol:")
        symbol_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        symbol_layout.addWidget(symbol_label)

        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF", "EURGBP", "EURJPY", "GBPJPY"])
        self.symbol_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        symbol_layout.addWidget(self.symbol_combo)

        layout.addLayout(symbol_layout)

        # Lot size input
        lot_layout = QHBoxLayout()
        lot_label = QLabel("Lot Size:")
        lot_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        lot_layout.addWidget(lot_label)

        self.lot_size_spin = QDoubleSpinBox()
        self.lot_size_spin.setRange(0.01, 10.0)
        self.lot_size_spin.setSingleStep(0.01)
        self.lot_size_spin.setValue(0.10)
        self.lot_size_spin.setDecimals(2)
        self.lot_size_spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 4px;
                padding: 4px;
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        lot_layout.addWidget(self.lot_size_spin)

        layout.addLayout(lot_layout)

        # SL Pips input
        sl_layout = QHBoxLayout()
        sl_label = QLabel("SL Pips:")
        sl_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        sl_layout.addWidget(sl_label)

        self.sl_pips_spin = QSpinBox()
        self.sl_pips_spin.setRange(1, 500)
        self.sl_pips_spin.setValue(5)  # Tight default!
        self.sl_pips_spin.setSuffix(" pips")
        self.sl_pips_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {settings.theme.danger};
                color: {settings.theme.background};
                border: 1px solid {settings.theme.danger};
                border-radius: 4px;
                padding: 4px;
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
            }}
        """)
        sl_layout.addWidget(self.sl_pips_spin)

        layout.addLayout(sl_layout)

        # TP Pips input
        tp_layout = QHBoxLayout()
        tp_label = QLabel("TP Pips:")
        tp_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        tp_layout.addWidget(tp_label)

        self.tp_pips_spin = QSpinBox()
        self.tp_pips_spin.setRange(1, 1000)
        self.tp_pips_spin.setValue(10)
        self.tp_pips_spin.setSuffix(" pips")
        self.tp_pips_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {settings.theme.success};
                color: {settings.theme.background};
                border: 1px solid {settings.theme.success};
                border-radius: 4px;
                padding: 4px;
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
            }}
        """)
        tp_layout.addWidget(self.tp_pips_spin)

        layout.addLayout(tp_layout)

        # Order type selector
        order_type_layout = QHBoxLayout()
        order_type_label = QLabel("Order Type:")
        order_type_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        order_type_layout.addWidget(order_type_label)

        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["MARKET", "BUY STOP", "SELL STOP", "BUY LIMIT", "SELL LIMIT"])
        self.order_type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        order_type_layout.addWidget(self.order_type_combo)

        layout.addLayout(order_type_layout)

        # Entry price (for pending orders) - SIMPLE TEXT BOX!
        entry_layout = QHBoxLayout()
        entry_label = QLabel("Entry Price:")
        entry_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_sm}px;
            }}
        """)
        entry_layout.addWidget(entry_label)

        self.entry_price_input = QLineEdit()
        self.entry_price_input.setText("1.08500")
        self.entry_price_input.setPlaceholderText("e.g. 1.08500")
        self.entry_price_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {settings.theme.surface_light};
                color: {settings.theme.text_primary};
                border: 1px solid {settings.theme.border_color};
                border-radius: 4px;
                padding: 6px;
                font-size: {settings.theme.font_size_sm}px;
                font-family: 'Courier New', monospace;
            }}
            QLineEdit:disabled {{
                background-color: {settings.theme.surface_dark};
                color: {settings.theme.text_secondary};
            }}
        """)
        self.entry_price_input.setEnabled(False)  # Disabled for MARKET orders
        entry_layout.addWidget(self.entry_price_input)

        layout.addLayout(entry_layout)

        # Enable/disable entry price based on order type
        self.order_type_combo.currentTextChanged.connect(self.on_order_type_changed)

        # Instant execution checkbox (NO CONFIRMATION!)
        self.instant_exec_checkbox = QCheckBox("⚡ Instant Execution (No Confirmation)")
        self.instant_exec_checkbox.setChecked(True)  # Default: INSTANT!
        self.instant_exec_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {settings.theme.warning};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                spacing: 4px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {settings.theme.warning};
                border-radius: 3px;
                background-color: {settings.theme.surface_light};
            }}
            QCheckBox::indicator:checked {{
                background-color: {settings.theme.warning};
            }}
        """)
        layout.addWidget(self.instant_exec_checkbox)

        # BUY/SELL buttons (BIG!)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # BUY button
        self.guerilla_buy_button = QPushButton("🎯 BUY")
        self.guerilla_buy_button.clicked.connect(self.fire_guerilla_buy)
        self.guerilla_buy_button.setFixedHeight(50)
        self.guerilla_buy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.theme.success};
                color: {settings.theme.background};
                border: none;
                border-radius: 8px;
                font-size: {settings.theme.font_size_lg}px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {settings.theme.bullish};
            }}
            QPushButton:pressed {{
                background-color: {settings.theme.success};
                transform: scale(0.95);
            }}
        """)
        button_layout.addWidget(self.guerilla_buy_button)

        # SELL button
        self.guerilla_sell_button = QPushButton("🎯 SELL")
        self.guerilla_sell_button.clicked.connect(self.fire_guerilla_sell)
        self.guerilla_sell_button.setFixedHeight(50)
        self.guerilla_sell_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.theme.danger};
                color: {settings.theme.background};
                border: none;
                border-radius: 8px;
                font-size: {settings.theme.font_size_lg}px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {settings.theme.bearish};
            }}
            QPushButton:pressed {{
                background-color: {settings.theme.danger};
                transform: scale(0.95);
            }}
        """)
        button_layout.addWidget(self.guerilla_sell_button)

        layout.addLayout(button_layout)

        # Info label
        info_label = QLabel("💡 Bypasses broker restrictions!")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_secondary};
                font-size: {settings.theme.font_size_xs}px;
                font-style: italic;
                padding: 4px;
                background: transparent;
                border: none;
            }}
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        return frame

    def on_order_type_changed(self, order_type: str):
        """Handle order type change"""
        # Enable entry price for pending orders
        is_pending = order_type != "MARKET"
        self.entry_price_input.setEnabled(is_pending)

        if is_pending:
            # Update entry price field color (orange = active!)
            self.entry_price_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {settings.theme.warning};
                    color: {settings.theme.background};
                    border: 2px solid {settings.theme.warning};
                    border-radius: 4px;
                    padding: 6px;
                    font-size: {settings.theme.font_size_sm}px;
                    font-weight: 600;
                    font-family: 'Courier New', monospace;
                    font-weight: 600;
                }}
            """)
        else:
            # Reset to default gray style for MARKET orders
            self.entry_price_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {settings.theme.surface_light};
                    color: {settings.theme.text_primary};
                    border: 1px solid {settings.theme.border_color};
                    border-radius: 4px;
                    padding: 6px;
                    font-size: {settings.theme.font_size_sm}px;
                    font-family: 'Courier New', monospace;
                }}
                QLineEdit:disabled {{
                    background-color: {settings.theme.surface_dark};
                    color: {settings.theme.text_secondary};
                }}
            """)

    def fire_guerilla_buy(self):
        """Fire GUERILLA BUY order"""
        symbol = self.symbol_combo.currentText()
        volume = self.lot_size_spin.value()
        sl_pips = self.sl_pips_spin.value()
        tp_pips = self.tp_pips_spin.value()
        proxy_mode = self.proxy_mode_checkbox.isChecked()
        instant_exec = self.instant_exec_checkbox.isChecked()
        order_type = self.order_type_combo.currentText()

        # Get entry price from text input (only for pending orders)
        entry_price = None
        if order_type != "MARKET":
            try:
                entry_price = float(self.entry_price_input.text())
            except ValueError:
                logger.warning(f"Invalid entry price: {self.entry_price_input.text()}")
                entry_price = 1.08500  # Default fallback

        logger.info(f"🎯 GUERILLA BUY fired: {order_type} {symbol} {volume} lots, SL: {sl_pips} pips, TP: {tp_pips} pips, Proxy: {proxy_mode}, Instant: {instant_exec}")

        # Emit signal with guerilla parameters
        self.setting_changed.emit('guerilla_order', {
            'type': 'BUY',
            'symbol': symbol,
            'volume': volume,
            'sl_pips': sl_pips,
            'tp_pips': tp_pips,
            'proxy_mode': proxy_mode,
            'instant_exec': instant_exec,
            'order_type': order_type,
            'entry_price': entry_price
        })

    def fire_guerilla_sell(self):
        """Fire GUERILLA SELL order"""
        symbol = self.symbol_combo.currentText()
        volume = self.lot_size_spin.value()
        sl_pips = self.sl_pips_spin.value()
        tp_pips = self.tp_pips_spin.value()
        proxy_mode = self.proxy_mode_checkbox.isChecked()
        instant_exec = self.instant_exec_checkbox.isChecked()
        order_type = self.order_type_combo.currentText()

        # Get entry price from text input (only for pending orders)
        entry_price = None
        if order_type != "MARKET":
            try:
                entry_price = float(self.entry_price_input.text())
            except ValueError:
                logger.warning(f"Invalid entry price: {self.entry_price_input.text()}")
                entry_price = 1.08500  # Default fallback

        logger.info(f"🎯 GUERILLA SELL fired: {order_type} {symbol} {volume} lots, SL: {sl_pips} pips, TP: {tp_pips} pips, Proxy: {proxy_mode}, Instant: {instant_exec}")

        # Emit signal with guerilla parameters
        self.setting_changed.emit('guerilla_order', {
            'type': 'SELL',
            'symbol': symbol,
            'volume': volume,
            'sl_pips': sl_pips,
            'tp_pips': tp_pips,
            'proxy_mode': proxy_mode,
            'instant_exec': instant_exec,
            'order_type': order_type,
            'entry_price': entry_price
        })

    def create_risk_section(self) -> QFrame:
        """Create risk management section"""

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

        # Title
        title = QLabel("💰 Risk Management")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Risk per trade slider
        risk_layout = QVBoxLayout()
        risk_layout.setSpacing(6)

        self.risk_label = QLabel(f"Risk per Trade: {settings.trading.default_risk_percent}%")
        self.risk_label.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_sm}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        risk_layout.addWidget(self.risk_label)

        self.risk_slider = QSlider(Qt.Orientation.Horizontal)
        self.risk_slider.setRange(10, 200)  # 0.1% to 2.0% (stored as int * 10)
        self.risk_slider.setValue(int(settings.trading.default_risk_percent * 10))
        self.risk_slider.valueChanged.connect(self.on_risk_changed)
        self.risk_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {settings.theme.surface_light};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {settings.theme.accent};
                border: 3px solid {settings.theme.background};
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {settings.theme.success};
            }}
            QSlider::sub-page:horizontal {{
                background: {settings.theme.accent};
                border-radius: 4px;
            }}
        """)
        risk_layout.addWidget(self.risk_slider)

        layout.addLayout(risk_layout)

        return frame

    def create_filters_section(self) -> QFrame:
        """Create institutional filters section"""

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

        # Title
        title = QLabel("🔍 Institutional Filters")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Filter checkboxes
        filters = [
            ('volume', 'Volume Filter', settings.trading.use_volume_filter),
            ('spread', 'Spread Filter', settings.trading.use_spread_filter),
            ('mtf', 'Multi-Timeframe Confirmation', settings.trading.use_mtf_confirmation),
            ('session', 'Session Filter', settings.trading.use_session_filter),
            ('news', 'News Filter', settings.trading.use_news_filter),
        ]

        self.filter_checkboxes = {}

        for key, label, default in filters:
            checkbox = self.create_styled_checkbox(label, default)
            checkbox.stateChanged.connect(
                lambda state, k=key: self.setting_changed.emit(f'use_{k}_filter', state == Qt.CheckState.Checked.value)
            )
            self.filter_checkboxes[key] = checkbox
            layout.addWidget(checkbox)

        return frame

    def create_smc_section(self) -> QFrame:
        """Create Smart Money Concepts section"""

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

        # Title
        title = QLabel("💎 Smart Money Concepts")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # SMC checkboxes
        smc_features = [
            ('liquidity', 'Liquidity Sweep', True),
            ('order_blocks', 'Order Blocks', True),
            ('fvg', 'Fair Value Gaps', True),
            ('market_structure', 'Market Structure', True),
        ]

        self.smc_checkboxes = {}

        for key, label, default in smc_features:
            checkbox = self.create_styled_checkbox(label, default)
            checkbox.stateChanged.connect(
                lambda state, k=key: self.setting_changed.emit(f'use_{k}', state == Qt.CheckState.Checked.value)
            )
            self.smc_checkboxes[key] = checkbox
            layout.addWidget(checkbox)

        return frame

    def create_ml_section(self) -> QFrame:
        """Create Machine Learning section"""

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

        # Title
        title = QLabel("🤖 Machine Learning")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # ML enable checkbox
        self.ml_enable_checkbox = self.create_styled_checkbox("Enable ML Filter", settings.trading.use_ml_filter)
        self.ml_enable_checkbox.stateChanged.connect(
            lambda state: self.setting_changed.emit('use_ml_filter', state == Qt.CheckState.Checked.value)
        )
        layout.addWidget(self.ml_enable_checkbox)

        return frame

    def create_visual_section(self) -> QFrame:
        """Create visual controls section"""

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

        # Title
        title = QLabel("👁️ Chart Visuals")
        title.setStyleSheet(f"""
            QLabel {{
                color: {settings.theme.accent};
                font-size: {settings.theme.font_size_md}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(title)

        # Visual checkboxes
        visuals = [
            ('patterns', 'Pattern Boxes', True),
            ('zones', 'FVG/OB Zones', True),
            ('liquidity', 'Liquidity Levels', True),
            ('indicators', 'Indicators', True),
        ]

        self.visual_checkboxes = {}

        for key, label, default in visuals:
            checkbox = self.create_styled_checkbox(label, default)
            checkbox.stateChanged.connect(
                lambda state, k=key: self.setting_changed.emit(f'show_{k}', state == Qt.CheckState.Checked.value)
            )
            self.visual_checkboxes[key] = checkbox
            layout.addWidget(checkbox)

        return frame

    def create_styled_checkbox(self, text: str, checked: bool = False) -> QCheckBox:
        """Create styled checkbox"""

        checkbox = QCheckBox(text)
        checkbox.setChecked(checked)
        checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {settings.theme.text_primary};
                font-size: {settings.theme.font_size_sm}px;
                spacing: 8px;
                background: transparent;
                border: none;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {settings.theme.border_color_light};
                border-radius: 4px;
                background-color: {settings.theme.surface_light};
            }}
            QCheckBox::indicator:checked {{
                background-color: {settings.theme.success};
                border-color: {settings.theme.success};
                image: none;
            }}
            QCheckBox::indicator:hover {{
                border-color: {settings.theme.accent};
            }}
        """)
        return checkbox

    def toggle_trading_mode(self):
        """Toggle between indicator and trading mode"""

        is_trading = self.mode_button.isChecked()

        if is_trading:
            self.mode_button.setText("🟢 AUTO TRADING")
            self.mode_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {settings.theme.success};
                    color: {settings.theme.background};
                    border: none;
                    border-radius: 10px;
                    font-size: {settings.theme.font_size_xl}px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                }}
            """)
            logger.info("Trading mode: AUTO TRADING enabled")
        else:
            self.mode_button.setText("🔴 INDICATOR MODE")
            self.mode_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {settings.theme.warning};
                    color: {settings.theme.background};
                    border: none;
                    border-radius: 10px;
                    font-size: {settings.theme.font_size_xl}px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                }}
            """)
            logger.info("Trading mode: INDICATOR MODE (safe)")

        self.setting_changed.emit('enable_trading', is_trading)

    def on_speed_changed(self, index: int):
        """Handle update speed change"""

        speed = self.speed_combo.itemData(index)
        if speed:
            settings.app.set_update_speed(speed)
            logger.info(f"Update speed changed to: {speed.value}")
            self.setting_changed.emit('update_speed', speed)

    def on_risk_changed(self, value: int):
        """Handle risk slider change"""

        risk_percent = value / 10.0  # Convert back to percentage
        self.risk_label.setText(f"Risk per Trade: {risk_percent:.1f}%")
        settings.trading.default_risk_percent = risk_percent
        self.setting_changed.emit('risk_percent', risk_percent)
