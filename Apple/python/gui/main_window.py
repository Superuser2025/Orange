"""
AppleTrader Pro - Main Window
Central application window with all panels
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStatusBar, QLabel, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

from config import settings
from utils.logger import logger
from core.mt5_connector import connector
from core.data_manager import data_manager
from core.proxy_trader import proxy_trader  # GUERILLA TRADER
from core.command_manager import command_manager  # Python → EA commands

# Import panels
from gui.chart_panel_matplotlib import ChartPanel
from gui.dashboard_panel import DashboardPanel
from gui.controls_panel import ControlsPanel
from gui.commentary_panel import CommentaryPanel
from gui.ml_panel import MLPanel
from gui.orders_panel import OrdersPanel
from widgets.market_drivers import MarketDriversWidget


class MainWindow(QMainWindow):
    """
    Main application window
    Manages all panels and coordinates data updates
    """

    # Signals
    data_updated = pyqtSignal()
    connection_status_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.title = settings.app.window_title
        self.connected = False

        # Setup UI
        self.init_ui()

        # Setup timers
        self.init_timers()

        # Connect to MT5
        self.connect_to_mt5()

        # Start GUERILLA TRADER engine
        if self.connected:
            proxy_trader.start()
            logger.info("🎯 GUERILLA TRADER engine started")

        logger.info("Main window initialized")

    def init_ui(self):
        """Initialize user interface"""

        # Window properties
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, settings.app.window_width, settings.app.window_height)
        self.setMinimumSize(settings.app.window_min_width, settings.app.window_min_height)

        # Create menu bar
        self.create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout (vertical)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main splitter (horizontal)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # ============================================================
        # LEFT PANEL: Controls
        # ============================================================
        left_panel = QWidget()
        left_panel.setFixedWidth(400)  # Increased to 400px for proper button spacing
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Add controls panel
        self.controls_panel = ControlsPanel()
        self.controls_panel.setting_changed.connect(self.on_setting_changed)
        self.controls_panel.order_requested.connect(self.on_order_requested)
        left_layout.addWidget(self.controls_panel)

        main_splitter.addWidget(left_panel)

        # ============================================================
        # CENTER PANEL: Chart + Commentary
        # ============================================================
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(10, 10, 10, 10)

        # Center splitter (vertical)
        center_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top: Chart
        chart_container = QWidget()
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)

        # Add chart panel
        self.chart_panel = ChartPanel()
        self.chart_panel.timeframe_changed.connect(self.on_timeframe_changed)
        chart_layout.addWidget(self.chart_panel)

        center_splitter.addWidget(chart_container)

        # Bottom: Commentary + ML
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        # Commentary panel
        commentary_container = QWidget()
        commentary_layout = QVBoxLayout(commentary_container)
        commentary_layout.setContentsMargins(0, 0, 0, 0)

        self.commentary_panel = CommentaryPanel()
        commentary_layout.addWidget(self.commentary_panel)

        bottom_layout.addWidget(commentary_container)

        # ML panel
        ml_container = QWidget()
        ml_layout = QVBoxLayout(ml_container)
        ml_layout.setContentsMargins(0, 0, 0, 0)

        self.ml_panel = MLPanel()
        ml_layout.addWidget(self.ml_panel)

        bottom_layout.addWidget(ml_container)

        center_splitter.addWidget(bottom_panel)

        # Set initial sizes (70% chart, 30% commentary)
        center_splitter.setSizes([700, 300])

        center_layout.addWidget(center_splitter)
        main_splitter.addWidget(center_panel)

        # ============================================================
        # RIGHT PANEL: Dashboard + Orders
        # ============================================================
        right_panel = QWidget()
        right_panel.setFixedWidth(420)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)

        # Right splitter (vertical)
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top: Market Status + Market Drivers (combined in scrollable area)
        dashboard_container = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_container)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        dashboard_layout.setSpacing(10)

        # Dashboard panel
        self.dashboard_panel = DashboardPanel()
        dashboard_layout.addWidget(self.dashboard_panel)

        # Market Drivers widget
        self.market_drivers = MarketDriversWidget()
        dashboard_layout.addWidget(self.market_drivers)

        right_splitter.addWidget(dashboard_container)

        # Bottom: Orders
        orders_container = QWidget()
        orders_layout = QVBoxLayout(orders_container)
        orders_layout.setContentsMargins(0, 0, 0, 0)

        # Orders panel
        self.orders_panel = OrdersPanel()
        self.orders_panel.close_position_requested.connect(self.on_close_position)
        orders_layout.addWidget(self.orders_panel)

        right_splitter.addWidget(orders_container)

        # Set initial sizes (60% dashboard, 40% orders)
        right_splitter.setSizes([600, 400])

        right_layout.addWidget(right_splitter)
        main_splitter.addWidget(right_panel)

        # Set splitter sizes (300px left, expand center, 400px right)
        main_splitter.setStretchFactor(0, 0)  # Left fixed
        main_splitter.setStretchFactor(1, 1)  # Center expands
        main_splitter.setStretchFactor(2, 0)  # Right fixed

        # Add main splitter to layout
        main_layout.addWidget(main_splitter)

        # Create status bar
        self.create_status_bar()

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Toggle fullscreen
        fullscreen_action = QAction("&Fullscreen", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Trading menu
        trading_menu = menubar.addMenu("&Trading")

        # Connect/Disconnect
        self.connect_action = QAction("&Connect to MT5", self)
        self.connect_action.setShortcut(QKeySequence("Ctrl+K"))
        self.connect_action.triggered.connect(self.toggle_connection)
        trading_menu.addAction(self.connect_action)

        trading_menu.addSeparator()

        # Close all positions
        close_all_action = QAction("Close &All Positions", self)
        close_all_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        close_all_action.triggered.connect(self.close_all_positions)
        trading_menu.addAction(close_all_action)

        # ML menu
        ml_menu = menubar.addMenu("&ML")

        # Train model
        train_action = QAction("&Train Model", self)
        train_action.triggered.connect(self.train_ml_model)
        ml_menu.addAction(train_action)

        # Export data
        export_action = QAction("&Export Training Data", self)
        export_action.triggered.connect(self.export_ml_data)
        ml_menu.addAction(export_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Create status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Connection status
        self.connection_label = QLabel("⚫ Disconnected")
        self.connection_label.setStyleSheet("color: #EF4444; font-weight: bold;")
        self.statusBar.addPermanentWidget(self.connection_label)

        # Data status
        self.data_label = QLabel("📊 No data")
        self.statusBar.addPermanentWidget(self.data_label)

        # ML status
        self.ml_label = QLabel("🤖 ML: Off")
        self.statusBar.addPermanentWidget(self.ml_label)

        # Initial message
        self.statusBar.showMessage("Ready - Connect to MT5 to start", 5000)

    def init_timers(self):
        """Initialize update timers"""

        # Market data update timer (every 10 seconds as requested)
        self.market_data_timer = QTimer()
        self.market_data_timer.timeout.connect(self.update_market_data)
        self.market_data_timer.start(settings.app.market_data_update_interval)

        # UI refresh timer (250ms for smooth updates)
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(settings.app.ui_refresh_interval)

        logger.debug("Timers initialized")

    def connect_to_mt5(self):
        """Connect to MetaTrader 5"""
        if connector.initialize():
            self.connected = True
            self.connection_label.setText("🟢 Connected")
            self.connection_label.setStyleSheet("color: #10B981; font-weight: bold;")
            self.connect_action.setText("&Disconnect from MT5")
            self.statusBar.showMessage("✓ Connected to MT5", 3000)

            # Emit signal
            self.connection_status_changed.emit(True)

            logger.info("✓ MT5 connection established")
        else:
            self.connected = False
            self.connection_label.setText("⚫ Disconnected")
            self.connection_label.setStyleSheet("color: #EF4444; font-weight: bold;")
            self.statusBar.showMessage("Failed to connect to MT5", 5000)

            logger.error("MT5 connection failed")

    def toggle_connection(self):
        """Toggle MT5 connection"""
        if self.connected:
            connector.shutdown()
            self.connected = False
            self.connection_label.setText("⚫ Disconnected")
            self.connection_label.setStyleSheet("color: #EF4444; font-weight: bold;")
            self.connect_action.setText("&Connect to MT5")
            self.statusBar.showMessage("Disconnected from MT5", 3000)
            self.connection_status_changed.emit(False)
        else:
            self.connect_to_mt5()

    def update_market_data(self):
        """Update market data from MT5 (called every 10 seconds)"""
        if not self.connected:
            return

        try:
            # Try to read from IPC file first (sent by EA)
            market_data = connector.read_market_data_file()

            if market_data:
                # Update data manager with IPC data
                data_manager.update_from_mt5_data(market_data)
                self.data_label.setText(f"📊 Data: {data_manager.last_update.strftime('%H:%M:%S')}")
                logger.debug("Market data updated from IPC file")

            else:
                # Fallback: Get data directly from MT5 API
                candles = connector.get_candles(settings.trading.default_symbol,
                                               settings.trading.default_timeframe,
                                               200)
                if candles is not None:
                    data_manager.update_candles(candles,
                                               settings.trading.default_symbol,
                                               settings.trading.default_timeframe)

                # Get account info
                account = connector.get_account_info()
                if account:
                    data_manager.account.update(account)

                # Get positions
                positions = connector.get_positions()
                data_manager.positions = positions

                self.data_label.setText(f"📊 API: {len(positions)} pos")
                logger.debug("Market data updated from MT5 API")

            # Emit data updated signal
            self.data_updated.emit()

        except Exception as e:
            logger.exception(f"Error updating market data: {e}")

    def update_ui(self):
        """Update UI elements (called every 250ms)"""
        # Update ML status
        ml_status = data_manager.get_ml_status()
        if ml_status.get('enabled'):
            prob = ml_status.get('probability', 0) * 100
            self.ml_label.setText(f"🤖 ML: {prob:.0f}%")
        else:
            self.ml_label.setText("🤖 ML: Off")

    def toggle_fullscreen(self, checked):
        """Toggle fullscreen mode"""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def show_settings(self):
        """Show settings dialog"""
        logger.info("Settings dialog (not yet implemented)")
        self.statusBar.showMessage("Settings dialog - Coming soon", 3000)

    def close_all_positions(self):
        """Close all open positions"""
        logger.info("Close all positions (not yet implemented)")
        self.statusBar.showMessage("Close all positions - Coming soon", 3000)

    def train_ml_model(self):
        """Train ML model"""
        logger.info("ML training (not yet implemented)")
        self.statusBar.showMessage("ML training - Coming soon", 3000)

    def export_ml_data(self):
        """Export ML training data"""
        logger.info("Export ML data (not yet implemented)")
        self.statusBar.showMessage("Export ML data - Coming soon", 3000)

    def show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "About AppleTrader Pro",
            f"""
            <h2>🍎 AppleTrader Pro v{settings.app.version}</h2>
            <p><b>Institutional Trading Platform for MT5</b></p>
            <p>
            A professional-grade trading dashboard that provides:<br>
            • Real-time charting with advanced overlays<br>
            • Machine Learning trade filtering<br>
            • Complete EA control from Python<br>
            • Institutional dark theme interface<br>
            </p>
            <p><i>Built with ❤️ for professional traders</i></p>
            <p>Clean charts. Clear decisions. Confident trading.</p>
            """
        )

    def on_setting_changed(self, setting_name: str, value):
        """Handle setting change from controls panel and send to EA"""
        logger.info(f"Setting changed: {setting_name} = {value}")

        # Handle GUERILLA TRADER orders (instant execution - no EA involved)
        if setting_name == 'guerilla_order':
            self.handle_guerilla_order(value)
            return

        # Update timers if update speed changed (Python app only)
        if setting_name == 'update_speed':
            self.market_data_timer.setInterval(settings.app.market_data_update_interval)
            self.ui_timer.setInterval(settings.app.ui_refresh_interval)
            self.statusBar.showMessage(f"Update speed: {settings.app.get_update_speed_description()}", 3000)
            return

        # ============================================================
        # SEND COMMANDS TO EA (Bidirectional IPC)
        # ============================================================

        # Trading Enable/Disable Toggle
        if setting_name == 'enable_trading':
            success = command_manager.set_trading_enabled(value)
            if success:
                if value:
                    self.commentary_panel.add_comment("🟢 AUTO TRADING ENABLED - EA will execute trades!", 1)
                    self.statusBar.showMessage("✓ EA: Auto trading enabled", 3000)
                else:
                    self.commentary_panel.add_comment("🔴 INDICATOR MODE - EA trading disabled", 1)
                    self.statusBar.showMessage("✓ EA: Indicator mode (no trading)", 3000)
            else:
                self.commentary_panel.add_comment("❌ Failed to send command to EA", 1)
            return

        # Risk Management Slider
        if setting_name == 'risk_percent':
            success = command_manager.set_risk_percent(value)
            if success:
                self.commentary_panel.add_comment(f"📊 Risk updated: {value:.1f}% per trade", 3)
                self.statusBar.showMessage(f"✓ EA: Risk set to {value:.1f}%", 3000)
            else:
                self.commentary_panel.add_comment("❌ Failed to update risk setting", 1)
            return

        # ============================================================
        # INSTITUTIONAL FILTERS
        # ============================================================

        if setting_name == 'use_volume_filter':
            success = command_manager.set_filter('use_volume_filter', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"📊 Volume filter {status}", 3)
                self.statusBar.showMessage(f"✓ EA: Volume filter {status}", 3000)
            return

        if setting_name == 'use_spread_filter':
            success = command_manager.set_filter('use_spread_filter', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"📏 Spread filter {status}", 3)
                self.statusBar.showMessage(f"✓ EA: Spread filter {status}", 3000)
            return

        if setting_name == 'use_mtf_filter':
            success = command_manager.set_filter('use_mtf_confirmation', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"📈 Multi-timeframe confirmation {status}", 3)
                self.statusBar.showMessage(f"✓ EA: MTF filter {status}", 3000)
            return

        if setting_name == 'use_session_filter':
            success = command_manager.set_filter('use_session_filter', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"🕐 Session filter {status}", 3)
                self.statusBar.showMessage(f"✓ EA: Session filter {status}", 3000)
            return

        if setting_name == 'use_news_filter':
            success = command_manager.set_filter('use_news_filter', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"📰 News filter {status}", 3)
                self.statusBar.showMessage(f"✓ EA: News filter {status}", 3000)
            return

        # ============================================================
        # SMC (SMART MONEY CONCEPTS)
        # ============================================================

        if setting_name == 'use_liquidity':
            success = command_manager.set_smc_feature('use_liquidity', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"💧 Liquidity sweep detection {status}", 3)
                self.statusBar.showMessage(f"✓ EA: Liquidity analysis {status}", 3000)
            return

        if setting_name == 'use_order_blocks':
            success = command_manager.set_smc_feature('use_order_blocks', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"📦 Order block detection {status}", 3)
                self.statusBar.showMessage(f"✓ EA: Order blocks {status}", 3000)
            return

        if setting_name == 'use_fvg':
            success = command_manager.set_smc_feature('use_fvg', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"📊 Fair Value Gap detection {status}", 3)
                self.statusBar.showMessage(f"✓ EA: FVG analysis {status}", 3000)
            return

        if setting_name == 'use_market_structure':
            success = command_manager.set_smc_feature('use_market_structure', value)
            if success:
                status = "enabled" if value else "disabled"
                self.commentary_panel.add_comment(f"🏗️ Market structure analysis {status}", 3)
                self.statusBar.showMessage(f"✓ EA: Market structure {status}", 3000)
            return

        # ============================================================
        # MACHINE LEARNING
        # ============================================================

        if setting_name == 'use_ml_filter':
            success = command_manager.set_ml_enabled(value)
            if success:
                if value:
                    self.commentary_panel.add_comment("🤖 ML filter ENABLED - Using AI predictions", 1)
                    self.statusBar.showMessage("✓ EA: ML filter active", 3000)
                else:
                    self.commentary_panel.add_comment("🤖 ML filter DISABLED", 3)
                    self.statusBar.showMessage("✓ EA: ML filter inactive", 3000)
            return

        # ============================================================
        # VISUAL CONTROLS (GUI only - don't send to EA)
        # ============================================================

        if setting_name.startswith('show_'):
            # These only affect chart display, no need to send to EA
            logger.info(f"Visual setting changed: {setting_name} = {value}")
            return

        # Unknown setting
        logger.warning(f"Unknown setting: {setting_name}")

    def handle_guerilla_order(self, order_params: dict):
        """
        Handle GUERILLA TRADER order execution

        Args:
            order_params: Dictionary with order parameters
        """
        from PyQt6.QtWidgets import QMessageBox

        order_type = order_params['type']  # BUY or SELL
        symbol = order_params['symbol']
        volume = order_params['volume']
        sl_pips = order_params['sl_pips']
        tp_pips = order_params['tp_pips']
        proxy_mode = order_params['proxy_mode']
        instant_exec = order_params.get('instant_exec', False)  # NEW: Instant execution flag
        mt5_order_type = order_params.get('order_type', 'MARKET')  # NEW: MARKET, BUY STOP, etc.
        entry_price = order_params.get('entry_price', None)  # NEW: For pending orders

        # Determine if this is a pending order
        is_pending = mt5_order_type != 'MARKET'

        # Confirmation dialog (SKIP if instant execution is enabled)
        if not instant_exec:
            # Build confirmation message based on order type
            if is_pending:
                order_desc = f"{mt5_order_type} @ {entry_price:.5f}"
            else:
                order_desc = "MARKET (Instant)"

            reply = QMessageBox.question(
                self,
                '🎯 GUERILLA TRADER - Confirm Order',
                f"""<h3>Fire GUERILLA {order_type} Order?</h3>
                <table>
                <tr><td><b>Symbol:</b></td><td>{symbol}</td></tr>
                <tr><td><b>Type:</b></td><td>{order_desc}</td></tr>
                <tr><td><b>Volume:</b></td><td>{volume} lots</td></tr>
                <tr><td><b>Stop Loss:</b></td><td>{sl_pips} pips (TIGHT!)</td></tr>
                <tr><td><b>Take Profit:</b></td><td>{tp_pips} pips</td></tr>
                <tr><td><b>Proxy Mode:</b></td><td>{"✓ YES (Bypass broker)" if proxy_mode else "✗ NO (Normal)"}</td></tr>
                </table>
                <br>
                <i>{'⚡ This will execute instantly with tight stops!' if proxy_mode else 'Standard broker execution'}</i>
                """,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                self.commentary_panel.add_comment(f"❌ GUERILLA {order_type} cancelled by user", 3)
                return

        # Execute via GUERILLA TRADER proxy engine
        if proxy_mode:
            # Choose execution path based on order type
            if is_pending:
                # PENDING ORDER: held locally, not sent to broker until triggered
                success, message = proxy_trader.place_pending_order(
                    symbol=symbol,
                    order_type=f"{order_type}_{mt5_order_type.split()[1]}",  # e.g., "BUY_STOP"
                    entry_price=entry_price,
                    volume=volume,
                    sl_pips=sl_pips,
                    tp_pips=tp_pips
                )

                if success:
                    self.commentary_panel.add_comment(
                        f"⚡ GUERILLA {mt5_order_type} @ {entry_price:.5f} PLACED! Waiting for trigger...", 1
                    )
                    self.statusBar.showMessage(f"✓ GUERILLA pending order: {message}", 5000)

                    # Show stats
                    stats = proxy_trader.get_statistics()
                    self.commentary_panel.add_comment(
                        f"📊 Guerilla Stats: {stats['pending_orders']} pending | {stats['active_orders']} active | {stats['total_profit']:.2f} P/L", 3
                    )
                else:
                    self.commentary_panel.add_comment(f"❌ GUERILLA pending order failed: {message}", 1)
                    if not instant_exec:  # Only show dialog if not instant mode
                        QMessageBox.critical(self, "Order Failed", f"GUERILLA pending order failed:\n{message}")
            else:
                # MARKET ORDER: execute immediately
                success, message = proxy_trader.place_market_order(
                    symbol=symbol,
                    order_type=order_type,
                    volume=volume,
                    sl_pips=sl_pips,
                    tp_pips=tp_pips
                )

                if success:
                    self.commentary_panel.add_comment(
                        f"🎯 GUERILLA {order_type} {symbol} FIRED! Virtual SL/TP active", 1
                    )
                    self.statusBar.showMessage(f"✓ GUERILLA {order_type} executed: {message}", 5000)

                    # Show stats
                    stats = proxy_trader.get_statistics()
                    self.commentary_panel.add_comment(
                        f"📊 Guerilla Stats: {stats['active_orders']} active | {stats['total_profit']:.2f} total P/L", 3
                    )
                else:
                    self.commentary_panel.add_comment(f"❌ GUERILLA order failed: {message}", 1)
                    if not instant_exec:  # Only show dialog if not instant mode
                        QMessageBox.critical(self, "Order Failed", f"GUERILLA order failed:\n{message}")
        else:
            # Standard MT5 order (no proxy)
            success, message = connector.place_order(
                symbol=symbol,
                order_type=order_type,
                volume=volume,
                sl=0,  # Calculate from pips if needed
                tp=0,
                comment="Manual"
            )

            if success:
                self.commentary_panel.add_comment(f"✓ Standard {order_type} {symbol} placed", 2)
                self.statusBar.showMessage(f"Order placed: {message}", 3000)
            else:
                self.commentary_panel.add_comment(f"❌ Order failed: {message}", 1)
                QMessageBox.critical(self, "Order Failed", f"Order failed:\n{message}")

    def on_order_requested(self, order_type: str):
        """Handle order request from controls panel"""
        from PyQt6.QtWidgets import QMessageBox

        # Confirmation dialog
        if settings.trading.require_confirmation:
            reply = QMessageBox.question(
                self,
                'Confirm Order',
                f'Place {order_type} order with {settings.trading.default_risk_percent}% risk?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                self.commentary_panel.add_comment(f"Order cancelled by user: {order_type}", 3)
                return

        # Place order via MT5 connector
        logger.info(f"Order requested: {order_type}")
        self.commentary_panel.add_comment(f"📈 Placing {order_type} order...", 2)

        # TODO: Calculate lot size, SL, TP
        # TODO: Call connector.place_order()

        self.statusBar.showMessage(f"{order_type} order requested", 3000)

    def on_close_position(self, ticket: int):
        """Handle close position request"""
        logger.info(f"Close position requested: {ticket}")
        self.commentary_panel.add_comment(f"Closing position #{ticket}...", 2)

        # TODO: Call connector.close_position(ticket)

        self.statusBar.showMessage(f"Position {ticket} close requested", 3000)

    def on_timeframe_changed(self, timeframe: str):
        """Handle timeframe change from chart panel"""
        logger.info(f"Timeframe changed to: {timeframe}")
        self.statusBar.showMessage(f"Timeframe: {timeframe}", 2000)

    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Application shutting down...")

        # Stop GUERILLA TRADER engine
        proxy_trader.stop()
        logger.info("Guerilla Trader stopped")

        # Save settings
        settings.save()

        # Disconnect MT5
        if self.connected:
            connector.shutdown()

        logger.info("Application closed")
        event.accept()
